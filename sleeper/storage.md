---
type: Reference
title: Sleeper Central SQLite Storage
description: Schema, query guidelines, and caching protocols for the unified SQLite database.
tags: [storage, sqlite, database, schema]
timestamp: 2026-01-21T00:00:00Z
---

# Sleeper Central SQLite Storage

To maximize performance, avoid API rate limits, and enable fast multi-table joins, the agent stores and queries all league, user, draft, pick, player, and transaction data in a local SQLite database: **`data/sleeper.db`** (managed by `sleeper/sleeper_db.py`).

## Core Agent Instruction

> **CRITICAL RULE:** Always query the local SQLite database (`data/sleeper.db`) FIRST. 
> 1. Start with an SQLite query to check if the desired player, draft, league, or transaction data already exists.
> 2. Only if the query returns nothing, or the data is found to be stale (e.g., player cache older than 24 hours), should you fall back to searching local markdown files or querying the Sleeper API.
> 3. Whenever you fetch fresh data from the API, immediately write/upsert it back to the database using `sleeper/sleeper_db.py` to keep the cache warm.

---

## Schema Overview

The database contains the following six tables and associated indexes:

```sql
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
    type        TEXT NOT NULL, -- snake vs linear
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
    pick        INTEGER NOT NULL, -- overall pick number (1-indexed)
    roster_id   INTEGER NOT NULL,
    player_id   TEXT, -- References players(player_id)
    picked_by   TEXT, -- References users(user_id)
    is_keeper   INTEGER DEFAULT 0, -- 1 for True, 0 for False
    metadata    TEXT, -- JSON Object snapshot at draft time (first_name, last_name, pos)
    PRIMARY KEY (draft_id, round, pick)
);

-- Transaction log (FA pickups, Trades, Waivers)
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id  TEXT PRIMARY KEY,
    league_id       TEXT NOT NULL,
    type            TEXT NOT NULL, -- free_agent, waiver, trade
    status          TEXT NOT NULL,
    created_at      INTEGER NOT NULL, -- Unix timestamp (ms)
    leg             INTEGER, -- Week number
    creator         TEXT, -- user_id who initiated
    waiver_bid      INTEGER, -- extracted waiver bid or FAAB transfer amount
    adds            TEXT, -- JSON Object mapping {player_id: roster_id}
    drops           TEXT, -- JSON Object mapping {player_id: roster_id}
    draft_picks     TEXT, -- JSON Array of swapped picks if trade
    synced_at       TEXT NOT NULL DEFAULT (datetime('now'))
);
```

---

## Access & Helper Utility: `sleeper/sleeper_db.py`

Initialize or execute SQL queries directly using Python or the terminal.

### 1. Terminal / Shell CLI Queries
To run arbitrary queries, query directly with the CLI wrapper:
```bash
python sleeper/sleeper_db.py "SELECT count(*) FROM draft_picks"
```

### 2. Python API
Querying via code is standard and clean:
```python
from sleeper import sleeper_db

# 1. Execute general SELECT statement (returns a list of dicts)
recent_picks = sleeper_db.query_sql(
    "SELECT * FROM draft_picks WHERE draft_id = ? ORDER BY round, pick LIMIT 10",
    ("1251597529313718272",)
)

# 2. Add or update items (automatic transactions and index updates)
sleeper_db.upsert_players([{
    "player_id": "4984",
    "full_name": "Josh Allen",
    "position": "QB",
    "team": "BUF",
    "age": 28,
    "status": "active",
    "injury_status": None
}])
```

---

## Performance Indexes

Ensure queries leverage secondary indexing on frequently filtered fields:
- `idx_players_pos_team` on `players(position, team)`
- `idx_draft_picks_player` on `draft_picks(player_id)`
- `idx_draft_picks_user` on `draft_picks(picked_by)`
- `idx_transactions_league_type` on `transactions(league_id, type)`

## Related

- [Players](/sleeper/players/index.md) — How players are modeled.
- [Drafts](/sleeper/drafts/index.md) — Analyzing drafting history.
- [Leagues](/sleeper/leagues/index.md) — Configuration and rosters.
