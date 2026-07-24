---
type: Schema
title: Transaction Object Schema
description: Field definitions for trades, waiver claims, and free agent pickups in a league.
tags: [leagues, transactions, trades, waivers, schema]
timestamp: 2026-01-21T00:00:00Z
---

# Transaction Object Schema

A Transaction represents a player move: free agent pickup, waiver claim, or trade. All three types share the same base object with type-specific fields.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `transaction_id` | string | No | Unique identifier for this transaction. |
| `type` | enum | No | `free_agent`, `waiver`, or `trade`. |
| `status` | enum | No | Lifecycle: `pending` (awaiting approval), `accepted` (approved, completed), `rejected`, `complete`. |
| `created` | int | No | Unix timestamp in milliseconds when transaction was created. |
| `status_updated` | int | No | Unix timestamp in milliseconds of last status change. |
| `leg` | int | No | Week this transaction occurred. |
| `creator` | string | No | User ID of player who initiated the transaction. |
| `roster_ids` | array (int) | No | All roster IDs involved in transaction. |
| `consenter_ids` | array (int) | No | Roster IDs that approved the transaction (for pending trades). |
| `adds` | object | Yes | `{player_id: roster_id}` map of players added (null if none). |
| `drops` | object | Yes | `{player_id: roster_id}` map of players dropped (null if none). |
| `draft_picks` | array | Yes | Draft picks exchanged in a trade (see [Traded Pick Object](#traded-pick-object)). |
| `settings` | object | Yes | Waiver-specific settings; e.g., `{waiver_bid: 45}` for FAAB league. |
| `waiver_budget` | array (object) | Yes | FAAB transfers (trades involving money only; see [Waiver Budget Object](#waiver-budget-object)). |
| `metadata` | object | Yes | Additional context; may contain waiver rejection reason as string. |

## By Transaction Type

### Free Agent Pickup

```json
{
  "type": "free_agent",
  "status": "complete",
  "roster_ids": [1],
  "adds": {
    "2315": 1
  },
  "drops": {
    "1736": 1
  },
  "settings": null,
  "waiver_budget": [],
  "metadata": null
}
```

### Waiver Claim (FAAB)

```json
{
  "type": "waiver",
  "status": "accepted",
  "roster_ids": [3],
  "adds": {
    "4892": 3
  },
  "drops": {
    "2100": 3
  },
  "settings": {
    "waiver_bid": 24
  },
  "waiver_budget": [],
  "metadata": null
}
```

### Waiver Claim Rejected

```json
{
  "type": "waiver",
  "status": "rejected",
  "roster_ids": [2],
  "adds": null,
  "drops": null,
  "settings": {
    "waiver_bid": 45
  },
  "metadata": "Insufficient FAAB budget",
  "consenter_ids": []
}
```

### Trade (Player + Pick Swap)

```json
{
  "type": "trade",
  "status": "accepted",
  "roster_ids": [1, 2],
  "consenter_ids": [1, 2],
  "adds": {
    "2307": 2,
    "4034": 1
  },
  "drops": null,
  "draft_picks": [
    {
      "season": "2025",
      "round": 1,
      "roster_id": 2,
      "previous_owner_id": 2,
      "owner_id": 1
    },
    {
      "season": "2024",
      "round": 3,
      "roster_id": 1,
      "previous_owner_id": 1,
      "owner_id": 2
    }
  ],
  "settings": null,
  "waiver_budget": []
}
```

### Trade (FAAB Transfer Only)

```json
{
  "type": "trade",
  "status": "complete",
  "roster_ids": [1, 3],
  "adds": null,
  "drops": null,
  "draft_picks": [],
  "waiver_budget": [
    {
      "sender": 1,
      "receiver": 3,
      "amount": 55
    }
  ]
}
```

## Traded Pick Object

| Field | Type | Description |
|-------|------|-------------|
| `season` | string | Draft year for this pick. |
| `round` | int | Round (1–12). |
| `roster_id` | int | Original owner's roster_id. |
| `previous_owner_id` | int | Prior owner before this trade. |
| `owner_id` | int | Current owner after this trade. |

## Waiver Budget Object

| Field | Type | Description |
|-------|------|-------------|
| `sender` | int | Roster ID sending money. |
| `receiver` | int | Roster ID receiving money. |
| `amount` | int | FAAB dollars transferred. |

## Field usage notes

- **status**: `pending` = awaiting approval; `accepted` = approved but not yet processed; `complete` = finalized. For trades, check `consenter_ids` to see who's locked in approval.
- **leg**: Week number. Off-season trades may have leg=0 or null.
- **adds / drops**: One transaction can have multiple adds or drops (e.g., 2-for-1 trade or packaged multi-player deal).
- **settings**: Only for waivers. `waiver_bid` is the FAAB amount spent (or null for rolling waivers).
- **draft_picks**: For multi-season pick trades (dynasty). Cross-reference against `/traded_picks` endpoint for authority.
- **waiver_budget**: FAAB-only. Money transfers can occur independent of player trades (paying for cap space).
- **metadata**: For rejected waivers, may contain a reason string; otherwise typically null.

## Querying transactions

### Get all FA pickups in a week

```
txn in transactions[week] where txn.type == "free_agent"
```

### Get completed trades between two rosters

```
txn in transactions where txn.type == "trade" and txn.status == "complete" and (1 in txn.roster_ids and 2 in txn.roster_ids)
```

### Sum total FAAB spent by a roster

```
sum(txn.settings.waiver_bid for txn in transactions where txn.status == "complete" and roster_id in txn.roster_ids)
```

## Related

- [Transaction endpoints](/sleeper/leagues/endpoint.md#get-transactions-free-agents-waivers-trades) — How to fetch transactions.
- [Traded picks endpoint](/sleeper/leagues/endpoint.md#get-traded-draft-picks) — Draft pick trades authority.
- [Roster schema](/sleeper/leagues/roster-schema.md) — Team-level cumulative stats including total moves.
- [Settings reference](/sleeper/leagues/settings-reference.md) — Waiver type (FAAB vs rolling) and transaction rules.

## Citations

[1] [Sleeper API Docs — Leagues: Get transactions](https://docs.sleeper.com/#get-transactions)
