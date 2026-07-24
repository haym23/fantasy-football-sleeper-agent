---
type: Schema
title: Matchup Object Schema
description: Field definitions for weekly matchup objects showing head-to-head pairings and scores.
tags: [leagues, matchups, schema, fields]
timestamp: 2026-01-21T00:00:00Z
---

# Matchup Object Schema

A Matchup object represents one team's configuration for a specific week in a league. Two matchup objects with the same `matchup_id` compete against each other.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `roster_id` | int | No | Team ID within league. |
| `matchup_id` | int | No | Pairing ID; two teams with same ID are opponents this week. |
| `players` | array (string) | No | All player_ids on the roster for this week. |
| `starters` | array (string) | No | Ordered player_ids in the starting lineup for this week. |
| `points` | float | Yes | Total fantasy points scored by the team for the week. Null if week hasn't started/finished. |
| `custom_points` | float | Yes | Commissioner manual override of points; null if no override. |

## Examples

### Two teams in the same matchup

```json
[
  {
    "roster_id": 1,
    "matchup_id": 2,
    "starters": ["421", "4035", "3242", "2133", "2449", "4531", "2257", "788", "PHI"],
    "players": ["1352", "1387", "2118", "2133", "2182", "223", "2319", "2449", "3208", "4035", "421", "4881", "4892", "788", "CLE"],
    "points": 132.45,
    "custom_points": null
  },
  {
    "roster_id": 3,
    "matchup_id": 2,
    "starters": ["2307", "2257", "4034", "147", "642", "4039", "515", "4149", "DET"],
    "players": ["1046", "138", "147", "2257", "2307", "2319", "4034", "4039", "4040", "4149", "421", "515", "642", "745", "DET"],
    "points": 118.22,
    "custom_points": null
  }
]
```

### Commissioner override

```json
{
  "roster_id": 5,
  "matchup_id": 7,
  "starters": ["2307", "2257", "4034", "147", "642", "4039", "515", "4149", "KC"],
  "players": ["1046", "138", "147", "2257", "2307", "2319", "4034", "4039", "4040", "4149", "421", "515", "642", "745", "KC"],
  "points": 145.5,
  "custom_points": 150.0
}
```

## Field usage notes

- **matchup_id**: Filter the response array by `matchup_id` to find both opponents. Each pair occupies two array entries.
- **starters**: Ordered list. Position order matches league's `roster_positions`; used for scoring calculation.
- **players**: All roster members active this week. Bench = `players` excluding `starters`.
- **points**: Reflects final score if the week is over. During live games, may be partial. Pre-week: null.
- **custom_points**: If set to non-null, overrides the calculated points for that team. Check both when calculating record or displaying scores.

## Derived calculations

### Head-to-head matchup winner

```
winner_roster_id = matchup[0].points > matchup[1].points ? matchup[0].roster_id : matchup[1].roster_id
```

### Bench scoring

```
bench_players = [p for p in matchup.players if p not in matchup.starters]
```

## Related

- [Roster schema](/sleeper/leagues/roster-schema.md) — Full-season roster composition.
- [Matchup endpoints](/sleeper/leagues/endpoint.md#get-matchups-for-a-week) — How to fetch matchups.
- [League state reference](/sleeper/leagues/state-reference.md) — Current NFL week and league phase.
- [Player schema](/sleeper/players/player-schema.md) — Player details by ID.

## Citations

[1] [Sleeper API Docs — Leagues: Getting matchups in a league](https://docs.sleeper.com/#getting-matchups-in-a-league)
