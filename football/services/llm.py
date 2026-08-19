"""LLM engine: OpenRouter via the openai client, with tool-calling over the
local DB. Tools are plain functions; the chat loop runs until the model stops
calling tools."""

import json
import logging
from datetime import datetime, timedelta, timezone

from django.conf import settings
from openai import OpenAI

from football.models import Leagues, NewsItem, Players, Transactions, Users
from football.services.sleeper_client import client as sleeper

log = logging.getLogger(__name__)

MAX_TOOL_ROUNDS = 6


# ---------- tool implementations ----------

def _player_names(ids) -> dict:
    return {p.player_id: p.full_name for p in Players.objects.filter(player_id__in=ids or [])}


def lookup_players(query: str = "", position: str = "", team: str = "", limit: int = 10):
    qs = Players.objects.all()
    if query:
        qs = qs.filter(full_name__icontains=query)
    if position:
        qs = qs.filter(position__iexact=position)
    if team:
        qs = qs.filter(team__iexact=team)
    return list(qs.values("player_id", "full_name", "position", "team", "age", "status", "injury_status")[:limit])


def get_roster(league_id: str, roster_id: int | None = None):
    """Rosters are fetched live from Sleeper — always current, nothing stored.
    ponytail: live fetch instead of a rosters table; add one if the UI needs
    rosters without an LLM round-trip."""
    owners = {u.user_id: u.display_name for u in Users.objects.filter(league_id=league_id)}
    out = []
    for r in sleeper.get(f"/league/{league_id}/rosters") or []:
        if roster_id and r["roster_id"] != roster_id:
            continue
        names = _player_names(r.get("players"))
        out.append(
            {
                "roster_id": r["roster_id"],
                "owner": owners.get(r.get("owner_id"), r.get("owner_id")),
                "players": [names.get(pid, pid) for pid in (r.get("players") or [])],
            }
        )
    return out


def get_recent_transactions(league_id: str, limit: int = 20):
    rows = list(Transactions.objects.filter(league_id=league_id).order_by("-created_at")[:limit])
    ids = {pid for t in rows for m in (t.adds, t.drops) if m for pid in json.loads(m)}
    names = _player_names(ids)
    return [
        {
            "type": t.type,
            "status": t.status,
            "date": datetime.fromtimestamp(t.created_at / 1000, tz=timezone.utc).date().isoformat(),
            "added": {names.get(k, k): v for k, v in json.loads(t.adds).items()} if t.adds else {},
            "dropped": {names.get(k, k): v for k, v in json.loads(t.drops).items()} if t.drops else {},
        }
        for t in rows
    ]


def search_news(player_name: str = "", days: int = 7):
    qs = NewsItem.objects.filter(published_at__gte=datetime.now(timezone.utc) - timedelta(days=days))
    if player_name:
        qs = qs.filter(headline__icontains=player_name)
    return [
        {**n, "published_at": n["published_at"].isoformat() if n["published_at"] else None}
        for n in qs.order_by("-published_at").values("headline", "body", "source", "published_at")[:20]
    ]


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": name,
            "description": fn.__doc__ or name,
            "parameters": {
                "type": "object",
                "properties": props,
                "required": [k for k, v in props.items() if "default" not in v],
            },
        },
    }
    for name, fn, props in [
        ("lookup_players", lookup_players, {
            "query": {"type": "string", "default": "", "description": "name substring"},
            "position": {"type": "string", "default": "", "description": "QB/RB/WR/TE/K/DEF"},
            "team": {"type": "string", "default": "", "description": "e.g. SF"},
            "limit": {"type": "integer", "default": 10},
        }),
        ("get_roster", get_roster, {
            "league_id": {"type": "string"},
            "roster_id": {"type": "integer", "description": "omit for all rosters"},
        }),
        ("get_recent_transactions", get_recent_transactions, {
            "league_id": {"type": "string"},
            "limit": {"type": "integer", "default": 20},
        }),
        ("search_news", search_news, {
            "player_name": {"type": "string", "default": ""},
            "days": {"type": "integer", "default": 7},
        }),
    ]
]

TOOL_FUNCS = {
    "lookup_players": lookup_players,
    "get_roster": get_roster,
    "get_recent_transactions": get_recent_transactions,
    "search_news": search_news,
}


# ---------- chat loop ----------

def _league_context() -> str:
    leagues = Leagues.objects.all().values("league_id", "name", "season", "status")
    lines = [f"- {l['name']} ({l['season']}, {l['status']}): league_id={l['league_id']}" for l in leagues]
    return "Known leagues:\n" + ("\n".join(lines) if lines else "none synced yet")


def chat(message: str, history: list[dict] | None = None) -> str:
    llm = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=settings.OPENROUTER_API_KEY)
    messages = [
        {
            "role": "system",
            "content": (
                "You are a fantasy football assistant for a single user's Sleeper leagues. "
                "Answer using the tools; never invent stats or rosters. Give concise, "
                "actionable advice (waiver claims, drops, trades) grounded in the data.\n\n"
                + _league_context()
            ),
        },
        *(history or []),
        {"role": "user", "content": message},
    ]
    for _ in range(MAX_TOOL_ROUNDS):
        resp = llm.chat.completions.create(model=settings.OPENROUTER_MODEL, messages=messages, tools=TOOLS)
        msg = resp.choices[0].message
        messages.append(msg)
        if not msg.tool_calls:
            return msg.content
        for call in msg.tool_calls:
            fn = TOOL_FUNCS[call.function.name]
            args = json.loads(call.function.arguments or "{}")
            log.info("tool %s(%s)", call.function.name, args)
            result = fn(**args)
            messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": json.dumps(result, default=str)}
            )
    return "I hit the tool-call limit before I could finish answering."
