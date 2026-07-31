#!/usr/bin/env python3
"""
Fetch historical draft results from Sleeper API.

Usage:
    python fetch_drafts.py <username> <league_name>
    
Example:
    python fetch_drafts.py haym23 "Innovate or Die"
"""

import requests
import json
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime
import sys

BASE_URL = "https://api.sleeper.app/v1"


def get_user_id(username: str) -> Optional[str]:
    """Look up user ID by username."""
    resp = requests.get(f"{BASE_URL}/user/{username}")
    if resp.status_code == 200:
        return resp.json()["user_id"]
    print(f"❌ User '{username}' not found")
    return None


def get_leagues(user_id: str) -> List[Dict[str, Any]]:
    """Fetch all leagues for a user from current & past seasons."""
    current_season = datetime.now().year
    seasons_to_try = [current_season, current_season - 1, current_season - 2]
    
    leagues = []
    for season in seasons_to_try:
        try:
            resp = requests.get(f"{BASE_URL}/user/{user_id}/leagues/nfl/{season}")
            if resp.status_code == 200:
                leagues.extend(resp.json())
        except Exception as e:
            print(f"  ⚠ Season {season}: {e}")
    
    return leagues


def find_league(leagues: List[Dict[str, Any]], name: str) -> Optional[Dict[str, Any]]:
    """Find league by name (case-insensitive prefix match)."""
    name_lower = name.lower()
    for league in leagues:
        if league.get("name", "").lower().startswith(name_lower):
            return league
    return None


def get_drafts(league_id: str) -> List[Dict[str, Any]]:
    """Fetch all drafts for a league."""
    resp = requests.get(f"{BASE_URL}/league/{league_id}/drafts")
    if resp.status_code == 200:
        return resp.json()
    return []


def get_draft_picks(draft_id: str) -> List[Dict[str, Any]]:
    """Fetch all picks from a draft."""
    resp = requests.get(f"{BASE_URL}/draft/{draft_id}/picks")
    if resp.status_code == 200:
        return resp.json()
    return []


def save_draft_data(league_id: str, league: Dict, drafts: List[Dict], picks_by_draft: Dict) -> str:
    """Save draft data to JSON file. Return file path."""
    league_name = league.get("name", "unknown").replace(" ", "_").lower()
    out_path = Path(f"sleeper/drafts/data_{league_name}_{league_id}.json")
    
    data = {
        "league": league,
        "drafts": drafts,
        "picks_by_draft": picks_by_draft
    }
    
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)
    
    return str(out_path)


def main(username: str, league_name: str):
    """Fetch and save draft history for a league."""
    print(f"\n🔍 Looking up user '{username}'...")
    user_id = get_user_id(username)
    if not user_id:
        return False
    print(f"✓ User ID: {user_id}")
    
    print(f"\n🔍 Fetching leagues for {username} (current and past seasons)...")
    leagues = get_leagues(user_id)
    if not leagues:
        print("❌ No leagues found")
        return False
    print(f"✓ Found {len(leagues)} league(s)")
    
    print(f"\n🔍 Finding league '{league_name}'...")
    league = find_league(leagues, league_name)
    if not league:
        print(f"❌ League '{league_name}' not found. Available:")
        for l in sorted(leagues, key=lambda x: x.get('season', 0), reverse=True):
            print(f"  - {l.get('name')} (season {l.get('season')}, {l.get('league_id')})")
        return False
    
    league_id = league["league_id"]
    print(f"✓ League: {league['name']} (ID: {league_id})")
    print(f"  Season: {league.get('season')}, Format: {league.get('settings', {}).get('league_format')}")
    
    print(f"\n🔍 Fetching drafts for '{league['name']}'...")
    drafts = get_drafts(league_id)
    if not drafts:
        print("❌ No drafts found for this league")
        return False
    print(f"✓ Found {len(drafts)} draft(s)")
    
    print(f"\n🔍 Fetching picks for each draft...")
    picks_by_draft = {}
    for i, draft in enumerate(drafts, 1):
        draft_id = draft["draft_id"]
        picks = get_draft_picks(draft_id)
        picks_by_draft[draft_id] = picks
        season = draft.get("season", "?")
        status = draft.get("status", "?")
        print(f"  [{i}/{len(drafts)}] Draft {draft_id} (season {season}, {status}): {len(picks)} picks")
    
    print(f"\n💾 Saving draft data...")
    filepath = save_draft_data(league_id, league, drafts, picks_by_draft)
    print(f"✓ Saved to {filepath}\n")
    
    return True


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <username> <league_name>")
        print(f"Example: {sys.argv[0]} haym23 'Innovate or Die'")
        sys.exit(1)
    
    username = sys.argv[1]
    league_name = sys.argv[2]
    success = main(username, league_name)
    sys.exit(0 if success else 1)
