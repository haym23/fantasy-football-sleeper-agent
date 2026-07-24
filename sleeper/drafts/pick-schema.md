---
type: Schema
title: Draft Pick Object Schema
description: Field definitions for individual picks in a draft.
tags: [drafts, schema, picks]
timestamp: 2026-01-21T00:00:00Z
---

# Draft Pick Object Schema

The Draft Pick object represents a single player selection made during a draft.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `draft_id` | string | No | Parent draft ID. |
| `round` | int | No | Round number (1-indexed; e.g., round 1 is the first round). |
| `pick` | int | No | Pick number within the round (1-indexed; e.g., pick 1 is 1st in that round). |
| `roster_id` | int | No | ID of roster (team) that made this pick. |
| `player_id` | string | Yes | Sleeper player ID of selected player; null if pick slot not yet filled. |
| `picked_by` | string | Yes | User ID who made the pick; null if not yet picked. |
| `is_keeper` | boolean | Yes | True if keeper pick (from prior draft), false for new selection, null if unknown. |
| `metadata` | object | Yes | Snapshot data at pick time (e.g., player first name, last name, position); typically null or sparse. |
| `created` | int | No | Unix timestamp (ms) of pick creation. |

## Calculated fields (derived from round and pick)

To find the **overall draft position** (1–180 for 12-team, 15-round):
- **Overall pick = ((round - 1) * slots) + pick**
  - Round 1, pick 3 in 12-team: `((1-1)*12) + 3 = 3` (3rd pick overall)
  - Round 2, pick 5 in 12-team: `((2-1)*12) + 5 = 17` (17th pick overall)

For snake drafts, later rounds have reversed order:
- **Odd rounds** (1, 3, 5…): picks 1–12 go to rosters 1–12 in order.
- **Even rounds** (2, 4, 6…): picks 12–1 go to rosters 1–12 in reverse order.

## Examples

### First round, snake draft

```json
[
  {
    "draft_id": "234567890123456789",
    "round": 1,
    "pick": 1,
    "roster_id": 1,
    "player_id": "7342",
    "picked_by": "user_a",
    "is_keeper": false,
    "metadata": { "first_name": "Patrick", "last_name": "Mahomes", "pos": "QB" },
    "created": 1725500401000
  },
  {
    "draft_id": "234567890123456789",
    "round": 1,
    "pick": 2,
    "roster_id": 2,
    "player_id": "6723",
    "picked_by": "user_b",
    "is_keeper": false,
    "metadata": { "first_name": "Josh", "last_name": "Allen", "pos": "QB" },
    "created": 1725500410000
  }
]
```

### Mid-draft with unpicked slot

```json
{
  "draft_id": "234567890123456789",
  "round": 5,
  "pick": 8,
  "roster_id": 8,
  "player_id": null,
  "picked_by": null,
  "is_keeper": null,
  "metadata": null,
  "created": 0
}
```

### Keeper pick

```json
{
  "draft_id": "234567890123456789",
  "round": 12,
  "pick": 3,
  "roster_id": 3,
  "player_id": "4156",
  "picked_by": "user_c",
  "is_keeper": true,
  "metadata": null,
  "created": 1725510200000
}
```

## Field usage notes

- **round / pick**: Reconstruct draft order and pacing. Check round and pick to know when a roster is "on the clock."
- **roster_id**: Maps picks to teams/rosters. Use to accumulate picks per roster.
- **player_id**: Links to [player data](/sleeper/players/endpoint.md) for full player metadata.
- **is_keeper**: Marks picks that don't represent new selections; useful for filtering real-draft picks only.
- **created**: Timestamp helps validate draft velocity and identify stalled/paused drafts.
- **metadata**: Light snapshot of player details at pick time; prefer fetching current player data from [Players API](/sleeper/players/endpoint.md) for accuracy.

## Round structure & snake logic

- **Total picks = rounds × rosters**: A 12-team, 15-round draft = 180 total picks.
- **Order changes by round** (in snake drafts):
  - Round 1 onwards, check parity to know direction.
  - Use `is_keeper` to filter genuine picks when analyzing draft strategy.

## Related

- [Draft schema](/sleeper/drafts/draft-schema.md) — Parent draft metadata.
- [Draft endpoints](/sleeper/drafts/endpoint.md) — How to fetch all picks via `/draft/<draft_id>/picks`.
- [Player schema](/sleeper/players/player-schema.md) — Full player information; use `player_id` to join.

## Citations

[1] [Sleeper API Docs — Drafts](https://docs.sleeper.com/#drafts)
