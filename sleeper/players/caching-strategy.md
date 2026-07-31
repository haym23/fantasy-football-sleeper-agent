---
type: Reference
title: Players API Caching and Sync Strategy
description: Best practices for caching the 5MB players endpoint, update frequency, and stale-data detection.
tags: [performance, caching, sync, strategy]
timestamp: 2026-01-21T00:00:00Z
---

# Caching the Players Endpoint

The Sleeper Players API returns ~5MB of data on every call. Fetching it live on every operation is wasteful when local caching is feasible.

## Recommended strategy

**Daily cache at 6 AM ET**, stored as a JSON file or SQLite blob, with a timestamp. Expire after 24 hours.

### Rationale

- **6 AM ET**: After overnight wire wire news settles, before user activity peaks. Catches rookie callups, trades, injury news from overnight wires.
- **24-hour window**: Sleeper updates information 1–2 times per day; daily is sufficient precision for most lineup decisions.
- **20 minutes of staleness is acceptable** for most stat analysis (historical draft data, player tiers); for current status (injured_reserve, suspended) prefer fresh data if available.

## When to sync beyond the daily window

Trigger an immediate sync (overriding cache) when:

- User explicitly requests it.
- A known significant event occurred (trade deadline, playoff expansion, week 1 kickoff).
- Stale data is detected (e.g., a player's `injury_status` contradicts the league's active roster).

## Detecting stale data

If the cache was last updated more than 24 hours ago, flag operations that depend on current player status (lineups, free agent rankings). Do not silently use stale data; inform the user and offer a sync option.

## Storage format

We cache the entire NFL player roster directly in the unified database (**`data/sleeper.db`**) in the `players` table, which is fully queryable and integrates seamlessly with mock draft, league, and selection analysis.

Refer to **[Sleeper Central SQLite Storage](../storage.md)** for details on the SQLite tables, setup, and query examples.

## Cache invalidation

When a refresh occurs:
- Overwrite the entire cache (all 5MB), not individual players.
- Update the timestamp.
- If stored as a JSON file, replace atomically (write to temp, then move).
- If stored in SQLite, wrap in a transaction.

Partial updates are error-prone (missing newly-drafted players, stale injury data if a player heals).

## Related

- [Endpoint mechanics](/sleeper/players/endpoint.md) — caching notes at API level.
- [Player schema](/sleeper/players/player-schema.md) — what fields are included.

## Citations

[1] [Sleeper API Docs — Players](https://docs.sleeper.app/#players)
