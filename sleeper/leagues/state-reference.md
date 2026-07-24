---
type: Reference
title: League Status and State Values
description: Enum values for league status and season_type fields, and NFL week state lookup.
tags: [leagues, enums, status, state]
timestamp: 2026-01-21T00:00:00Z
---

# League Status and State Reference

## League Status Enum

The `status` field on a League object indicates its lifecycle phase:

| Value | Meaning | Rosters | Draft | Transactions |
|-------|---------|---------|-------|-------------|
| `pre_draft` | Setup phase; league created, settings locked, waiting for draft. | No active rosters. | Hasn't started. | None possible. |
| `drafting` | Draft in progress. | Rosters exist but incomplete. | Live snake draft running. | No FA/waivers until post-draft. |
| `in_season` | Regular or playoff play. | Rosters active, trades/waivers enabled. | Completed (or best-ball). | All transaction types active. |
| `complete` | Season ended, read-only. | Rosters frozen. | Final. | None possible. |

## Season Type Enum

The `season_type` field indicates the current competitive phase:

| Value | Meaning | Context |
|-------|---------|---------|
| `regular` | Regular season, weeks 1–17 (NFL). | Most matchups occur here. |
| `playoff` | Playoff weeks, 18+. | Top 6–8 teams; bracket format. |

## Example: Status transitions within a season

```
[season opens] --setup--> pre_draft
   |
   +--[draft starts]--> drafting --[draft ends]--> in_season
                          |
                          +--[regular season]--> in_season (season_type: regular)
                             |
                             +--[playoffs start]--> in_season (season_type: playoff)
                                |
                                +--[league crowned]--> complete
```

## NFL Week / State Lookup

**Note:** Sleeper does not expose a league-state API endpoint. Instead, use Sleeper's or NFL.com's week calculation:

- **Regular season:** Weeks 1–17 correspond to NFL weeks.
- **Playoff weeks:** 18–21 map to playoff rounds (wild card, divisional, conference, super bowl).
- **Off-season:** Week 0 or null (no active week).

For determining the current week, check:
- Your league's `status` and `season_type`.
- Your app's local assumption of the current NFL week (e.g., via ESPN/NFL official calendar).
- Sleeper does not offer a `/nfl/state` endpoint; track this client-side.

## League Lifecycle Queries

### Active trade window?

```
league.status == "in_season" && league.season_type == "regular"
```

### Can roster changes happen?

```
league.status in ("drafting", "in_season")
```

### Is league read-only?

```
league.status == "complete"
```

## Related

- [League schema](/sleeper/leagues/league-schema.md) — Full League object structure.
- [Status reference query pattern](/sleeper/leagues/query-patterns.md#filtering-by-status) — How to filter leagues by state.

## Citations

[1] [Sleeper API Docs — Leagues](https://docs.sleeper.com/#leagues)
