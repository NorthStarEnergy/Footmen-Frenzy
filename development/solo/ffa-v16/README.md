# v16: T1/T2/T3 XP

Native non-hero XP table levels 1–4: 25,38,57,85 (previous stock values 25,40,60,85). Levels 2 and 3 cover all 15 distinct T1/T2/T3 spawned troop types. Level 1 footmen, level 4 T4 troops and level 6 T5 troops retain their base XP values; the explicit level-4 entry preserves the normal recurrence for subsequent levels.

The three existing tier-specific bonus XP award functions now grant 95% of their former integer per-hero award. Fractional hundredths carry over per hero, avoiding an excessive reduction from rounding every small award down. Existing range, sharing and hero-level eligibility rules remain. Normal engine XP sharing still uses Warcraft's own integer rounding.

Scope note: Warcraft's native XP table is keyed by unit level, not troop tier. Other non-hero units at level 2 or 3 also receive the base-XP reduction. No combat stats, unit levels, gold bounties, item prices, hero-kill XP, terrain or placements changed. unit-stats.json records the affected troop IDs, authored HP, damage, armor, attack speed, range, bounty and before/after base XP.

Build compiles runtime and synchronized editor JASS, round-trips 1298 entries, verifies unchanged object/terrain/placement data and troop stat initialization, and executes the packaged fractional XP helper against multiple hero/award sequences. Live gameplay verification remains pending.
