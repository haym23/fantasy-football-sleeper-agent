# Leagues API

The Sleeper Leagues API provides access to league configuration, rosters, matchups, transactions, and playoff brackets. All endpoints are read-only.

## Endpoints

* [League Endpoints](./endpoint.md) - HTTP routes for retrieving leagues, rosters, users, matchups, brackets, and transactions.

## Schema & Reference

* [League Object Schema](./league-schema.md) - Field definitions for individual league objects.
* [Roster Object Schema](./roster-schema.md) - Roster (team) composition, players, and stats.
* [Matchup Object Schema](./matchup-schema.md) - Weekly head-to-head pairings and scores.
* [Transaction Object Schema](./transaction-schema.md) - Free agent pickups, waiver claims, and trades.
* [Playoff Bracket Schema](./bracket-schema.md) - Winners and losers bracket matchup structure.
* [League Status and State](./state-reference.md) - Enum values for status and season_type; league lifecycle.
* [League Settings and Scoring](./settings-reference.md) - Configuration objects and stat scoring multilpliers.

## Implementation

* [League Data Storage](../storage.md) - Schema, queries, and operations for storing leagues in SQLite.
