---
type: Schema
title: Draft Object Schema
description: Field definitions for the Draft object returned by Sleeper draft endpoints.
tags: [drafts, schema, fields]
timestamp: 2026-01-21T00:00:00Z
---

# Draft Object Schema

The Draft object defines configuration, timing, and status for a fantasy football draft.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `draft_id` | string | No | Sleeper's internal draft identifier; stable across references. |
| `league_id` | string | No | Parent league ID; use to fetch league metadata. |
| `season` | string | No | Four-digit year as string (e.g., `"2024"`). |
| `type` | enum | No | Draft order style: `snake` (rounds alternate direction) or `linear` (same order each round). |
| `status` | enum | No | Lifecycle state: `pre_draft`, `in_progress`, or `complete`. |
| `start_time` | int | Yes | Unix timestamp (ms) when draft is/was scheduled to begin; null if not scheduled. |
| `avatar` | string | Yes | Avatar hash for custom draft branding; null if default. Build URL: `https://sleepercdn.com/avatars/<avatar_id>`. |
| `created` | int | No | Unix timestamp (ms) of draft creation in Sleeper. |
| `updated` | int | No | Unix timestamp (ms) of last status change. |
| `sport` | string | No | Always `"nfl"`. |
| `settings` | object | Yes | Draft configuration object; see [Draft Settings](#draft-settings). |
| `metadata` | object | Yes | Optional draft notes or custom fields; typically null or empty. |

## Draft Settings

The `settings` object in a Draft contains round and scoring format configuration:

| Field | Type | Description |
|-------|------|-------------|
| `rounds` | int | Number of rounds in draft (typically 12–15). |
| `slots` | int | Number of rosters/teams in draft (league size). |
| `position_limit` | object | Position-by-position limits, e.g., `{"QB": 3, "RB": 6}` etc. |

## Examples

### Pre-draft snake draft

```json
{
  "draft_id": "234567890123456789",
  "league_id": "123456789012345678",
  "season": "2024",
  "type": "snake",
  "status": "pre_draft",
  "start_time": 1725500400000,
  "avatar": "d5e6f7g8h9i0j1k2",
  "created": 1725491200000,
  "updated": 1725491200000,
  "sport": "nfl",
  "settings": {
    "rounds": 15,
    "slots": 12,
    "position_limit": {
      "QB": 3,
      "RB": 6,
      "WR": 6,
      "TE": 3,
      "K": 2,
      "DEF": 2
    }
  },
  "metadata": null
}
```

### Completed linear draft

```json
{
  "draft_id": "111111111111111111",
  "league_id": "987654321098765432",
  "season": "2024",
  "type": "linear",
  "status": "complete",
  "start_time": 1694400000000,
  "avatar": "a1b2c3d4e5f6g7h8",
  "created": 1694300000000,
  "updated": 1694410000000,
  "sport": "nfl",
  "settings": {
    "rounds": 12,
    "slots": 10,
    "position_limit": {
      "QB": 2,
      "RB": 5,
      "WR": 5,
      "TE": 2,
      "K": 1,
      "DEF": 1
    }
  },
  "metadata": { "theme": "Halloween" }
}
```

## Field usage notes

- **draft_id**: Use as primary key for caching/storage and to fetch picks.
- **status**: `pre_draft` drafts have no picks yet; `in_progress` drafts are live; `complete` drafts are historical.
- **type**: Determines optimal roster-building strategy. Snake alternates pick order each round; linear keeps same order.
- **start_time**: Check if future (not yet started) or past (already drafted). Best as local timezone conversion.
- **settings**: Always check position limits before validating a roster against a draft's constraints.
- **league_id**: Look up the associated league for season context and scoring settings.

## Related

- [Draft endpoints](/sleeper/drafts/endpoint.md) — How to fetch Draft objects.
- [Draft pick schema](/sleeper/drafts/pick-schema.md) — Structure of individual picks.
- [League schema](/sleeper/leagues/league-schema.md) — Parent league metadata.

## Citations

[1] [Sleeper API Docs — Drafts](https://docs.sleeper.com/#drafts)
