#!/usr/bin/env python3
"""
Sleeper Database Manager

Unified SQLite management for Sleeper NFL player data, leagues, drafts,
picks, users, and transactions.
"""

import sqlite3
import json
import sys
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

DB_PATH = Path("data/sleeper.db")

SCHEMA = """
-- NFL Player Master Catalog
CREATE TABLE IF NOT EXISTS players (
    player_id       TEXT PRIMARY KEY,
    full_name       TEXT,
    position        TEXT,
    team            TEXT,
    age             INTEGER,
    status          TEXT,
    injury_status   TEXT,
    synced_at       TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Leagues Metadata
CREATE TABLE IF NOT EXISTS leagues (
    league_id           TEXT PRIMARY KEY,
    name                TEXT NOT NULL,
    season              TEXT NOT NULL,
    status              TEXT NOT NULL,
    total_rosters       INTEGER NOT NULL,
    draft_id            TEXT,
    roster_positions    TEXT, -- JSON Array
    scoring_settings    TEXT, -- JSON Object
    settings            TEXT, -- JSON Object
    previous_league_id  TEXT,
    synced_at           TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Managers / Users lookup
CREATE TABLE IF NOT EXISTS users (
    user_id       TEXT NOT NULL,
    league_id     TEXT NOT NULL,
    display_name  TEXT NOT NULL,
    avatar        TEXT,
    PRIMARY KEY (user_id, league_id)
);

-- Draft configurations
CREATE TABLE IF NOT EXISTS drafts (
    draft_id    TEXT PRIMARY KEY,
    league_id   TEXT NOT NULL,
    season      TEXT NOT NULL,
    type        TEXT NOT NULL,
    status      TEXT NOT NULL,
    rounds      INTEGER NOT NULL,
    slots       INTEGER NOT NULL,
    draft_order TEXT, -- JSON Object
    synced_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Draft Pick results
CREATE TABLE IF NOT EXISTS draft_picks (
    draft_id    TEXT NOT NULL,
    round       INTEGER NOT NULL,
    pick        INTEGER NOT NULL,
    roster_id   INTEGER NOT NULL,
    player_id   TEXT,
    picked_by   TEXT,
    is_keeper   INTEGER DEFAULT 0,
    metadata    TEXT, -- JSON Object
    PRIMARY KEY (draft_id, round, pick)
);

-- Transaction log
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id  TEXT PRIMARY KEY,
    league_id       TEXT NOT NULL,
    type            TEXT NOT NULL,
    status          TEXT NOT NULL,
    created_at      INTEGER NOT NULL,
    leg             INTEGER,
    creator         TEXT,
    waiver_bid      INTEGER,
    adds            TEXT, -- JSON Object
    drops           TEXT, -- JSON Object
    draft_picks     TEXT, -- JSON Array
    synced_at       TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_players_pos_team ON players (position, team);
CREATE INDEX IF NOT EXISTS idx_draft_picks_player ON draft_picks (player_id);
CREATE INDEX IF NOT EXISTS idx_draft_picks_user ON draft_picks (picked_by);
CREATE INDEX IF NOT EXISTS idx_transactions_league_type ON transactions (league_id, type);
"""


@contextmanager
def get_conn(db_path: Path = DB_PATH):
    """Context-managed SQLite connection with Row factory."""
    db_path.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: Path = DB_PATH) -> None:
    """Initialize unified database schema."""
    with get_conn(db_path) as conn:
        conn.executescript(SCHEMA)


def _to_json(val: Any) -> Optional[str]:
    """Helper to convert objects or arrays to JSON strings."""
    if val is None:
        return None
    if isinstance(val, (dict, list)):
        return json.dumps(val)
    return str(val)


