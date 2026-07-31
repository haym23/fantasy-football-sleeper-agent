#!/usr/bin/env python3
"""Analyze draft patterns of CURRENT members of Innovate or Die across all seasons."""
import json, requests
from collections import defaultdict, Counter

BASE = "https://api.sleeper.app/v1"
DATA = json.load(open("sleeper/drafts/data_innovate_or_die_all_seasons.json"))

def get(path):
    r = requests.get(f"{BASE}{path}", timeout=20)
    return r.json() if r.status_code == 200 else None

# --- 1. Current members (2025 league) ---
cur_league_id = DATA["2025"]["league"]["league_id"]
cur_users = {u["user_id"]: u["display_name"] for u in get(f"/league/{cur_league_id}/users")}

# --- 2. Walk full history: seasons -> league, drafts, picks ---
seasons = {}  # season_year -> {league, drafts, picks, users, rosters, bracket}
# start from local data, then walk previous_league_id chain back
chain = [DATA[y]["league"] for y in sorted(DATA, reverse=True)]
seen = set()
leagues = []
for lg in chain:
    if lg["league_id"] not in seen:
        leagues.append(lg)
        seen.add(lg["league_id"])
prev = chain[-1].get("previous_league_id")
while prev and prev not in seen:
    lg = get(f"/league/{prev}")
    if not lg: break
    leagues.append(lg)
    seen.add(prev)
    prev = lg.get("previous_league_id")

for lg in sorted(leagues, key=lambda l: l["season"]):
    yr = lg["season"]
    lid = lg["league_id"]
    if yr in DATA and DATA[yr]["league"]["league_id"] == lid:
        drafts = DATA[yr]["drafts"]
        picks_by_draft = DATA[yr]["picks_by_draft"]
    else:
        drafts = get(f"/league/{lid}/drafts") or []
        picks_by_draft = {}
        for dr in drafts:
            if dr.get("status") == "complete":
                p = get(f"/draft/{dr['draft_id']}/picks")
                if p: picks_by_draft[dr["draft_id"]] = p
    users = {u["user_id"]: u["display_name"] for u in (get(f"/league/{lid}/users") or [])}
    rosters = get(f"/league/{lid}/rosters") or []
    bracket = get(f"/league/{lid}/winners_bracket") or []
    seasons[yr] = dict(league=lg, drafts=drafts, picks_by_draft=picks_by_draft,
                       users=users, rosters=rosters, bracket=bracket)

# --- 3. Season outcomes per user ---
# regular season 1st = best (wins, then fpts) among rosters; champion = bracket final winner
outcomes = defaultdict(dict)  # user_id -> {season: {'reg1': bool, 'champ': bool, 'wins':, 'rank':}}
for yr, s in seasons.items():
    ros = s["rosters"]
    if not ros: continue
    ranked = sorted(ros, key=lambda r: (-r["settings"].get("wins", 0), -r["settings"].get("fpts", 0)))
    for i, r in enumerate(ranked):
        o = outcomes.setdefault(r["owner_id"], {})[yr] = {
            "rank": i + 1, "wins": r["settings"].get("wins", 0),
            "losses": r["settings"].get("losses", 0),
            "fpts": r["settings"].get("fpts", 0),
            "reg1": i == 0, "champ": False, "roster_id": r["roster_id"]}
    # champion: final round match (highest round, winner 'w')
    if s["bracket"]:
        final = max(s["bracket"], key=lambda m: m["r"])
        champ_rid = final.get("w")
        for r in ros:
            if r["roster_id"] == champ_rid:
                outcomes[r["owner_id"]][yr]["champ"] = True

