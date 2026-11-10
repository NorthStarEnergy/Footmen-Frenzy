# Consolidated 799X v84 TEST

This is the consolidated 799X candidate built November 4, 2026. Use `release/FF799X_Rx_Consolidated_v84_TEST.w3x`.

## Included work

- All v83 mainline content: repaired UI/icons, Lux Final Spark, Stalker movement/Blink fixes, Demon Knight Soul Hook, Mundo health kit/cleaver/cloud ramp, Veigar casting/ranges/visuals, Z permanent damage and V permanent damage from Z kills.
- Spawn-unit XP levels v75; the later v77 Colossal progression curve; v78 catch-up; v79 lagging-team Colossal rewards; v80 fed-player XP/gold rules.
- The installed v68 spawn intervals and v69 Ghoul/Grunt buffs, merged into both runtime/editor scripts and unit object data.
- Completed Guardian dome, pylon and icon assets, plus the selected Dark Matter icon branch, which were absent from v83.

## Conflict decisions and branch scope

V83 is the mainline base. Only four existing function bodies change: the installed spawn configuration/stat tables and the Guardian visual functions. Its other 3,804 functions remain identical. The v76 early-wave level reduction is superseded by the later v77 progression and v79 reward design; applying both would double-change those rules. The old Veigar Intelligence rewards are superseded by the requested Z/V flat-damage stacking.

Solo UPDATE08 and Mini Foots remain independent player-count/game-mode variants. Their separate spawn scheduler, mass staging, slot/team arithmetic, taverns, altar, camera and victory handling were not substituted for the 799X equivalents. `solo-review.json` records shared-function differences; this is not a completed semantic merge of every Solo change. The user's requested latest 799X consolidation does not convert the map into Solo. Historical casino/profile prototypes remain excluded under the prior project scope. Unfinished Veigar v69 travelling-projectile code is not imported over the completed and subsequently tested immediate-damage implementation.

## Verification

- Runtime pjass and reconstructed World Editor JassHelper/pjass compilation passed.
- No predecessor function is missing across v74 through v83; later-revision differences are enumerated in `coverage.json`.
- All 1,393 unrelated v83 archive entries preserved; packed payloads read back byte-for-byte.
- Six unit-stat fields merged; the Guardian pylon is the only added unit object. Existing abilities, buffs, items, upgrades, terrain, placed units and player configuration remain byte-identical to v83.
- Ten imported visual payloads match their completed donor artifacts. All 21 Mundo cloud models match their previously parsed/validated versions.
- Against the final packed scripts: 282 behavior/object assertions across Veigar, Soul Hook, Mundo cloud/cleaver/resources, Stalker and rewards; 1,000 randomized Stalker casts; 18,981 reward-curve cases passed. These use mocked Warcraft natives.

No Warcraft engine or multiplayer playtest was performed. Existing playtest questions about spell timing, visual rendering, Veigar cage scanning performance and native reward behavior remain. This is a verified consolidation candidate, not a claim that every historical variant or engine behavior has been tested.

## Files and rebuild

`build.py` compiles and packages from hash-checked v83, installed v69 and completed Guardian/Dark Matter donors. `merge-changes.json`, `verification.json`, `coverage.json` and `test-results.json` hold the detailed evidence. `verify-coverage.py` checks the final archive. The original maps remain untouched. Use the bundled Python; the legacy Warcraft compilers require execution outside the sandbox on this machine.
