# v77 colo XP curve

Built from v75 (including its army spawn-level correction). The set-aside v76 reduction is not included. Applies through the existing normal-Pub P67_Enabled gate.

Center boss level: 5 + integer((wave - 1) / 2). Base-pack XP excludes the center boss. Waves 1 and 2 retain their original pack XP. Wave 3 targets 1260 * 1.10; later waves compound the unrounded target by 1.05. Native integer unit levels approximate each target within 0.4%.

| Wave | Pack XP target | Actual pack XP | Boss level | Boss XP | Pack XP at 70% |
|---|---:|---:|---:|---:|---:|
| 1 | 1390.00 | 1390 | 5 | 115 | 973.0 |
| 2 | 1260.00 | 1260 | 5 | 115 | 882.0 |
| 3 | 1386.00 | 1390 | 6 | 150 | 973.0 |
| 4 | 1455.30 | 1450 | 6 | 150 | 1015.0 |
| 5 | 1528.07 | 1525 | 7 | 190 | 1067.5 |
| 6 | 1604.47 | 1600 | 7 | 190 | 1120.0 |
| 7 | 1684.69 | 1685 | 8 | 235 | 1179.5 |
| 8 | 1768.93 | 1765 | 8 | 235 | 1235.5 |
| 9 | 1857.37 | 1855 | 9 | 285 | 1298.5 |
| 10 | 1950.24 | 1950 | 9 | 285 | 1365.0 |

XP totals are for the directly spawned units in one team pack, before sharing and engine rounding. Subsequent summons/splits are excluded. Existing 70% native XP at hero level 7+ and below-7 catch-up still apply. Gold, composition, HP, damage, armor, drops and timing are preserved. Levels are assigned once at spawn, so survivors keep their original wave reward.

Validation: actual JASS level-helper translation executed against 1,564 cases; runtime pjass and authoritative editor JassHelper/pjass compile; WCT/runtime/source_roundtrip agree; packed payloads re-read exactly and 1,400 unrelated archive entries preserved. Engine and multiplayer playtest pending. Not installed or deployed.

Rebuild with the bundled Python runtime: build.py. The legacy JASS compilers require execution outside this sandbox on this machine. Per-unit tuning is in progression.j and wave-plan.json.
