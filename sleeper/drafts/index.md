# Sleeper Drafts

The Sleeper Drafts API provides access to league draft listings, draft state, and round-by-round pick history.

## Quick Start

Always check the database first: [Storage](../storage.md) for querying existing draft data before hitting the API.

## API Reference

* [Draft Endpoints](./endpoint.md) - HTTP routes for drafts, picks, and traded picks.

## Schema & Data Types

* [Draft Object Schema](./draft-schema.md) - Metadata, timing, and configuration fields.
* [Draft Pick Object Schema](./pick-schema.md) - Individual pick structure, round/pick position, keeper marks.
* [Draft Strategy and Type Reference](./draft-strategy.md) - Snake vs. linear ordering, positional scarcity, strategic patterns.

## Related

* [Players](../players/index.md) - Player info used in draft selection.
* [Leagues](../leagues/index.md) - League configuration for a draft.
