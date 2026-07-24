---
type: APIRef
title: League Endpoints
description: HTTP routes for retrieving leagues, rosters, users, matchups, playoff brackets, and transactions.
tags: [leagues, endpoints, http]
timestamp: 2026-01-21T00:00:00Z
---

# League Endpoints

## Get all leagues for user

```
GET https://api.sleeper.app/v1/user/<user_id>/leagues/<sport>/<season>
```

Returns list of leagues a user is in for a given sport and season.

**URL Parameters:**
- `user_id` (string): Sleeper user ID.
- `sport` (string): `"nfl"` only.
- `season` (string/int): Year, e.g., `2024`.

**Response:** Array of [League Object](#league-object).

## Get a specific league

```
GET https://api.sleeper.app/v1/league/<league_id>
```

Returns a single league by ID.

**URL Parameters:**
- `league_id` (string): Sleeper league ID.

**Response:** [League Object](#league-object).

## Get rosters in a league

```
GET https://api.sleeper.app/v1/league/<league_id>/rosters
```

Returns all rosters (teams) in a league with player lists and stats.

**URL Parameters:**
- `league_id` (string): Sleeper league ID.

**Response:** Array of [Roster Object](#roster-object).

## Get users in a league

```
GET https://api.sleeper.app/v1/league/<league_id>/users
```

Returns all users and their metadata for a league.

**URL Parameters:**
- `league_id` (string): Sleeper league ID.

**Response:** Array of [LeagueUser Object](#leagueuser-object).

## Get matchups for a week

```
GET https://api.sleeper.app/v1/league/<league_id>/matchups/<week>
```

Returns all matchups (head-to-head pairings) in a league for a given week.

**URL Parameters:**
- `league_id` (string): Sleeper league ID.
- `week` (int): Week number (1–17 for regular season, 18+ for playoffs).

**Response:** Array of [Matchup Object](#matchup-object).

## Get playoff brackets

```
GET https://api.sleeper.app/v1/league/<league_id>/winners_bracket
GET https://api.sleeper.app/v1/league/<league_id>/losers_bracket
```

Returns playoff bracket matchups for a league.

**URL Parameters:**
- `league_id` (string): Sleeper league ID.

**Response:** Array of [Bracket Object](#bracket-object).

## Get transactions (free agents, waivers, trades)

```
GET https://api.sleeper.app/v1/league/<league_id>/transactions/<round>
```

Returns all player transactions (FA pickups, waiver claims, trades) for a week.

**URL Parameters:**
- `league_id` (string): Sleeper league ID.
- `round` (int): Week number (transaction round).

**Response:** Array of [Transaction Object](#transaction-object).

## Get traded draft picks

```
GET https://api.sleeper.app/v1/league/<league_id>/traded_picks
```

Returns all draft picks that have been traded in a league.

**URL Parameters:**
- `league_id` (string): Sleeper league ID.

**Response:** Array of [Traded Pick Object](#traded-pick-object).

## Objects

### League Object

| Field | Type | Description |
|-------|------|-------------|
| `league_id` | string | Sleeper's internal league ID. |
| `name` | string | League display name. |
| `season` | string | Four-digit year. |
| `sport` | string | Always `"nfl"`. |
| `status` | enum | `pre_draft`, `drafting`, `in_season`, or `complete`. |
| `season_type` | enum | `regular` or `playoff`. |
| `total_rosters` | int | Number of teams in league. |
| `draft_id` | string | Associated draft ID, null if no draft yet. |
| `avatar` | string | Sleeper avatar hash; build URL with `/avatars/<avatar_id>`. |
| `settings` | object | League-wide configuration object (roster positions, scoring). |
| `scoring_settings` | object | Scoring multipliers for each stat. |
| `roster_positions` | array | List of required roster slots, e.g., `["QB", "RB", "RB", "WR", "TE", "FLEX", "K", "DEF"]`. |
| `previous_league_id` | string | ID of prior season's league if this is a continuation. |

### Roster Object

| Field | Type | Description |
|-------|------|-------------|
| `roster_id` | int | Team ID within league (1–12). |
| `owner_id` | string | User ID of roster owner. |
| `league_id` | string | Parent league ID. |
| `players` | array | List of all player_ids on roster. |
| `starters` | array | Ordered list of player_ids in starting lineup. |
| `reserve` | array | Stash slots, typically empty during in-season. |
| `settings` | object | Team stats: `wins`, `losses`, `ties`, `fpts`, `fpts_against`, etc. |

### LeagueUser Object

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | string | Sleeper user ID. |
| `username` | string | Username (can change; use user_id for stability). |
| `display_name` | string | Human-readable name. |
| `avatar` | string | Avatar hash. |
| `is_owner` | boolean | True if user is commissioner (can be multiple). |
| `metadata` | object | May contain `team_name` field (custom team nickname). |

### Matchup Object

| Field | Type | Description |
|-------|------|-------------|
| `roster_id` | int | Roster involved in matchup. |
| `matchup_id` | int | ID of matchup; two rosters with same ID play each other. |
| `players` | array | All player_ids on this roster for this week. |
| `starters` | array | Player_ids in starting lineup, ordered. |
| `points` | float | Total fantasy points scored. |
| `custom_points` | float | Manual override by commissioner, null if none. |

### Bracket Object

| Field | Type | Description |
|-------|------|-------------|
| `r` | int | Round number (1, 2, 3, …). |
| `m` | int | Match ID, unique within bracket. |
| `t1` | int \| object | Roster ID of team 1, or `{w: <match_id>}` (winner of match) or `{l: <match_id>}` (loser). |
| `t2` | int \| object | Roster ID of team 2, or winner/loser reference. |
| `t1_from` | object | Bracket path for t1: `{w: id}` or `{l: id}`. |
| `t2_from` | object | Bracket path for t2: `{w: id}` or `{l: id}`. |
| `w` | int | Winning roster_id, null if not yet played. |
| `l` | int | Losing roster_id, null if not yet played. |
| `p` | int | Placement (e.g., `p: 1` for 1st place match). |

### Transaction Object

| Field | Type | Description |
|-------|------|-------------|
| `transaction_id` | string | Unique transaction ID. |
| `type` | enum | `free_agent`, `waiver`, or `trade`. |
| `status` | enum | `pending`, `accepted`, `rejected`, or `complete`. |
| `created` | int | Unix timestamp (ms). |
| `status_updated` | int | Unix timestamp (ms) of last status change. |
| `leg` | int | Week the transaction occurred. |
| `creator` | string | User ID who initiated. |
| `roster_ids` | array | Rosters involved. |
| `consenter_ids` | array | Rosters that approved (for pending trades). |
| `adds` | object | `{player_id: roster_id}` pairs for adds. |
| `drops` | object | `{player_id: roster_id}` pairs for drops. |
| `draft_picks` | array | Traded draft picks (see [Traded Pick Object](#traded-pick-object)). |
| `settings` | object | For waivers, may contain `{waiver_bid: amount}` for FAAB. |
| `waiver_budget` | array | FAAB transfers between rosters. |
| `metadata` | object | Notes, typically null. |

### Traded Pick Object

| Field | Type | Description |
|-------|------|-------------|
| `season` | string | Draft year for this pick. |
| `round` | int | Round (1–12). |
| `roster_id` | int | Original owner's roster_id. |
| `previous_owner_id` | int | Prior owner's roster_id. |
| `owner_id` | int | Current owner's roster_id. |

## Rate Limit

Stay under 1000 API calls per minute to avoid IP blocking.

## Citations

[1] [Sleeper API Docs — Leagues](https://docs.sleeper.com/#leagues)
