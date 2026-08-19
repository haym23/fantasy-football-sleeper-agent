from ninja import NinjaAPI, Schema

from football.models import DraftPicks, Drafts, Leagues, Players, Users
from football.services import llm

api = NinjaAPI(title="Fantasy Football API")


@api.get("/players")
def players(request, query: str = "", position: str = "", team: str = "", limit: int = 50):
    return llm.lookup_players(query=query, position=position, team=team, limit=limit)


@api.get("/leagues")
def leagues(request):
    return list(Leagues.objects.all().values("league_id", "name", "season", "status", "total_rosters"))


@api.get("/leagues/{league_id}/draft")
def draft(request, league_id: str):
    drafts = list(Drafts.objects.filter(league_id=league_id).values("draft_id", "season", "status", "rounds"))
    draft_ids = [d["draft_id"] for d in drafts]
    picks = DraftPicks.objects.filter(draft_id__in=draft_ids).order_by("draft_id", "round", "pick")
    names = {p.player_id: p.full_name for p in Players.objects.filter(player_id__in=[p.player_id for p in picks])}
    owners = {u.user_id: u.display_name for u in Users.objects.filter(league_id=league_id)}
    for d in drafts:
        d["picks"] = [
            {
                "round": p.round,
                "pick": p.pick,
                "roster_id": p.roster_id,
                "player": names.get(p.player_id, p.player_id),
                "picked_by": owners.get(p.picked_by, p.picked_by),
            }
            for p in picks
            if p.draft_id == d["draft_id"]
        ]
    return drafts


@api.get("/leagues/{league_id}/transactions")
def transactions(request, league_id: str, limit: int = 50):
    return llm.get_recent_transactions(league_id, limit=limit)


@api.get("/news")
def news(request, player_name: str = "", days: int = 14):
    return llm.search_news(player_name=player_name, days=days)


class ChatIn(Schema):
    message: str
    history: list[dict] | None = None


@api.post("/chat")
def chat(request, payload: ChatIn):
    return {"answer": llm.chat(payload.message, payload.history)}
