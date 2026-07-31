# Players API

The Sleeper Players API provides a complete list of NFL players with metadata: status, team, position, injury notes, and depth chart placement.

## Quick Start

Cache daily and query locally: [Caching Strategy](./caching-strategy.md).

## API Reference

* [Get All NFL Players](./endpoint.md) - Public endpoint returning all players keyed by Sleeper player ID.

## Schema & Data Types

* [Player Object Schema](./player-schema.md) - Field definitions and types.
* [Position Abbreviations](./position-reference.md) - Standard position codes (QB, RB, WR, TE, K, DEF, IDP).
* [Status and Injury Codes](./status-reference.md) - Status and injury_status field semantics; eligibility rules.

## Operations

* [Caching and Sync Strategy](./caching-strategy.md) - Daily sync, stale data detection, 24-hour cache window.
* [Player Data Storage](./storage.md) - Database schema and queries (DEPRECATED; see [Storage](/sleeper/storage.md)).
