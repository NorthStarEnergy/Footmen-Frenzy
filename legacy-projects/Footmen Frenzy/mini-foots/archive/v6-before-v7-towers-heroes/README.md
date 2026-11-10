# Mini Foots v1

Playable map: `release/Mini Foots v1.w3x`.
Installed copy: `C:\Users\User\OneDrive\Documents\Warcraft III\Maps\Mini Foots\Mini Foots v1.w3x`.

## Source

Based on the latest locally identified 799X testing build, `FF799X_Rx_HeroTavern_v1.w3x` (October 19, 2026), from the Warcraft III Maps/Test folder. The invisible, paused mass staging follows `Solo_Foots_v1.8_4P_PRELOAD_TEST07.w3x` (October 17).

The original maps were not overwritten. The executable JASS is authoritative. As with these inherited builds, World Editor trigger files do not describe all runtime custom systems: saving this map through World Editor can replace the custom script. Make gameplay changes in the source/build pipeline instead.

## Changes

The map browser description explicitly says 8 players, four teams of two. The preview has eight starting-location markers, and the in-game title reads Mini Foots v1.

- Four teams of two, exactly eight playable lobby slots. Original team slot numbering is retained internally to preserve existing team arithmetic, research sharing and shop redirects. Removed slots and observer slots are not playable.
- Removed the corner/middle base position from each three-base arrangement. The two outer positions remain, moved back 192 Warcraft units toward their outer edge.
- Four towers per team, two owned by each remaining player.
- Heroes stop at level 10 through gameplay constants.
- T2 is the highest base tier. All 30 higher-tier base types are unavailable, their upgrade links are removed, and the T3 unlock trigger is disabled.
- Attack and armor research both stop at level 5 in object data and player tech limits.
- All 25 purchasable creep types (including the old legacy capped type) are limited to one living unit of each type per team. Dead units do not block replacement. Duplicates are removed and their full configured gold price is refunded. Shop page-selection units are excluded.
- Pre-mass footmen spawn invisibly, paused, invulnerable and without pathing/food use in four formations in the middle. They become visible, active, vulnerable and pathable together when mass starts. Normal later spawning remains on the inherited schedule.
- Starting footmen are multiplied by 1.5 for each player. For odd totals, one teammate rounds down and the other up, preserving exactly the original three-player team's total. For example, 25 original footmen per player becomes 37 + 38 = 75 per team. This applies to the opening mass, not later normal waves.
- Automatic mass roar is cast in the middle formations. The inherited mass movement-speed boost is applied on release.
- All neutral backshop pages remain unchanged. Every active player gets their own overlapping `n003` upgrade shop; clicks still redirect to the selecting player's copy, and team research sharing remains intact. The fourth team now has both required copies explicitly created. Upgrade-shop positions and owners are recorded in `changes.json`.

## Verification

### October 28 Charge and HUD follow-up â€” current release

Ghoul now has 675 HP and 1 base heavy armor; Grunt has 800 HP and 2 base heavy armor. Both receive Militia's A0D9 Charge (+50% movement, +10% attack speed, 5 seconds, 30-second cooldown, zero mana and no damage-taken penalty). Its unavailable Robk requirement is cleared. Ghoul retains Cleave and 15% Evasion. Grunt has only 15% Evasion and Charge; its old Web autocast default is cleared. Object and runtime stats agree on both tech paths.

Zoom and Stats use the root game UI rather than the named console backdrop. Zoom creation is delayed 0.5 seconds, with explicit lock visibility and an unscaled value label. Stats creation no longer depends on multiboard visibility, and its initialization starts earlier. The slider texture names were checked against the installed game's escmenutemplates.fdf.

Compilation and 385 checks pass. Release SHA-256: `5226265ec156b7e0df66a478b6bfb648ea3b4f49d42d34d54711e124a90797cc`. Both map copies, including the active OneDrive directory, are updated; installed hash verified. The previous build is archived. Live UI testing remains pending; no running match was interrupted.


### October 28 melee roster and armor revision â€” previous release

Both former Burning Archer paths (17/44) now spawn the modified `ugho` object: 525 HP, 2 heavy armor, primary damage 14+2d2, 1.1s cooldown, 110 runtime melee range, Cleaving Attack and Evasion. Its separate structure attack (6+1d2, 1s cooldown) is retained. Both former T1 Headhunter paths (23/27) now spawn modified `ogru`: 750 HP, 4 heavy armor, damage 24+1d4, 1.6s cooldown, 110 range, with all four existing abilities. Normal attack typing is explicit. Tech names/tooltips/icons and XP/stat classifications follow the replacements. Spawn intervals, tech costs and bounty schedules remain unchanged.

