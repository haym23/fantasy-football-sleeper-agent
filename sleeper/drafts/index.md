# Sleeper Drafts

The Sleeper Drafts provides access to league draft listings, draft state, and round-by-round pick history.

## Data

Always check for existing data in the database ([data/sleeper.db](../../data/sleeper.db)) before querying the Sleeper API.

Refer to [storage.md](../storage.md) to determine how to query the central database for draft information.

## Schema & Reference

* [Draft Object Schema](./draft-schema.md) - Field definitions for draft metadata, timing, and configuration.
* [Draft Pick Object Schema](./pick-schema.md) - Structure of individual picks, round/pick position, and keeper information.
* [Draft Strategy and Type Reference](./draft-strategy.md) - Snake vs. linear draft ordering, positional value, and strategy notes.

## Endpoints

* [Draft Endpoints](./endpoint.md) - HTTP routes for retrieving drafts, picks, and traded picks.

## Related

* [Players](../players/index.md) - player information used during draft selection.
* [Leagues](../leagues/index.md) - league configuration for a draft.
* [Storage](../storage.md) - information on how Sleeper data is stored
