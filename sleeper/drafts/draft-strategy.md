---
type: Reference
title: Draft Strategy and Type Reference
description: Draft format types (snake vs. linear), ordering logic, and common strategic patterns.
tags: [drafts, strategy, reference]
timestamp: 2026-01-21T00:00:00Z
---

# Draft Strategy and Type Reference

## Draft Types

### Snake Draft

Also called "alternating" or "serpentine" draft. Pick order reverses after each round.

**Order pattern (12-team example):**
- Round 1: Rosters 1 → 12 (picks 1–12)
- Round 2: Rosters 12 → 1 (picks 12–1 in reverse; 12 picks next, then 11, …, then 1)
- Round 3: Rosters 1 → 12 (resets to forward)

**Advantage:** Later picks get compensation; roster 12 picks 12th overall but 13th overall.

**Math:** Overall pick = `((round - 1) * num_teams) + pick_in_round`. Adjust for parity when round is even.

### Linear Draft

Same pick order in every round; no reversal.

**Order pattern (12-team example):**
- Round 1: Rosters 1 → 12 (picks 1–12)
- Round 2: Rosters 1 → 12 (picks 1–12 again; same order)
- Round 3: Rosters 1 → 12 (same order)

**Advantage:** Simpler logistics; earlier picks always go first.

**Disadvantage:** Early picks compound with advantage (more total picks); no built-in compensation.

## Position Value and Strategy

### Value at Different Draft Points

- **Early rounds (1–3)**: Elite positional talent. RB, WR scarcity peaks; QB/TE/K more abundant later.
- **Mid rounds (4–8)**: Tier transitions. Depth begins; secondary pass-catchers, flex options emerge.
- **Late rounds (9+)**: Lottery tickets, bench depth, lottery QBs, streaming defenses.

### Positional Scarcity

- **RB/WR**: Deep pool; many usable options across rounds but elite tier limited.
- **QB**: Abundant; elite QBs in rounds 5–8, but 20+ usable options drafted rounds 6+.
- **TE**: Bimodal; elite TE (Kelce, Andrews tier) rounds 1–3; cliff into mid-tier in rounds 5–7; waiver depth after round 8.
- **DEF**: Streaming viable; most drafted rounds 10–12; lottery options earlier by league preference.
- **K**: Deep pool; almost always available rounds 12+.

## Common Pitfalls

- **Positional run**: League mates reach on same position (e.g., QB in round 4). Adjust strategy; don't follow.
- **Bye week stacking**: Avoid drafting 2+ studs with same bye week; limits flexibility.
- **Bench waste**: Spending high picks on backup RBs/WRs when targets are uncertain. Prioritize starters.
- **Overestimating handcoff value**: Same backfield context doesn't guarantee same PPR PPG; context shifts.

## Keeper Considerations

[See `is_keeper` field](/sleeper/drafts/pick-schema.md#field-usage-notes) in pick data.

- **Keeper leagues**: Some picks marked `is_keeper: true` represent retained players from prior season, not new selections.
- **Salary caps**: Kept players may have associated cost (dynasty/auction format); check league [settings](/sleeper/leagues/settings-reference.md).
- **Strategic scarcity**: Keepers reduce available talent pool; adjust round expectations.

## Related

- [Draft schema](/sleeper/drafts/draft-schema.md) — Type field references this guide.
- [Draft pick schema](/sleeper/drafts/pick-schema.md) — Pick order and round structure.
- [League settings](/sleeper/leagues/settings-reference.md) — Roster positions and positional limits.

## Citations

[1] [Sleeper API Docs — Drafts](https://docs.sleeper.com/#drafts)