def upsert_players(players: List[Dict[str, Any]], db_path: Path = DB_PATH) -> int:
    """Insert or update players in database."""
    with get_conn(db_path) as conn:
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        for p in players:
            cursor.execute("""
                INSERT INTO players 
                (player_id, full_name, position, team, age, status, injury_status, synced_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(player_id) DO UPDATE SET
                    full_name = excluded.full_name,
                    position = excluded.position,
                    team = excluded.team,
                    age = excluded.age,
                    status = excluded.status,
                    injury_status = excluded.injury_status,
                    synced_at = excluded.synced_at
            """, (
                p["player_id"], p.get("full_name"), p.get("position"), p.get("team"),
                p.get("age"), p.get("status"), p.get("injury_status"), now
            ))
        return len(players)


def upsert_leagues(leagues: List[Dict[str, Any]], db_path: Path = DB_PATH) -> int:
    """Insert or update leagues in database."""
    with get_conn(db_path) as conn:
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        for l in leagues:
            cursor.execute("""
                INSERT INTO leagues 
                (league_id, name, season, status, total_rosters, draft_id, 
                 roster_positions, scoring_settings, settings, previous_league_id, synced_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(league_id) DO UPDATE SET
                    name = excluded.name,
                    season = excluded.season,
                    status = excluded.status,
                    total_rosters = excluded.total_rosters,
                    draft_id = excluded.draft_id,
                    roster_positions = excluded.roster_positions,
                    scoring_settings = excluded.scoring_settings,
                    settings = excluded.settings,
                    previous_league_id = excluded.previous_league_id,
                    synced_at = excluded.synced_at
            """, (
                l["league_id"], l["name"], l["season"], l["status"], l["total_rosters"],
                l.get("draft_id"), _to_json(l.get("roster_positions")),
                _to_json(l.get("scoring_settings")), _to_json(l.get("settings")),
                l.get("previous_league_id"), now
            ))
        return len(leagues)


def upsert_users(users: List[Dict[str, Any]], league_id: str, db_path: Path = DB_PATH) -> int:
    """Insert or update users who are members of a specific league."""
    with get_conn(db_path) as conn:
        cursor = conn.cursor()
        for u in users:
            cursor.execute("""
                INSERT INTO users (user_id, league_id, display_name, avatar)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, league_id) DO UPDATE SET
                    display_name = excluded.display_name,
                    avatar = excluded.avatar
            """, (u["user_id"], league_id, u["display_name"], u.get("avatar")))
        return len(users)


def upsert_drafts(drafts: List[Dict[str, Any]], db_path: Path = DB_PATH) -> int:
    """Insert or update drafts in database."""
    with get_conn(db_path) as conn:
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        for d in drafts:
            cursor.execute("""
                INSERT INTO drafts 
                (draft_id, league_id, season, type, status, rounds, slots, draft_order, synced_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(draft_id) DO UPDATE SET
                    league_id = excluded.league_id,
                    season = excluded.season,
                    type = excluded.type,
                    status = excluded.status,
                    rounds = excluded.rounds,
                    slots = excluded.slots,
                    draft_order = excluded.draft_order,
                    synced_at = excluded.synced_at
            """, (
                d["draft_id"], d["league_id"], d["season"], d["type"], d["status"],
                d.get("settings", {}).get("rounds", 15), d.get("settings", {}).get("slots", 12),
                _to_json(d.get("draft_order")), now
            ))
        return len(drafts)


def upsert_draft_picks(picks: List[Dict[str, Any]], db_path: Path = DB_PATH) -> int:
    """Insert or update draft picks in database."""
    with get_conn(db_path) as conn:
        cursor = conn.cursor()
        for p in picks:
            is_keeper = 1 if p.get("is_keeper") else 0
            pick = p.get("pick") if p.get("pick") is not None else p.get("pick_no")
            cursor.execute("""
                INSERT INTO draft_picks (draft_id, round, pick, roster_id, player_id, picked_by, is_keeper, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(draft_id, round, pick) DO UPDATE SET
                    roster_id = excluded.roster_id,
                    player_id = excluded.player_id,
                    picked_by = excluded.picked_by,
                    is_keeper = excluded.is_keeper,
                    metadata = excluded.metadata
            """, (
                p["draft_id"], p["round"], pick, p["roster_id"],
                p.get("player_id"), p.get("picked_by"), is_keeper,
                _to_json(p.get("metadata"))
            ))
        return len(picks)


