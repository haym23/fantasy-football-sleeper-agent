# Players API

The Sleeper Players API provides a complete list of NFL players with metadata: status, team, position, injury notes, and depth chart placement.

## Endpoint

* [Get All NFL Players](./endpoint.md) - Public endpoint returning all active NFL players keyed by Sleeper player ID.

## Schema & Reference

* [Player Object Schema](./player-schema.md) - Field definitions and types for individual player entries.
* [NFL Position Abbreviations](./position-reference.md) - Standardized position codes (QB, RB, WR, TE, K, DEF, IDP).
* [Player Status and Injury Codes](./status-reference.md) - Semantics of status and injury_status fields; when to exclude players from lineups.

## Implementation

* [Caching and Sync Strategy](./caching-strategy.md) - Best practices for caching the 5MB endpoint, update frequency, and stale-data detection.
* [Player Data Storage in SQLite](./storage.md) - Schema, queries, and operations for storing and retrieving player data from local database.
