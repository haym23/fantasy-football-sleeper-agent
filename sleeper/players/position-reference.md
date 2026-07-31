---
type: Reference
title: NFL Position Abbreviations
description: Standardized position codes used in player `position` and `depth_chart_position` fields.
tags: [positions, reference, nfl]
timestamp: 2026-01-21T00:00:00Z
---

# Position Codes

Fantasy football and Sleeper use standardized two-letter abbreviations for playing positions, aligned with NFL official terminology:

| Code | Position | Fantasy Slot | Notes |
|---|---|---|---|
| `QB` | Quarterback | QB | Pass attempts, TD passes, interceptions. |
| `RB` | Running Back | RB / FLEX | Carries, rushing TDs, receptions. |
| `WR` | Wide Receiver | WR / FLEX | Receptions, receiving TDs, yardage. |
| `TE` | Tight End | TE / FLEX | Receptions, receiving TDs. Less volume than WR. |
| `K` | Kicker | K | Field goals, extra points. |
| `DEF` | Team Defense | DEF | Sacks, interceptions, defensive TDs, shutout bonus. |
| `IDP` | Individual Defensive Player | IDP_FLEX | Tackles, sacks, interceptions, forced fumbles. (Position-agnostic; sub-positions exist in some leagues.) |

## FLEX eligibility

In a league with FLEX or SUPER_FLEX slots, those typically allow any of `{RB, WR, TE}` or `{QB, RB, WR, TE}` respectively. Depth chart position (`depth_chart_position`) is more permissive — a RB listed at an unusual spot still counts as RB within the league.

## Mapping to on-field positions

`position` and `depth_chart_position` are Sleeper's canonical values; they differ slightly from raw NFL designations:

- **Slot**: Classified as `WR` or `TE` depending on team and contract.
- **H-back / Hybrid**: Usually `RB` or `TE` depending on role.
- **Fullback**: Classified as `RB` for fantasy purposes.
- **Defensive backs**: All classified as `DEF` for team defense; individual secondary players are `IDP`.
- **Linebackers, Edge rushers**: All classified as `IDP`.

## Related

- [Player schema](/sleeper/players/player-schema.md) — `position` and `depth_chart_position` fields.

## Citations

[1] [Sleeper API Docs — Players](https://docs.sleeper.app/#players)
