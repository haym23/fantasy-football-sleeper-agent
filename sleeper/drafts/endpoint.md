---
type: APIRef
title: Draft Endpoints
description: HTTP routes for retrieving draft listings, draft metadata, and pick-by-pick history.
tags: [drafts, endpoints, http]
timestamp: 2026-01-21T00:00:00Z
---

# Draft Endpoints

## Get all drafts for a league

```
GET https://api.sleeper.app/v1/league/<league_id>/drafts
```

Returns all completed drafts associated with a league.

**URL Parameters:**
- `league_id` (string): Sleeper league ID.

**Response:** Array of [Draft Object](#draft-object).

## Get a specific draft

```
GET https://api.sleeper.app/v1/draft/<draft_id>
```

Returns metadata and configuration for a single draft.

**URL Parameters:**
- `draft_id` (string): Sleeper draft ID.

**Response:** [Draft Object](#draft-object).

## Get all picks in a draft

```
GET https://api.sleeper.app/v1/draft/<draft_id>/picks
```

Returns all picks made in the draft, in order, with player information.

**URL Parameters:**
- `draft_id` (string): Sleeper draft ID.

**Response:** Array of [Draft Pick Object](#draft-pick-object).

## Get all traded picks in a draft

```
GET https://api.sleeper.app/v1/draft/<draft_id>/traded_picks
```

Returns all draft picks that have been traded for future draft capital.

**URL Parameters:**
- `draft_id` (string): Sleeper draft ID.

**Response:** Array of [Traded Pick Object](#traded-pick-object).

## Objects

### Draft Object

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `draft_id` | string | No | Unique draft identifier. |
| `league_id` | string | No | Parent league ID. |
| `season` | string | No | Draft year (four-digit). |
| `type` | enum | No | `snake` (alternating) or `linear` (rounds repeat order). |
| `status` | enum | No | `pre_draft`, `in_progress`, or `complete`. |
| `start_time` | int | Yes | Unix timestamp (ms) when draft is/was scheduled to begin; null if not set. |
| `avatar` | string | Yes | Draft avatar hash; null if none. |
| `created` | int | No | Unix timestamp (ms) of draft creation. |
| `updated` | int | No | Unix timestamp (ms) of last status change. |
| `sport` | string | No | Always `"nfl"`. |
| `settings` | object | Yes | Draft configuration: scoring format, roster positions, etc. |
| `metadata` | object | Yes | Optional metadata; typically null or empty. |

### Draft Pick Object

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `draft_id` | string | No | Parent draft ID. |
| `round` | int | No | Round number (1-indexed). |
| `pick` | int | No | Pick number in round (1-indexed). |
| `roster_id` | int | No | Roster ID that made this pick. |
| `player_id` | string | Yes | Sleeper player ID; null if pick not yet made. |
| `picked_by` | string | Yes | User ID who made the pick; null if not yet picked. |
| `is_keeper` | boolean | Yes | True if this is a keeper pick (not newly drafted). |
| `metadata` | object | Yes | Optional metadata (e.g., player name snapshot at pick time). |
| `created` | int | No | Unix timestamp (ms) of pick. |

### Traded Pick Object

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `season` | string | No | Draft year this pick is for. |
| `round` | int | No | Round (1–12+). |
| `roster_id` | int | No | Original owner's roster_id. |
| `previous_owner_id` | int | No | Prior owner's roster_id. |
| `owner_id` | int | No | Current owner's roster_id. |

## Rate Limit

Stay under 1000 API calls per minute to avoid IP blocking.

## Citations

[1] [Sleeper API Docs — Drafts](https://docs.sleeper.com/#drafts)
