---
type: Schema
title: League Object Schema
description: Field definitions for the League object returned by Sleeper league endpoints.
tags: [leagues, schema, fields]
timestamp: 2026-01-21T00:00:00Z
---

# League Object Schema

The League object defines configuration and status for a fantasy football league.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `league_id` | string | No | Sleeper's internal identifier; stable across seasons if re-used. |
| `name` | string | No | League display name (e.g., `"Dynasty Chaos"`). |
| `season` | string | No | Four-digit year as string (e.g., `"2024"`). |
| `sport` | string | No | Always `"nfl"`. |
| `status` | enum | No | Lifecycle state: `pre_draft`, `drafting`, `in_season`, `complete`. |
| `season_type` | enum | No | `regular` or `playoff`. |
| `total_rosters` | int | No | Number of teams in the league (typically 8–14). |
| `draft_id` | string | Yes | Associated draft ID if the league has held a draft; null otherwise. |
| `avatar` | string | Yes | Avatar hash; null if no custom avatar. Build URL: `https://sleepercdn.com/avatars/<avatar_id>` or thumbnail: `https://sleepercdn.com/avatars/thumbs/<avatar_id>`. |
| `settings` | object | Yes | League-wide configuration; see [Settings Object](/sleeper/leagues/settings-reference.md). |
| `scoring_settings` | object | Yes | Stat-by-stat scoring multipliers; see [Scoring Settings](/sleeper/leagues/settings-reference.md#scoring-multipliers). |
| `roster_positions` | array (string) | Yes | Array of roster slot requirements; e.g., `["QB", "RB", "RB", "WR", "WR", "TE", "FLEX", "RB/WR/TE", "K", "DEF", "DEF"]`. |
| `previous_league_id` | string | Yes | League ID of the prior season if this is a continuation league (for dynasty/keeper formats). |

## Examples

### Fresh league, pre-draft

```json
{
  "league_id": "123456789012345678",
  "name": "Friends League 2024",
  "season": "2024",
  "sport": "nfl",
  "status": "pre_draft",
  "season_type": "regular",
  "total_rosters": 12,
  "draft_id": null,
  "avatar": "c8f4a9e2b1d3c5f7",
  "settings": { "...": "..." },
  "scoring_settings": { "...": "..." },
  "roster_positions": ["QB", "RB", "RB", "WR", "WR", "TE", "FLEX", "K", "DEF"],
  "previous_league_id": null
}
```

### In-season dynasty league

```json
{
  "league_id": "987654321098765432",
  "name": "Dynasty Empire",
  "season": "2024",
  "sport": "nfl",
  "status": "in_season",
  "season_type": "regular",
  "total_rosters": 10,
  "draft_id": "555555555555555555",
  "avatar": "a1b2c3d4e5f6g7h8",
  "settings": { "...": "..." },
  "scoring_settings": { "...": "..." },
  "roster_positions": ["QB", "RB", "RB", "WR", "WR", "TE", "FLEX", "RB/WR/TE", "FLEX", "K", "DEF", "DEF"],
  "previous_league_id": "111111111111111111"
}
```

### Playoff status

```json
{
  "league_id": "456789012345678901",
  "name": "Office League",
  "season": "2024",
  "status": "in_season",
  "season_type": "playoff",
  "total_rosters": 8,
  "...": "..."
}
```

## Field usage notes

- **league_id**: Use this as the primary key for caching/storage. Reused IDs in continuation leagues, so pair with season for uniqueness.
- **status**: Filters what endpoints are useful. `pre_draft` leagues have no rosters yet. `complete` leagues are read-only historical.
- **draft_id**: Always check this before calling draft endpoints; leagues can exist without drafts (e.g., best-ball, best-available mock).
- **avatar**: Optional; cache this hash rather than fetching live to avoid 404s.
- **roster_positions**: Governs lineup validation. More positions = deeper benches and more roster depth needed.
- **previous_league_id**: Chain of leagues for dynasty leagues; if non-null, lookup that league to trace history.

## Related

- [Settings reference](/sleeper/leagues/settings-reference.md) — Details on the `settings` and `scoring_settings` objects.
- [League endpoints](/sleeper/leagues/endpoint.md) — How to fetch League objects.
- [Roster schema](/sleeper/leagues/roster-schema.md) — Structure of teams within a league.

## Citations

[1] [Sleeper API Docs — Leagues](https://docs.sleeper.com/#leagues)
