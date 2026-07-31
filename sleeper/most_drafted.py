#!/usr/bin/env python3
"""Most-drafted players per current league member, across all saved seasons."""
import json
from collections import Counter, defaultdict
from pathlib import Path

import requests

DATA = Path(__file__).parent / "sleeper/drafts/data_innovate_or_die_all_seasons.json"


def main():
    data = json.load(open(DATA))
    latest = max(data)  # current season
    league_id = data[latest]["league"]["league_id"]

    users = requests.get(f"https://api.sleeper.app/v1/league/{league_id}/users").json()
    names = {u["user_id"]: u["display_name"] for u in users}
    print(f"Current users ({latest} league): {len(names)}\n")

    picks = defaultdict(Counter)
    for season, blob in data.items():
        for draft_picks in blob["picks_by_draft"].values():
            for p in draft_picks:
                if p["picked_by"] in names:
                    m = p["metadata"]
                    picks[p["picked_by"]][f'{m["first_name"]} {m["last_name"]} ({m["position"]})'] += 1

    for uid, name in sorted(names.items(), key=lambda kv: kv[1].lower()):
        print(f"{name}:")
        for player, n in picks[uid].most_common(5):
            print(f"  {player} x{n}")
        print()


if __name__ == "__main__":
    main()