def upsert_transactions(transactions: List[Dict[str, Any]], league_id: str, db_path: Path = DB_PATH) -> int:
    """Insert or update transactions in database."""
    with get_conn(db_path) as conn:
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        for t in transactions:
            # Extract waiver bid if present in settings. Waiver bid might be in any bid setting format.
            waiver_bid = None
            if t.get("settings") and isinstance(t["settings"], dict):
                waiver_bid = t["settings"].get("waiver_bid")
            elif t.get("type") == "trade" and t.get("waiver_budget"):
                # For trades, sum amount if transferred
                try:
                    waiver_bid = sum(x.get("amount", 0) for x in t.get("waiver_budget") if isinstance(x, dict))
                except Exception:
                    pass

            cursor.execute("""
                INSERT INTO transactions 
                (transaction_id, league_id, type, status, created_at, leg, creator, waiver_bid, adds, drops, draft_picks, synced_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(transaction_id) DO UPDATE SET
                    type = excluded.type,
                    status = excluded.status,
                    created_at = excluded.created_at,
                    leg = excluded.leg,
                    creator = excluded.creator,
                    waiver_bid = excluded.waiver_bid,
                    adds = excluded.adds,
                    drops = excluded.drops,
                    draft_picks = excluded.draft_picks,
                    synced_at = excluded.synced_at
            """, (
                t["transaction_id"], league_id, t["type"], t["status"], t["created"],
                t.get("leg"), t.get("creator"), waiver_bid,
                _to_json(t.get("adds")), _to_json(t.get("drops")), _to_json(t.get("draft_picks")),
                now
            ))
        return len(transactions)


# --- Custom Helper Queries ---

def query_sql(q: str, params: tuple = (), db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    """Execute raw SQL query and return rows as dicts."""
    with get_conn(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(q, params)
        return [dict(row) for row in cursor.fetchall()]


def get_player(player_id: str, db_path: Path = DB_PATH) -> Optional[Dict[str, Any]]:
    """Fetch single player by ID."""
    res = query_sql("SELECT * FROM players WHERE player_id = ?", (player_id,), db_path)
    return res[0] if res else None


def get_league_draft_picks(draft_id: str, db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    """Fetch all draft picks with joined player names and selector user names."""
    q = """
        SELECT dp.*, p.full_name, p.position, p.team, u.display_name
        FROM draft_picks dp
        LEFT JOIN players p ON dp.player_id = p.player_id
        LEFT JOIN users u ON dp.picked_by = u.user_id AND u.league_id = (SELECT l.league_id FROM drafts d INNER JOIN leagues l ON d.league_id = l.league_id WHERE d.draft_id = dp.draft_id)
        WHERE dp.draft_id = ?
        ORDER BY dp.round, dp.pick
    """
    return query_sql(q, (draft_id,), db_path)


def run_cli_query(query: str):
    """Auxiliary for executing user commands on CLI."""
    init_db()
    try:
        res = query_sql(query)
        if not res:
            print("No rows returned or query completed.")
            return
        # Print nicely formatted
        keys = res[0].keys()
        headers = " | ".join(keys)
        print(headers)
        print("-" * len(headers))
        for row in res[:100]:
            print(" | ".join(str(row[k]) for keys_loop in [keys] for k in keys_loop))
        if len(res) > 100:
            print(f"... ({len(res) - 100} more rows)")
    except Exception as e:
        print(f"Error executing query: {e}", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Easy execution of commands e.g. python sleeper_db.py "SELECT count(*) FROM players"
        run_cli_query(sys.argv[1])
    else:
        init_db()
        print(f"Initialized database structure at {DB_PATH}")