# --- 4. Draft profiles per CURRENT member ---
profiles = defaultdict(lambda: defaultdict(list))  # uid -> field -> list of per-season values
pick_details = defaultdict(lambda: defaultdict(list))  # uid -> season -> picks
for yr, s in seasons.items():
    for did, picks in s["picks_by_draft"].items():
        if not picks: continue
        draft = next(d for d in s["drafts"] if d["draft_id"] == did)
        n_rounds = max(p["round"] for p in picks)
        order = draft.get("draft_order") or {}
        by_user = defaultdict(list)
        for p in picks:
            uid = p.get("picked_by")
            if not uid:  # resolve via roster_id if missing
                ros = {r["roster_id"]: r["owner_id"] for r in s["rosters"]}
                uid = ros.get(p["roster_id"])
            if uid in cur_users:
                by_user[uid].append(p)
        for uid, ps in by_user.items():
            ps.sort(key=lambda p: p["pick_no"])
            pick_details[uid][yr] = ps
            P = profiles[uid]
            P["seasons"].append(yr)
            P["slot"].append(order.get(uid) or ps[0]["draft_slot"])
            P["first_pos"].append(ps[0]["metadata"]["position"])
            # position counts by draft third
            third = n_rounds // 3
            for label, lo, hi in (("early", 1, third), ("mid", third+1, 2*third), ("late", 2*third+1, n_rounds)):
                P[f"{label}_pos"].append(Counter(p["metadata"]["position"] for p in ps if lo <= p["round"] <= hi))
            P["pos_total"].append(Counter(p["metadata"]["position"] for p in ps))
            # round of first pick at each key position
            for pos in ("QB", "RB", "WR", "TE", "K", "DL", "LB", "DB", "DEF"):
                rnd = next((p["round"] for p in ps if p["metadata"]["position"] == pos), None)
                P[f"first_{pos}"].append(rnd)
            # position run detection: max consecutive same position
            run = mx = 1
            for a, b in zip(ps, ps[1:]):
                run = run + 1 if a["metadata"]["position"] == b["metadata"]["position"] else 1
                mx = max(mx, run)
            P["max_run"].append((mx, yr))
            # first IDP pick round
            idp = next((p["round"] for p in ps if p["metadata"]["position"] in ("DL","LB","DB","DE","DT","CB","S","IDP")), None)
            P["first_IDP"].append(idp)

# --- 5. Report ---
def avg(xs): 
    xs = [x for x in xs if x is not None]
    return round(sum(xs)/len(xs), 1) if xs else None

print("="*100)
print(f"Seasons available: {sorted(seasons)} | Current members: {len(cur_users)}")
print("="*100)
for uid, name in sorted(cur_users.items(), key=lambda kv: -len(profiles.get(kv[0], {}).get("seasons", []))):
    P = profiles.get(uid)
    if not P or not P["seasons"]:
        print(f"\n### {name} — no drafts found (likely new member)")
        continue
    print(f"\n### {name} ({len(P['seasons'])} drafts: {', '.join(P['seasons'])})")
    print(f"  draft slots: {P['slot']}")
    print(f"  first-pick positions: {P['first_pos']}")
    for pos in ("QB","RB","WR","TE","K","DL","LB","DB"):
        print(f"  first {pos} taken round: {P[f'first_{pos}']}  (avg {avg(P[f'first_{pos}'])})")
    print(f"  first IDP pick round: {P['first_IDP']} (avg {avg(P['first_IDP'])})")
    for label in ("early","mid","late"):
        tot = Counter()
        for c in P[f"{label}_pos"]: tot.update(c)
        print(f"  {label} rounds positions: {dict(tot.most_common())}")
    tot = Counter()
    for c in P["pos_total"]: tot.update(c)
    print(f"  total drafted: {dict(tot.most_common())}")
    print(f"  longest same-position runs: {P['max_run']}")
    out = outcomes.get(uid, {})
    for yr in P["seasons"]:
        o = out.get(yr, {})
        if o:
            flags = ("REG-SEASON 1ST " if o.get("reg1") else "") + ("CHAMPION" if o.get("champ") else "")
            print(f"  outcome {yr}: rank {o.get('rank')}, {o.get('wins')}-{o.get('losses')}, {o.get('fpts')} pts {flags}")
    # first 5 picks per season for narrative
    for yr in P["seasons"]:
        ps = pick_details[uid][yr][:6]
        print(f"  {yr} first picks: " + ", ".join(f"R{p['round']} {p['metadata']['first_name']} {p['metadata']['last_name']} ({p['metadata']['position']})" for p in ps))
