---
type: Schema
title: Player Object Schema
description: Field definitions and types for individual player entries returned by the Sleeper Players API.
tags: [players, schema, fields]
timestamp: 2026-01-21T00:00:00Z
---

# Player Object Schema

Each key in the players API response maps to a player object with the following fields:

| Field | Type | Nullable | Description |
|---|---|---|---|
| `player_id` | string | No | Sleeper's internal player identifier. Stable across seasons. |
| `nfl_id` | string | Yes | Official NFL ID if the player is/was in the league. Empty for prospects or unsigned. |
| `full_name` | string | No | Player's legal name. |
| `first_name` | string | Yes | Given name, if split separately. |
| `last_name` | string | Yes | Surname, if split separately. |
| `position` | enum | No | NFL position: `QB`, `RB`, `WR`, `TE`, `K`, `DEF`, `IDP` (see [position mapping](/sleeper/players/position-reference.md)). |
| `depth_chart_position` | enum | Yes | Current depth chart position: one of `QB`, `RB`, `RB`, `WR`, `WR`, `TE` or null if not ranked. |
| `nfl_team` | string | Yes | Current NFL team abbreviation (e.g., `"KC"`) or null if not affiliated. |
| `number` | integer | Yes | Jersey number if in the league, null otherwise. |
| `status` | enum | No | Eligibility status: `active`, `injured_reserve`, `out`, `suspended`, `unknown`, or null. See [status reference](/sleeper/players/status-reference.md). |
| `injury_status` | string | Yes | Free-text injury notes, e.g., `"Hamstring"` or null if not injured. |
| `years_pro` | integer | Yes | Number of years in the NFL (0 = rookie year). |
| `college` | string | Yes | College name or null if international. |
| `injury_start_date` | string (ISO 8601) | Yes | Date injury occurred, if `status` is `injured_reserve`. |
| `bye_week` | integer | Yes | NFL team's bye week (1–17) or null. |

## Examples of common cases

### Active player, in-season

```json
{
  "player_id": "6802",
  "nfl_id": "07bcb5f4-f3c8-4e3d-b0fa-bd6c3e5b2e4a",
  "full_name": "Patrick Mahomes",
  "first_name": "Patrick",
  "last_name": "Mahomes",
  "position": "QB",
  "depth_chart_position": "QB",
  "nfl_team": "KC",
  "number": 15,
  "status": "active",
  "injury_status": null,
  "years_pro": 6,
  "college": "Texas Tech",
  "bye_week": 10
}
```

### Injured reserve

```json
{
  "player_id": "3456",
  "nfl_id": null,
  "full_name": "Example Receiver",
  "position": "WR",
  "nfl_team": "LAR",
  "status": "injured_reserve",
  "injury_status": "Ankle - Out",
  "injury_start_date": "2025-11-03",
  "bye_week": 6
}
```

### Prospect (pre-draft or prep league)

```json
{
  "player_id": "10001",
  "nfl_id": null,
  "full_name": "Prospect Name",
  "position": "WR",
  "nfl_team": null,
  "status": null,
  "years_pro": 0,
  "college": "Alabama"
}
```

## Nullability quirks

- `nfl_id` is empty for prospects and unsigned players, not missing.
- `injury_status` is checked independently of `status` — a player can have injury notes without being on IR.
- `bye_week` is team-driven; it appears even for backups.
- `depth_chart_position` lags official NFL updates by 12–24 hours.

## Related

- [Position mapping](/sleeper/players/position-reference.md) — enum values for `position` and `depth_chart_position`.
- [Status reference](/sleeper/players/status-reference.md) — semantics of `status` and `injury_status`.
- [API endpoint](/sleeper/players/endpoint.md) — mechanics of fetching the player list.

## Citations

[1] [Sleeper API Docs — Players](https://docs.sleeper.app/#players)
