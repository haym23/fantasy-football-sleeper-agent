---
type: Schema
title: Roster Object Schema
description: Field definitions for roster (team) objects returned by the rosters endpoint.
tags: [leagues, rosters, schema, fields]
timestamp: 2026-01-21T00:00:00Z
---

# Roster Object Schema

A Roster object represents a team in a league: its player list, starters, and performance metrics.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `roster_id` | int | No | Team identifier within league (1–12, typically). |
| `league_id` | string | No | Parent league ID. |
| `owner_id` | string | No | Sleeper user ID of the roster owner. |
| `players` | array (string) | No | List of all player_ids on the roster (starters + bench). |
| `starters` | array (string) | No | Ordered list of player_ids in the starting lineup. Length matches league's roster_positions. |
| `reserve` | array (string) | No | Reserve/stash slots; typically empty during in-season, used for NA/out players in keeper leagues. |
| `settings` | object | No | Team-level stats and metadata; see [Roster Settings Object](#roster-settings-object). |

## Roster Settings Object

| Field | Type | Description |
|-------|------|-------------|
| `wins` | int | Season record wins. |
| `losses` | int | Season record losses. |
| `ties` | int | Season record ties. |
| `fpts` | float | Total fantasy points (integer or .5 decimal). |
| `fpts_against` | float | Total points against. |
| `fpts_decimal` | int | Trailing decimal places of fpts (e.g., `78` fpts_decimal = `.78`); full score is `fpts + fpts_decimal/100`. |
| `fpts_against_decimal` | int | Trailing decimal places of fpts_against. |
| `waiver_position` | int | Current waiver priority (lower is earlier). |
| `waiver_budget_used` | int | FAAB dollars spent (0 if not FAAB league). |
| `total_moves` | int | Count of transactions (trades, FA pickups, waivers). |

## Examples

### Active roster, mid-season

```json
{
  "roster_id": 1,
  "league_id": "206827432160788480",
  "owner_id": "188815879448829952",
  "players": [
    "2307", "2257", "4034", "147", "642", "4039", "515", "4149",
    "1046", "138", "2319", "4040", "421", "515", "745"
  ],
  "starters": ["2307", "2257", "4034", "147", "642", "4039", "515", "4149"],
  "reserve": [],
  "settings": {
    "wins": 5,
    "losses": 9,
    "ties": 0,
    "fpts": 1617,
    "fpts_against": 1670,
    "fpts_decimal": 78,
    "fpts_against_decimal": 32,
    "waiver_position": 7,
    "waiver_budget_used": 0,
    "total_moves": 0
  }
}
```

### Dynasty roster with reserves

```json
{
  "roster_id": 3,
  "league_id": "987654321098765432",
  "owner_id": "300000000000000001",
  "players": [
    "2307", "2257", "4034", "1046", "138", "147",
    "2319", "420", "515", "745", "990", "1234", "5678", "99999"
  ],
  "starters": ["2307", "2257", "4034", "1046", "138", "147", "2319", "420"],
  "reserve": ["99999", "5678"],
  "settings": {
    "wins": 8,
    "losses": 5,
    "ties": 0,
    "fpts": 1847,
    "fpts_against": 1523,
    "fpts_decimal": 45,
    "fpts_against_decimal": 12,
    "waiver_position": 1,
    "waiver_budget_used": 75,
    "total_moves": 18
  }
}
```

## Field usage notes

- **roster_id**: Integer position in the league, often (but not always) 1-indexed from the API perspective.
- **starters**: Always matches the league's `roster_positions` array in length. To get bench, subtract starters from players.
- **reserve**: Dynasty leagues may pre-reserve slots for prospects/injured players; regular season leagues leave this empty.
- **fpts_decimal**: Due to rounding in scoring, full points = `fpts + (fpts_decimal / 100)`. Always divide by 100 when combining.
- **waiver_position**: Lower number = earlier priority until a FA claim is made; then the claimant moves to the end.
- **waiver_budget_used**: Only populated in FAAB leagues. Compare against league's budget cap (check league settings).
- **players**: Includes all roster slots; cross-reference with [Player IDs](/sleeper/players/endpoint.md) to resolve names and positions.

## Related

- [League schema](/sleeper/leagues/league-schema.md) — Parent league configuration.
- [Roster endpoints](/sleeper/leagues/endpoint.md#get-rosters-in-a-league) — How to fetch rosters.
- [Matchup schema](/sleeper/leagues/matchup-schema.md) — Roster state in a given week.
- [Player schema](/sleeper/players/player-schema.md) — Cross-reference player_ids.

## Citations

[1] [Sleeper API Docs — Leagues: Getting rosters in a league](https://docs.sleeper.com/#getting-rosters-in-a-league)
