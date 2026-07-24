# Players API Update Log

## 2026-01-21 (continued)
* **Refactor**: Replaced copy-paste Python code in [storage.md](/sleeper/players/storage.md) with documentation linking to actual implementation in `ff/sync/players.py` and `ff/db.py`. Storage.md is now pure documentation pointing to canonical sources. No wrapper module needed.

## 2026-01-21 (initial)
* **Initialization**: Created conformant OKF bundle for Sleeper Players API reference. Replaces `players_api.md`.
* **Addition**: Added [storage.md](/sleeper/players/storage.md) — SQLite schema, queries, and patterns for LLM-assisted implementation.
