# v78 individual catch-up to level 10

Built from the v77 colo-curve test map, including the v75 army spawn-level fix. Applies under the existing normal-Pub gate.

Before any active registered primary hero reaches 10, heroes at level 7+ receive 70% kill XP. The first valid hero to reach 10 permanently unlocks catch-up for individual heroes at levels 7–9, on every team. Each hero's own cumulative XP determines progress within its current level; team average and team membership do not change its rate.

Rate = 70% + 40 percentage points × (10 − fractional hero level).

| Hero progress | Before unlock | After unlock |
|---|---:|---:|
| 7 | 70% | 190% |
| 7.5 | 70% | 170% |
| 8 | 70% | 150% |
| 8.5 | 70% | 130% |
| 9 | 70% | 110% |
| 9.5 | 70% | 90% |
| 10+ | 70% | 70% |

Existing below-7 assistance remains in place. The first level-10 hero's allies receive only the rate appropriate to their own XP. Dead but active registered heroes remain valid; illusions, removed units, inactive slots and unregistered heroes cannot unlock the milestone. Repicking or losing the first level-10 hero does not revoke the unlock. The existing anti-cheat 25% rate takes precedence.

Native kill XP uses the player handicap; scripted kill supplements calculate through the same rate helper. No timer or milestone grants XP. Native rates update every second and immediately at level events; native XP awards are engine-sized chunks, so a large award can cross level 10 before the new rate applies to later awards. No XP is clawed back. In-engine event ordering and multiplayer balance remain untested.

The current map inherits stock cumulative XP thresholds: level 7 = 2700, 8 = 3500, 9 = 4400, 10 = 5400. The build rejects a map override of NeedHeroXP; future game-data changes need these constants rechecked. Tune P78_BONUS_PER_LEVEL in globals.j, then rebuild.

Validation: actual helper bodies executed with mocked Warcraft natives, including 2,701 fractional XP points, all 11 mode gates, unlock ordering, individual cutoff, leader removal, invalid heroes, no free grants, and scripted reward scaling. Runtime pjass and editor JassHelper/pjass pass. Runtime, WCT and source_roundtrip are synchronized; all packed changes re-read exactly; 1,400 unrelated archive entries preserved.

Rebuild with the bundled Python runtime: build.py. The local legacy compilers require execution outside the restricted sandbox. Not installed or deployed.
