---
type: Schema
title: Playoff Bracket Schema
description: Field definitions for bracket matchups in winners and losers brackets.
tags: [leagues, brackets, playoffs, schema]
timestamp: 2026-01-21T00:00:00Z
---

# Playoff Bracket Object Schema

A Bracket object represents one playoff matchup in a winners or losers bracket. Supports 4, 6, and 8-team playoffs.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `r` | int | No | Round number (1, 2, 3, …). |
| `m` | int | No | Match ID, unique within the bracket. |
| `t1` | int or object | No | Roster ID of team 1, or `{w: <match_id>}` (winner of match) or `{l: <match_id>}` (loser). |
| `t2` | int or object | Yes | Roster ID of team 2, or winner/loser reference; null if TBD. |
| `t1_from` | object | Yes | Bracket path for t1: `{w: id}` or `{l: id}`; indicates progression. |
| `t2_from` | object | Yes | Bracket path for t2: `{w: id}` or `{l: id}`; indicates progression. |
| `w` | int | Yes | Winning roster_id; null if match hasn't been played yet. |
| `l` | int | Yes | Losing roster_id; null if match hasn't been played yet. |
| `p` | int | Yes | Placement index (e.g., `1` for 1st place, `3` for 3rd place consolation). |

## Examples

### 8-team bracket, first round (both matchups fixed)

```json
[
  {
    "r": 1,
    "m": 1,
    "t1": 3,
    "t2": 6,
    "w": null,
    "l": null,
    "t1_from": null,
    "t2_from": null
  },
  {
    "r": 1,
    "m": 2,
    "t1": 4,
    "t2": 5,
    "w": null,
    "l": null,
    "t1_from": null,
    "t2_from": null
  }
]
```

### Second round, seeded from first-round winners

```json
[
  {
    "r": 2,
    "m": 3,
    "t1": 1,
    "t2": null,
    "t2_from": {
      "w": 1
    },
    "w": null,
    "l": null
  },
  {
    "r": 2,
    "m": 4,
    "t1": 2,
    "t2": null,
    "t2_from": {
      "w": 2
    },
    "w": null,
    "l": null
  }
]
```

### Losers bracket, consolation matchup (feeds from first-round losers)

```json
{
  "r": 2,
  "m": 5,
  "t1": null,
  "t2": null,
  "t1_from": {
    "l": 1
  },
  "t2_from": {
    "l": 2
  },
  "w": null,
  "l": null,
  "p": 5
}
```

### Finals (winner determined)

```json
{
  "r": 3,
  "m": 6,
  "t1": null,
  "t2": null,
  "t1_from": {
    "w": 3
  },
  "t2_from": {
    "w": 4
  },
  "w": 1,
  "l": 2,
  "p": 1
}
```

## Field usage notes

- **r (round):** Bracket progresses through rounds; later rounds have fewer matches.
- **m (match):** Unique ID per bracket (not globally). Match 1 in winners bracket differs from match 1 in losers bracket.
- **t1 / t2:** 
  - If int: direct roster ID (fixed seed or bye).
  - If object `{w: id}`: winner of match `id` feeds here.
  - If object `{l: id}`: loser of match `id` feeds here (losers bracket).
- **t1_from / t2_from:** Only present when the team is a forward reference (winner/loser of another match). Helps visualize bracket progression.
- **w / l:** Null until the match is played. Once played, both fields are populated.
- **p (placement):** Optional, may be present. Used for tiebreaker or consolation indexing (e.g., `p: 1` for 1st place, `p: 3` for 3rd place). Not always populated.

## Bracket interpretation

### How to resolve a team in a future matchup

If `t1: {w: 5}`, the team in slot t1 is the winner of match 5. If match 5 hasn't been played:
1. Look up match 5 in the bracket.
2. Recursively resolve its participants until you hit a fixed roster_id or find an unplayed match.
3. If unplayed, t1 is TBD or in-progress.

### Render bracket lanes

```
Round 1   Round 2   Round 3
 [1 vs 8] ├─ W1 ──┐
          │       ├─ W3 ──┐
 [4 vs 5] ├─ W2 ──┘       ├─ Champion
          │               │
 [2 vs 7] ├─ W4 ──┐       │
          │       ├─ W6 ──┘
 [3 vs 6] ├─ W5 ──┘

Loser bracket (not shown but similar structure)
```

## Loser bracket specifics

- Loser bracket seeds from winners bracket losers.
- Round 2 losers bracket matches typically use `t_from: {l: id}` references.
- Placement (`p`) field helps identify consolation match destinations.
- Typical loser bracket: `t1_from: {l: 1}` and `t2_from: {l: 2}` → loser of match 1 faces loser of match 2.

## Related

- [Bracket endpoints](/sleeper/leagues/endpoint.md#get-playoff-brackets) — How to fetch winners/losers brackets.
- [Matchup schema](/sleeper/leagues/matchup-schema.md) — Week-by-week scores within a playoff matchup.
- [State reference](/sleeper/leagues/state-reference.md) — Detecting playoff season (`season_type: playoff`).

## Citations

[1] [Sleeper API Docs — Leagues: Getting the playoff bracket](https://docs.sleeper.com/#getting-the-playoff-bracket)
