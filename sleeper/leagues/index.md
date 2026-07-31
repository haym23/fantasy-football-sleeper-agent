# Leagues API

The Sleeper Leagues API provides access to league configuration, rosters, matchups, transactions, and playoff brackets. All endpoints are read-only.

## Quick Start

Query existing data first: [Storage](/sleeper/storage.md).

## API Reference

* [League Endpoints](./endpoint.md) - HTTP routes for leagues, rosters, users, matchups, brackets, transactions.

## Schema & Data Types

* [League Object Schema](./league-schema.md) - Core league metadata, status, settings.
* [Roster Object Schema](./roster-schema.md) - Team composition, players, stats.
* [Matchup Object Schema](./matchup-schema.md) - Weekly head-to-head pairings and scores.
* [Transaction Object Schema](./transaction-schema.md) - Free agent pickups, waiver claims, trades.
* [Playoff Bracket Schema](./bracket-schema.md) - Winners/losers bracket matchup structure.

## Reference & Configuration

* [League Status and State](./state-reference.md) - Lifecycle enum values (pre_draft, drafting, in_season, complete).
* [League Settings and Scoring](./settings-reference.md) - League-wide rules and stat scoring multipliers.
