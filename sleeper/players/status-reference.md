---
type: Reference
title: Player Status and Injury Codes
description: Semantics of `status` and `injury_status` fields; when to exclude players from lineups.
tags: [status, injury, reference, eligibility]
timestamp: 2026-01-21T00:00:00Z
---

# Status Codes

## Primary Status Field

The `status` field indicates league eligibility and availability:

| Value | Meaning | Fantasy Impact | Lineup Risk |
|---|---|---|---|
| `active` | The player is on the team's active roster and eligible to play. | Eligible to start. | Low — can be benched or activated without league penalty. |
| `injured_reserve` | The player is on IR; team cannot use them in games until activated. | Ineligible. | High — cannot play until status changes. |
| `out` | The player is out for this game or week but expected to return. | Ineligible for this week only. | Medium — check `injury_status` for return timeline. |
| `suspended` | The player is under league suspension (NFLPa violation, etc.). | Ineligible. | Highest — return date is league-determined. |
| `unknown` | Sleeper lacks eligibility data (rare; usually resolves within 24 hours). | Treat as `active` with caution. | Medium — verify manually. |
| `null` | Prospect, undrafted, or not yet in the league. | Ineligible for fantasy. | N/A |

## Secondary Status Field

`injury_status` provides free-text detail about the nature of an injury or absence, independent of `status`:

```
"Hamstring"
"Knee - Out"
"Finger - Doubtful"
"Suspension - Appeals"
"PUP List (knee)"
```

### Decoding injury_status

The field is unstructured. Common patterns:

| Pattern | Interpretation |
|---|---|
| `<body_part>` | Injured in that area, timeline unclear. |
| `<body_part> - <confidence>` | Confidence level: `Doubtful`, `Questionable`, `Probable`, `Out`. |
| `Suspension - <reason>` | Under suspension; includes reason if available. |
| `PUP List (...)` | Physically Unable to Perform; usually injury-related. |
| Null / empty | No injury reported; status reason is not injury-related. |

**Do not parse `injury_status` as a state machine.** It is authored by Sleeper sports staff reflecting NFL/team reports. It changes mid-week in response to practice reports. The only canonical flag for ineligibility is `status`.

## Rostering and lineup rules (hard rules)

**Never start a player with any of:**
- `status` = `injured_reserve`, `out`, `suspended`, or `unknown`
- `injury_status` = `Out` or `Doubtful` (if parsing)

Always check the `status` field as the canonical source—it overrides all other signals.

## Update frequency

- `status` is updated by Sleeper sports staff as NFL transactions are announced. Usually within 1 hour of news.
- `injury_status` reflects daily practice reports and pregame activity. Most volatile on Fridays and Sundays.
- `bye_week` is set once per season; `depth_chart_position` lags by 12–24 hours.

## Related

- [Player schema](/sleeper/players/player-schema.md) — field definitions.

## Citations

[1] [Sleeper API Docs — Players](https://docs.sleeper.app/#players)
[2] [NFL.com Official Transaction Guidelines](https://www.nfl.com/)
