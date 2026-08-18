"""Upsert logic for Sleeper + news data. Called by management commands; each
function is idempotent and safe to re-run on any schedule."""

import json
import logging
from datetime import datetime, timezone

import feedparser
from django.conf import settings

from football.models import DraftPicks, Drafts, Leagues, NewsItem, Players, Transactions, Users
from football.services.sleeper_client import client

log = logging.getLogger(__name__)

FANTASY_POSITIONS = {"QB", "RB", "WR", "TE", "K", "DEF"}


def _jd(val):
    return json.dumps(val) if val is not None else None


def sync_players() -> int:
    """Refresh the player catalog. Weekly cadence."""
    raw = client.players()
    rows = [
        Players(
            player_id=pid,
            full_name=p.get("full_name") or pid,
            position=p.get("position"),
            team=p.get("team"),
            age=p.get("age"),
            status=p.get("status"),
            injury_status=p.get("injury_status"),
        )
        for pid, p in raw.items()
        if p.get("position") in FANTASY_POSITIONS
    ]
    Players.objects.bulk_create(
        rows,
        update_conflicts=True,
        unique_fields=["player_id"],
        update_fields=["full_name", "position", "team", "age", "status", "injury_status", "synced_at"],
    )
    log.info("players synced: %d", len(rows))
    return len(rows)


def sync_league(league_id: str) -> dict:
    """Full snapshot of one league: metadata, users, drafts, picks. Safe to run
    once for historical seasons or repeatedly for the current one."""
    lg = client.league(league_id)
    if not lg:
        log.warning("league %s not found", league_id)
        return {"leagues": 0}

    Leagues.objects.update_or_create(
        league_id=league_id,
        defaults={
            "name": lg["name"],
            "season": lg["season"],
            "status": lg["status"],
            "total_rosters": lg["total_rosters"],
            "draft_id": lg.get("draft_id"),
            "roster_positions": _jd(lg.get("roster_positions")),
            "scoring_settings": _jd(lg.get("scoring_settings")),
            "settings": _jd(lg.get("settings")),
            "previous_league_id": lg.get("previous_league_id"),
        },
    )

    users = [
        Users(user_id=u["user_id"], league_id=league_id, display_name=u.get("display_name", ""), avatar=u.get("avatar"))
        for u in client.league_users(league_id)
    ]
    Users.objects.bulk_create(
        users,
        update_conflicts=True,
        unique_fields=["user_id", "league_id"],
        update_fields=["display_name", "avatar"],
    )

    drafts = picks = 0
    for d in client.league_drafts(league_id):
        meta = d.get("metadata", {})
        Drafts.objects.update_or_create(
            draft_id=d["draft_id"],
            defaults={
                "league_id": league_id,
                "season": d["season"],
                "type": d["type"],
                "status": d["status"],
                "rounds": d["settings"].get("rounds", 0),
                "slots": len(d.get("slot_to_roster_id") or d.get("draft_order") or {}),
                "draft_order": _jd(d.get("draft_order")),
            },
        )
        drafts += 1
        if d["status"] != "complete":
            continue
        rows = [
            DraftPicks(
                draft_id=d["draft_id"],
                round=p["round"],
                pick=p["pick_no"],
                roster_id=p["roster_id"],
                player_id=p.get("player_id"),
                picked_by=p.get("picked_by"),
                is_keeper=1 if p.get("is_keeper") else 0,
                metadata=_jd(p.get("metadata")),
            )
            for p in client.draft_picks(d["draft_id"])
        ]
        DraftPicks.objects.bulk_create(
            rows,
            update_conflicts=True,
            unique_fields=["draft_id", "round", "pick"],
            update_fields=["roster_id", "player_id", "picked_by", "is_keeper", "metadata"],
        )
        picks += len(rows)
        log.info("draft %s: %d picks (%s)", d["draft_id"], len(rows), meta.get("scoring_type", ""))

    log.info("league %s synced: %d users, %d drafts, %d picks", league_id, len(users), drafts, picks)
    return {"leagues": 1, "users": len(users), "drafts": drafts, "picks": picks}


def sync_user_season(username: str, season: str) -> list[str]:
    """Sync every league a user belongs to for one season. Returns league IDs."""
    user = client.user(username)
    if not user:
        raise ValueError(f"Sleeper user {username!r} not found")
    ids = []
    for lg in client.user_leagues(user["user_id"], season):
        sync_league(lg["league_id"])
        ids.append(lg["league_id"])
    return ids


def sync_current() -> list[str]:
    """Sync the user's current-season leagues. Hourly cadence."""
    season = client.state()["league_season"]
    return sync_user_season(settings.SLEEPER_USERNAME, season)


def sync_transactions(league_id: str) -> int:
    """Append-only transaction log for a league, all weeks. Hourly cadence for
    active leagues (statuses like pending -> complete get updated on re-run)."""
    total = 0
    for week in range(1, 19):
        rows = [
            Transactions(
                transaction_id=t["transaction_id"],
                league_id=league_id,
                type=t["type"],
                status=t["status"],
                created_at=t["created"],
                leg=t.get("leg"),
                creator=t.get("creator"),
                waiver_bid=t.get("waiver_bid"),
                adds=_jd(t.get("adds")),
                drops=_jd(t.get("drops")),
                draft_picks=_jd(t.get("draft_picks")),
            )
            for t in client.transactions(league_id, week)
        ]
        if rows:
            Transactions.objects.bulk_create(
                rows,
                update_conflicts=True,
                unique_fields=["transaction_id"],
                update_fields=["status", "waiver_bid", "adds", "drops", "draft_picks", "synced_at"],
            )
        total += len(rows)
    log.info("league %s transactions synced: %d", league_id, total)
    return total


def sync_news() -> int:
    """Ingest RSS feeds into the news table. Url is the dedupe key.

    ponytail: player linking is naive full-name substring matching against the
    players table (~360 rows, cheap). Upgrade to a proper NER/ticker pass only
    if unmatched volume matters.
    """
    name_map = {
        p.full_name.lower(): p.player_id
        for p in Players.objects.exclude(full_name__isnull=True)
        if " " in p.full_name  # skip DEF rows whose full_name is a team code ("NE")
    }
    created = 0
    for source, feed_url in settings.NEWS_FEEDS.items():
        for entry in feedparser.parse(feed_url).entries:
            if not entry.get("link") or NewsItem.objects.filter(url=entry.link).exists():
                continue
            text = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
            player_id = next((pid for name, pid in name_map.items() if name in text), None)
            published = entry.get("published_parsed") or entry.get("updated_parsed")
            NewsItem.objects.create(
                player_id=player_id,
                source=source,
                headline=entry.get("title", "")[:500],
                body=entry.get("summary"),
                url=entry.link,
                published_at=datetime(*published[:6], tzinfo=timezone.utc) if published else None,
            )
            created += 1
        log.info("feed %s ingested", source)
    log.info("news synced: %d new items", created)
    return created
