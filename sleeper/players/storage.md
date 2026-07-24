---
type: Runbook
title: Player Data Storage in SQLite
description: Schema, queries, and operations for storing and retrieving NFL player data from the local SQLite database.
tags: [storage, sqlite, database, implementation]
timestamp: 2026-01-21T00:00:00Z
---

# Player Data Storage in SQLite

Player data is cached in `data/players.db` in a `players` table, keyed by Sleeper player ID. This enables fast local queries without API calls.

## Schema

Defined in `player_storage.py`, `SCHEMA` constant:

```sql
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
```

Initialize on first use:

```bash
python player_storage.py
```

Or in code:

```python
from player_storage import init_db
init_db()
```

## Loading from cache

Import functions from `player_storage.py`. All queries return lists of dicts or a single dict, with automatic connection cleanup:

- `get_all_players()` — All players ordered by name.
- `get_players_by_position(position)` — Find all at a position (e.g., "WR").
- `get_players_by_team(team)` — Find all from a team (e.g., "KC").
- `get_player(player_id)` — Single player by ID, or None if not found.
- `get_roster_dict()` — All players as `{player_id: player_dict}` for O(1) ID lookup.
- `get_startable_players(position)` — Active players at position with no "Out" injury status.

Example in agent context:

```python
from player_storage import get_startable_players

# Get viable starters for QB
qbs = get_startable_players("QB")
```

## Updating the cache

`upsert_players(players_list)` in `player_storage.py` accepts a list of player dicts with schema keys (`player_id`, `full_name`, `position`, `team`, `age`, `status`, `injury_status`) and:
- Inserts new players or updates existing ones by ID
- Auto-stamps each with `synced_at` on insert/update
- Returns count upserted

Agent passes transformed Sleeper API response to this function.



## Check cache staleness

`get_cache_age_hours()` returns hours since last `synced_at`, or None if DB is empty. Use to decide whether to refresh from Sleeper API:

```python
from player_storage import get_cache_age_hours

age = get_cache_age_hours()
if not age or age > 24:
    # Fetch fresh from API and upsert
```

## Implementation details

- **Connection**: `get_conn()` context manager auto-commits on success, rolls back on error, closes always.
- **Initialization**: `init_db()` creates tables. Safe to call repeatedly.
- **DB path**: Defaults to `data/players.db`, override per function if needed.
- **Row factory**: All queries return dicts, not tuples.

## Demo

Run `python player_storage.py` to see all query patterns in action.

## Related

- [Caching strategy](/sleeper/players/caching-strategy.md) — When to refresh the cache.
- [Player schema](/sleeper/players/player-schema.md) — Field definitions and types.
- [Status reference](/sleeper/players/status-reference.md) — Status values and eligibility rules.
- [API endpoint](/sleeper/players/endpoint.md) — How to fetch fresh data from Sleeper.
- `player_storage.py` — Implementation (queries, upsert, schema)
