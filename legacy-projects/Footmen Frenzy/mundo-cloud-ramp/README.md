# Mundo Disease Cloud ramp

Test map: `release/FF799X_Rx_Mundo_Cloud_Ramp_Test.w3x`. Includes the prior zero Intelligence/mana, Disease Cloud damage fix and Cleaver Wound work. Based on the separate v68-derived Mundo build; parallel Lux, Stalker and icon changes are not merged.

The existing click toggle remains. Continuous activation increases damage and health drain linearly from 1x to 2x over 10 seconds, then caps both. Toggling off, death, losing the ability or automatic low-health shutdown resets the ramp. Health drain integrates actual elapsed time on the existing quarter-second heartbeat; the first partial heartbeat is prorated. Mundo still stops before the next drain would kill him. Spell resistance and passive healing are unchanged.

| Rank | Damage/sec, start → full | Health/sec, start → full |
|---|---|---|
| 1 | 35 → 70 | 12 → 24 |
| 2 | 50 → 100 | 16 → 32 |
| 3 | 65 → 130 | 20 → 40 |
| 4 | 80 → 160 | 24 → 48 |
| 5 | 95 → 190 | 28 → 56 |
| 6 | 110 → 220 | 32 → 64 |

21 small particle models represent the ramp in half-second color increments: light green at activation; darker green around 3.3 seconds; purple mixed with dark green around 6.7 seconds; near-black at 10 seconds. The native Plague Cloud emitter is retained with authored particle colors and alpha blending, so dark particles remain visible. All models roundtrip through the parser, use model version 800, and reuse the installed native cloud texture. The dark stage slightly increases opacity. These are authored values; actual appearance requires an in-game check.

Clouds continue spawning every half-second and retain their emitted damage and color along the trail. They last approximately three seconds, and exposure leaves two seconds of poison. One poison timer per Mundo/victim holds four pending half-second doses. Each cloud refreshes those doses with the higher exposure strength: overlapping clouds do not add damage, old weaker clouds cannot overwrite stronger poison, and weaker exposure cannot keep maximum poison alive indefinitely. Leaving a powerful cloud therefore retains its strength for the existing two-second poison duration. Old trails persist after toggling off, as before.

Implementation: `ramp.j` adds five MC_ helpers. Hero MU_Hash keys 24 and 25 hold activation/payment times; scheduling stays at key 23, preserving cleaver key 20. Cloud key 46 snapshots DPS. Poison keys 50–53 hold pending doses. `changes.json` lists the seven modified functions, new helpers, AMu2 tooltip edit and 21 imported models. Runtime and editor WCT are synchronized. `prepare.py` accepts an optional baseline path that already includes the earlier Mundo health-kit and cleaver patches; it does not merge those prerequisites automatically.

Rebuild with bundled Python/Node: `prepare.py`, `assets.cjs`, `compile.py`, `checks.py`, `pack.py`. Compiler hashes reject stale script validation. The package verifies unchanged functions, unrelated ability records, old imports and unrelated archive entries. 65 actual translated-JASS/model/object checks cover the ramp, elapsed-time drain, all ranks, reset, low HP, overlap, lingering poison, cleanup and tooltip values.

Engine checks still needed: watch the complete 10-second color transition while standing and moving; compare enemy health loss and Mundo health drain at each stage; toggle off/on; overlap pale and dark trails; leave the gas; test death and low-health shutdown. Net health loss includes Mundo's existing regeneration. This build is not installed or deployed.
