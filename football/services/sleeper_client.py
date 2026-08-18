import time

import httpx


class SleeperClient:
    """Thin wrapper over the Sleeper API with basic retry on 429/5xx."""

    def __init__(self):
        self._http = httpx.Client(base_url="https://api.sleeper.app/v1", timeout=30)

    def get(self, path: str):
        for attempt in range(3):
            resp = self._http.get(path)
            if resp.status_code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(2**attempt)
                continue
            resp.raise_for_status()
            return resp.json()
        return None

    # Convenience endpoints
    def state(self):
        return self.get("/state/nfl")

    def user(self, username: str):
        return self.get(f"/user/{username}")

    def user_leagues(self, user_id: str, season: str):
        return self.get(f"/user/{user_id}/leagues/nfl/{season}") or []

    def league(self, league_id: str):
        return self.get(f"/league/{league_id}")

    def league_users(self, league_id: str):
        return self.get(f"/league/{league_id}/users") or []

    def league_drafts(self, league_id: str):
        return self.get(f"/league/{league_id}/drafts") or []

    def draft_picks(self, draft_id: str):
        return self.get(f"/draft/{draft_id}/picks") or []

    def transactions(self, league_id: str, week: int):
        return self.get(f"/league/{league_id}/transactions/{week}") or []

    def players(self):
        return self.get("/players/nfl") or {}


client = SleeperClient()
