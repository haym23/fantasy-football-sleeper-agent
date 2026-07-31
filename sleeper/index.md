# Sleeper Concepts

- [drafts](./drafts/index.md): Fetch current or historical draft information.
- [leagues](./leagues/index.md): Fetch league information.
- [players](./players/index.md): Fetch NFL player information.
- [storage](./storage.md): Central SQLite Database runbook and schema documentation.

## Behavior

- Whenever searching for data in Sleeper, first attempt to query the SQLite db before calling the Sleeper APIs

## Running Database Updates

Use the following implementation scripts to sync and manage Sleeper data:
- `sleeper/sleeper_db.py`: Unified SQLite manager. Query via `python sleeper/sleeper_db.py "SELECT ..."` or import `sleeper_db` in Python code.
- `sleeper/fetch_drafts.py`: Fetch and cache draft results from Sleeper API.
- `sleeper/analyze_drafts.py`: Analyze draft patterns across historical seasons.