Huntress, Banshee and Wraith now use unarmored typing in both object data and all relevant runtime paths. The late Banshee/Wraith medium-armor override is removed. Militia is heavy armor and 900 HP in both paths. All earlier UI/gameplay fixes remain in the build.

Compilation and 380 regression/archive checks pass. SHA-256: `2738cc09066b13891e591e5460a054387a06d9b320d34ec00fff9c28b311b476`. The previous combined release is archived as `archive/Mini Foots v1 - 2026-10-28 before melee roster.w3x`. Active OneDrive installation and live testing still await the user's match ending.

### October 28 combined follow-up â€” previous release

`release/Mini Foots v1.w3x` contains all requested revisions together. SHA-256: `4a61f508944d9fb28416a44df776bb2f3aba9f92b783f0da7817d40ed42a0247`.

- Compilation passes. 362 structural/archive checks pass; all 15 payloads match after extraction, and 1,247 untouched source files are preserved byte for byte.
- Stats now creates and updates exactly the eight retained player rows, with consistent text/icon coordinates and a footer below the rows.
- Gragas Fortitude directly adds/removes its armor bonus instead of attaching the ineffective Devotion Aura helper. X has a green icon; C has a simpler blue/cyan icon.
- Range application compensates for the native setter's additive behavior, so a second application at mass release still targets 110 for Footmen. Both object weapon ranges remain zero for all spawn types.
- Random-reward Boots of Speed use a distinct buff and independent +60 base-speed bonus, preserving amulet item bonuses. Pickup/drop and hero speed initialization retain/reverse it. Multiple boots do not stack; the normal 435 movement cap still applies. Item value 125 Ã— map pawn rate 0.6 = 75 gold resale.
- `audit/unit-audit.html` contains all 21 retained tech paths, eleven distinct units, script statistics, inherited object fields, and ability values. `audit/spawn-validation.json` models the quarter-second scheduler. This is source validation, not observed gameplay timing.
- `audit/request-checklist.html` records every requested change and its validation status.

The actual OneDrive Documents map and the running match still use the earlier build. Installation there and live interaction testing are pending until the user finishes the match. Do not exit or reload their match. Earlier builds remain in `archive/`.

### October 28 gameplay and UI revision

Zoom rendering follow-up: the slider now declares its track, thumb and disabled-state artwork explicitly instead of inheriting them from the horizontal menu template. Zoom and Stats controls use the console foreground parent. The earlier build is retained in `archive/Mini Foots v1 - 2026-10-28 before zoom repair.w3x`. Compilation and 330 structural/archive checks pass; installation and visual validation of this follow-up are pending while the active test match holds the installed map open.

