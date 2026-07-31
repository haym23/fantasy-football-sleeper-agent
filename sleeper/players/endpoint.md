---
type: APIRef
title: Get All NFL Players
description: Public endpoint returning all active NFL players with metadata, keyed by Sleeper player ID.
resource: https://api.sleeper.app/v1/players/nfl
tags: [players, nfl, public, cacheable]
timestamp: 2026-01-21T00:00:00Z
---

# Endpoint

## URL

```
GET https://api.sleeper.app/v1/players/nfl
```

## Parameters

None. Returns all players; filtering is client-side.

## Response

Returns a JSON object where keys are Sleeper player IDs (strings) and values are [player objects](/sleeper/players/player-schema.md).

## Caching

This endpoint is **read-only and stable** — suitable for daily or less-frequent caching. Sleeper does not document a cache-control header, but in practice:

- New player data (rookie callups, position changes) appears within 24 hours of NFL news.
- Historical data never changes; once a player entry is set, its `player_id`, `nfl_id`, and core attributes are permanent.
- The ~5MB payload is worth caching locally rather than fetching live.

**Recommended:** Cache daily at a fixed time (after MLS news settles, e.g., 6am ET). Store as JSON in SQLite or local filesystem keyed by date.

## Error handling

- `200`: Success.
- `429`: Rate limited. Sleeper does not document limits, but public API is rarely rate-limited. Rare cases suggest backoff.
- `500+`: Service error. Retry after exponential backoff (e.g., 5s, 10s, 30s).

## Related

See [player schema](/sleeper/players/player-schema.md) for field definitions and [position mapping](/sleeper/players/position-reference.md) for NFL position identifiers.

## Citations

[1] [Sleeper API Docs — Players](https://docs.sleeper.app/#players)
