#!/usr/bin/env python3
"""
Player Data Storage

SQLite database management for NFL player data from Sleeper API.
"""

import sqlite3
import json
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

DB_PATH = Path("data/players.db")
SCHEMA = """
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

CREATE INDEX IF NOT EXISTS idx_players_pos_team ON players (position, team);
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
    """Initialize database schema. Safe to call repeatedly."""
    with get_conn(db_path) as conn:
        conn.executescript(SCHEMA)


def upsert_players(players: List[Dict[str, Any]], db_path: Path = DB_PATH) -> int:
    """
    Insert or update players in database.
    
    Args:
        players: List of player dicts with keys: player_id, full_name, position, 
                 team, age, status, injury_status
        db_path: Path to database file
    
    Returns:
        Count of players upserted
    """
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
                p["player_id"], p["full_name"], p["position"], p["team"],
                p["age"], p["status"], p.get("injury_status"), now
            ))
        return len(players)


def get_all_players(db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    """Fetch all players ordered by name."""
    with get_conn(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM players ORDER BY full_name")
        return [dict(row) for row in cursor.fetchall()]


def get_players_by_position(position: str, db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    """Fetch all players at a given position."""
    with get_conn(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM players WHERE position = ? ORDER BY full_name",
            (position,)
        )
        return [dict(row) for row in cursor.fetchall()]


def get_players_by_team(team: str, db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    """Fetch all players from a given team."""
    with get_conn(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM players WHERE team = ? ORDER BY position, full_name",
            (team,)
        )
        return [dict(row) for row in cursor.fetchall()]


def get_player(player_id: str, db_path: Path = DB_PATH) -> Optional[Dict[str, Any]]:
    """Fetch a single player by ID."""
    with get_conn(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM players WHERE player_id = ?", (player_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_roster_dict(db_path: Path = DB_PATH) -> Dict[str, Dict[str, Any]]:
    """Fetch all players as dict keyed by player_id for O(1) lookup."""
    with get_conn(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM players")
        return {row["player_id"]: dict(row) for row in cursor.fetchall()}


def get_startable_players(
    position: str, db_path: Path = DB_PATH
) -> List[Dict[str, Any]]:
    """
    Fetch active players at position who are not out with injury.
    
    Args:
        position: QB, RB, WR, TE, K, DEF
        db_path: Path to database file
    
    Returns:
        List of eligible starters ordered by name
    """
    with get_conn(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM players 
            WHERE position = ? 
            AND status = 'active'
            AND (injury_status IS NULL OR injury_status NOT LIKE '%Out%')
            ORDER BY full_name
        """, (position,))
        return [dict(row) for row in cursor.fetchall()]


def get_cache_age_hours(db_path: Path = DB_PATH) -> Optional[float]:
    """
    Get age of cache in hours. Returns None if db is empty.
    """
    with get_conn(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(synced_at) FROM players")
        last_sync = cursor.fetchone()[0]
        if not last_sync:
            return None
        age = datetime.now() - datetime.fromisoformat(last_sync)
        return age.total_seconds() / 3600


def demo():
    """
    Demo all query patterns. Run to understand available operations.
    """
    init_db()
    print(f"Initialized {DB_PATH}\n")
    
    # Demo data
    demo_players = [
        {"player_id": "1", "full_name": "Patrick Mahomes", "position": "QB",
         "team": "KC", "age": 28, "status": "active", "injury_status": None},
        {"player_id": "2", "full_name": "Travis Kelce", "position": "TE",
         "team": "KC", "age": 34, "status": "active", "injury_status": None},
        {"player_id": "3", "full_name": "Rashee Rice", "position": "WR",
         "team": "KC", "age": 22, "status": "active", "injury_status": "Out"},
        {"player_id": "4", "full_name": "DeAndre Washington", "position": "RB",
         "team": "KC", "age": 30, "status": "active", "injury_status": None},
    ]
    
    count = upsert_players(demo_players)
    print(f"✓ Upserted {count} demo players\n")
    
    # All players
    all_players = get_all_players()
    print(f"✓ All players ({len(all_players)}):")
    for p in all_players:
        print(f"  - {p['full_name']} ({p['position']}, {p['team']})")
    print()
    
    # By position
    qbs = get_players_by_position("QB")
    print(f"✓ Quarterbacks ({len(qbs)}):")
    for p in qbs:
        print(f"  - {p['full_name']}")
    print()
    
    # By team
    kc = get_players_by_team("KC")
    print(f"✓ KC players ({len(kc)}):")
    for p in kc:
        print(f"  - {p['full_name']} ({p['position']})")
    print()
    
    # Single player
    mahomes = get_player("1")
    if mahomes:
        print(f"✓ Fetched single player: {mahomes['full_name']} (ID: {mahomes['player_id']})")
    print()
    
    # Roster dict (instant lookup)
    roster = get_roster_dict()
    print(f"✓ Roster dict ({len(roster)} players):")
    target = roster["2"]
    print(f"  - O(1) lookup: roster['2'] = {target['full_name']}")
    print()
    
    # Startable (not Out)
    startable_tes = get_startable_players("TE")
    print(f"✓ Startable TE ({len(startable_tes)}):")
    for p in startable_tes:
        print(f"  - {p['full_name']}")
    print()
    
    # Cache age
    age = get_cache_age_hours()
    if age:
        print(f"✓ Cache age: {age:.2f} hours")
    print()


if __name__ == "__main__":
    demo()