- T1/T2 base research menus contain only attack and armor. Racial research sharing is disabled so it cannot restore the removed upgrades.
- Both object-data weapon ranges are explicitly zero on all 26 distinct spawned army unit types; the existing runtime range system remains authoritative.
- Each player's opening footmen occupy a distinct half of their team's diagonal mass front, in ten-column rows with 48-unit coordinate spacing.
- Pub starts automatically. Only the existing RJE accounts (`RJE#11113`, `RJE#2927`) receive Pub/Debug choices, in their own slot.
- Allied manual and automatic pooling unlock ten seconds before the actual T1 timer expires and remain enabled. Immediate debug tech unlocks enable pooling immediately.
- All six category-11 transmute heroes are disabled in shops and random/fallback selection.
- Zoom uses a proper vertical slider template. The slider, lock and value label are anchored together beside the minimap, clear of its buttons.
- The half-width `Stats` button is anchored above the minimap. Its panel opens within the screen independently of the button's new position.
- 328 checks passed; 1,252 unchanged files preserved. Ten payloads are packaged (eight changes plus two new UI files). This revision still needs in-game interaction and multiplayer testing; the older build's startup test does not validate this revision.
- Slider template reference: [Tasyen's camera-control tutorial](https://www.hiveworkshop.com/threads/ui-creating-a-cam-control.315961/).

### Previous build checks

- pjass compilation passed with the installed Warcraft III compiler and common.j/Blizzard.j.
- All seven changed archive files were re-extracted and matched their source bytes exactly.
- All 1,253 other extracted asset/data files matched the source map byte for byte.
- Structural checks passed for lobby slots/forces, sixteen towers, eight upgrade shops, level/research limits, blocked upgrade paths, creep catalog, mass release state and complementary mass-count rounding.
- Warcraft III loaded Mini Foots and entered gameplay. Blank labels were fixed by preserving the original WTS BOM/line endings, then verified visually. A full eight-player gameplay test is still pending.

Before release to players, test a full eight-player lobby: every player can select and research at the back upgrade shop; creep purchase/replacement/refund works across both teammates; all mass formations release together; T3 and upgrade level 6 are inaccessible; heroes stop at 10. Also test one disconnected teammate on each team.

## Build files

- `build_source.py`: deterministic changes from the extracted original map.
- `src/`: the seven authoritative modified payloads.
- `changes.json`: slots, coordinates, unit/creep raw IDs.
- `Pack-Map.ps1`: copy/patch MPQ with verification and full round-trip extraction.
- `verify.py`: structural and archive preservation checks.
- `pjass.log`, `verification.json`: validation evidence.

Python is the bundled Codex Python runtime. MPQ tools come from the local Solo Foots tools folder; .NET 10 is installed privately under `tools/dotnet` with major-version roll-forward for the .NET 8 packer. `Pack-Map.ps1` records its generated stage path in `last-build.txt`. Re-run `build_source.py`, pjass, `Pack-Map.ps1`, then `verify.py` after changes; do not publish an uncompiled build.

### October 28 spawn interval update
Solo v1.8 intervals with requested overrides: Footman 8s; Archer/Banshee 6s; Ghoul/Grunt 4.5s; Crypt Fiend 6.5s; Rifleman/Huntress 7s; Berserker/Militia/Wraith 5s. Both alternate tech paths match. One unit per wave and opening mass bonus are preserved. Compiler and 406 checks pass; 1,247 unchanged source assets preserved. Prior release archived before spawn intervals. Installation is pending: the installed map is locked by another process. Live timing/UI validation remains pending.


### October 28 tech costs, formations and compact Stats
T1 techs cost 600 gold and T2 techs cost 1300 gold across all paths. Allies stage on separate perpendicular fronts selected by their base position, with 12 units per rank at 64 spacing and a clear corner gap. Stats panel is 0.650 by 0.305 with 0.022 row spacing, smaller portraits and inset title/footer. All earlier spawn interval overrides remain. Compilation and 427 checks pass; 1,247 unchanged assets preserved. Prior release archived. Live visual testing remains pending; see verification.json for installation status.


### October 28 earlier timeline and 20-minute pooling
Mass countdown reduced from 90 to 60 seconds. Default T1 delay reduced from 240 to 210 seconds (alternate 290 to 260). T2 reduced from 540 to 420 seconds; underlying T3 from 720 to 480 seconds, while T3 remains blocked by the T2 cap. Pooling no longer follows tech: manual/automatic pooling unlock at game clock 20:00, with a visible Pooling available countdown that hides on unlock. Debug instant tech does not bypass pooling. Earlier work remains included.


### Release version policy
Current release: Mini Foots v6. For each subsequent delivered build, increment the displayed version (v3, v4, etc.) consistently in build_source.py, Pack-Map.ps1, verify.py, record_delivery.py and render_audit.py. Filename, SetMapName, W3I metadata, WTS title and in-game label must agree. Keep only the current W3X in each Mini Foots map directory and release directory; move superseded maps to an archive outside the active Mini Foots folder. Never overwrite an existing archived build.


### Mini Foots v3 layout
Moved each base inward from its corner into a mirrored two-base layout. Two evenly spaced towers stand toward the center in front of each base. All 24 structure positions have clear 192x192 terrain footprints; shop positions/ownership preserved. Lobby starts and minimap markers updated. Compilation and 432 checks pass. Installed v3 is the only map in each Mini Foots folder; v2 archived outside those folders. Prior gameplay changes retained. Live layout testing pending.


### Mini Foots v4 Orianna backport
Orianna functions and hor1/hor2, AOz5, BOr4/BOr5 objects are copied from the inspected FF799X_Rx_Orianna_v3 donor snapshot, together with its Orianna models, textures, icons and sounds. Adds clearer ball feedback, windup/return cleanup, sale/ownership registration and distinct slow buff. Non-Orianna functions are preserved from v3 (except map version config). port_orianna.py repeats this scoped import during builds. Prior Mini Foots gameplay/layout/UI changes remain. Live Orianna testing pending.


### Mini Foots v5 stats panel
Removed the panel title and bottom legend, and added an X at the upper right using the existing per-player Stats toggle. Compiled with pjass and passed 556 archive/structural checks. Installed and hash-verified in both Warcraft Mini Foots folders; v4 copies archived. In-game visual and interaction testing remains pending.


### Mini Foots v6 â€” 799X hero updates
Ports the Orianna and Gragus runtime, scoped objects, models, icons and effects from the 799X v12 hero update, using a frozen source snapshot. Mini's rules and eight-player UI remain. pjass and 652 structural/archive checks pass; matching hero functions and objects are verified against the donor. Installed and hash-verified in both Mini Foots map folders. Live gameplay and visual testing remain pending.

