---
type: Reference
title: League Settings and Scoring Multipliers
description: Configuration objects for league-wide rules (rosters, waivers, scoring) and stat-by-stat scoring multipliers.
tags: [leagues, settings, scoring, configuration]
timestamp: 2026-01-21T00:00:00Z
---

# League Settings and Scoring Reference

## Settings Object

The `settings` field on a League object contains league-wide rules:

| Field | Type | Description |
|-------|------|-------------|
| `max_keepers` | int | Number of players a team can keep year-to-year (dynasty/keeper leagues). |
| `playoff_teams` | int | Number of teams that make playoffs (4, 6, 8, 10, 12). |
| `playoff_round_type` | int | 0 = bracket, 1 = elite playoff. |
| `playoff_seed_type` | int | 0 = no bonus, 1 = per-seed points. |
| `bench_lock` | int | 0 = no bench lock, 1 = bench locked during game start. |
| `disable_trades` | int | 0 = trades allowed, 1 = trades disabled. |
| `disable_adds` | int | 0 = FA/waivers allowed, 1 = disabled. |
| `waiver_type` | int | 0 = FAAB (auctioning $$ for pickups), 1 = rolling (resume order). |
| `waiver_day_of_week` | int | Day waivers run (0=Sun, 1=Mon, …, 6=Sat). |
| `waiver_clear_day` | int | Day unclaimed players become FA (typically 2 days after games). |
| `waiver_hour_of_day` | int | UTC hour (0–23) when waivers run. |
| `best_ball` | int | 0 = normal league, 1 = best-ball (auto-optimize lineup). |
| `league_average_match` | int | 0 or 1; if 1, every team plays the league average. |
| `change_settings_on_lock` | int | 0 or 1; if 0, settings locked when season starts. |
| `cpu_autopilot` | int | 0 or 1; whether manager can auto-set lineups. |
| `default_position` | string | Default position on roster when player added (e.g., `"BN"` for bench). |

## Scoring Settings Object

The `scoring_settings` field maps NFL stats to point multipliers:

| Stat | Type | Example Value | Notes |
|------|------|---|-------|
| `pass_yd` | float | 0.04 | Points per passing yard (0.04 = 1pt/25 yards). |
| `pass_td` | float | 4 | Points per passing TD. |
| `pass_int` | float | -2 | Points per interception thrown. |
| `rush_yd` | float | 0.1 | Points per rushing yard. |
| `rush_td` | float | 6 | Points per rushing TD. |
| `rec_yd` | float | 0.1 | Points per receiving yard. |
| `rec` | float | 1 | Points per reception. |
| `rec_td` | float | 6 | Points per receiving TD. |
| `fumble` | float | -2 | Points per fumble lost. |
| `fum_rec_td` | float | 6 | Points for fumble recovery TD. |
| `def_td` | float | 6 | Defensive TD. |
| `def_int` | float | 2 | Interception by defense. |
| `def_fum_rec` | float | 2 | Fumble recovery by defense. |
| `def_sack` | float | 1 | Sack by defense. |
| `pts_against` | float | -1 | Points per point allowed (defense). |
| `pts_against_6_13` | float | -1 | Per-tier scoring (6–13 pts allowed). |
| `def_tkl` | float | 0.5 | Defense tackle (if DST league). |

### Example: Standard PPR scoring

```json
{
  "scoring_settings": {
    "pass_yd": 0.04,
    "pass_td": 4,
    "pass_int": -2,
    "rush_yd": 0.1,
    "rush_td": 6,
    "rec": 1,
    "rec_yd": 0.1,
    "rec_td": 6,
    "fumble": -2,
    "def_sack": 1,
    "def_int": 2,
    "pts_against": -1
  }
}
```

### Example: Half-PPR with reduced passing TD

```json
{
  "scoring_settings": {
    "pass_yd": 0.04,
    "pass_td": 3,
    "pass_int": -1,
    "rush_yd": 0.1,
    "rush_td": 6,
    "rec": 0.5,
    "rec_yd": 0.1,
    "rec_td": 6,
    "fumble": -1,
    "def_sack": 1,
    "def_int": 2,
    "pts_against": -1
  }
}
```

## Field usage notes

- **waiver_type:** 0 = FAAB (teams have a budget); 1 = rolling (order resets after each claim).
- **waiver_day_of_week / waiver_hour_of_day:** Use to predict when waivers clear and FA pickups become possible.
- **disable_trades / disable_adds:** If either is 1, no transactions of that type are possible (league is locked).
- **best_ball:** 1 means no lineup management needed; scores are auto-optimized. Useful for one-and-done leagues.
- **scoring_settings:** Some leagues may have null values for unused stats. Always handle gracefully (default to 0).

## Common Settings Patterns

- **Re-Draft (1QB, PPR):** `max_keepers: 0`, `waiver_type: 1` (rolling)
- **PPR Dynasty (FAAB):** `max_keepers: null`, `waiver_type: 0`
- **Best-Ball:** `best_ball: 1`, `disable_adds: 1`

## Related

- [League schema](/sleeper/leagues/league-schema.md) — Full League object.
- [State reference](/sleeper/leagues/state-reference.md) — League lifecycle status.

## Citations

[1] [Sleeper API Docs — Leagues](https://docs.sleeper.com/#leagues)
