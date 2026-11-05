# 799X Consolidated InstaMass v36

One combined test map from the parallel October 29 builds. Previous releases are retained. Use **FF799X_Rx_Consolidated_InstaMass_v36.w3x** for the combined changes.

## Included

- Pub insta-mass: footmen stage hidden, paused and invulnerable in separate formation bands for all 12 players; all release together at the end of the existing 90-second countdown. Normal wave quantities remain unchanged (no Mini Foots 50% multiplier). Autosend, current upgrades, unit caps, mass speed, automatic roar, dead/inactive-owner cleanup and post-mass spawning are handled. Inhouse and no-mass modes retain their spawning behavior.
- Twisted Fate v33: larger orbs, cycle/lock/throw, homing red/gold/green effects, Gamble, normal selection.
- Mundo: Thunderaxe-style cleaver, health/distance scaling, ground pickup, Devour, allies-only completion healing, Undying, and the colored persistent poison trail. Mundo remains selectable.
- Demon Knight: two-pass returning axe, pull, Demon Ascension and Refuse Death. Applicable Requiem cleanup and repeated-completion protection retained in legacy functions.
- Guardian forcefield/channel/lantern, Gragus improvements and compact rank-specific hero tooltips inherited and checked.
- Gul'dan: imported model/portrait, matching voice, requested Z/X/C/V animations, and the final **Gul'dan — The Warlock** rename including hire/revive text.
- Veigar dummy hero: `-veigar`, Event Horizon and Dark Matter.
- Unrelated UI, zoom, terrain, map objects and assets from the common lineage retained.

## Explicit conflict resolutions

Mundo's later Devour/Undying kit replaces Fling/Sadism. His separate colored gas trail is integrated with the newer kit, preserving poison resistance and avoiding double area damage. Demon Ascension replaces Dread Requiem as requested in the Demon Knight rework; the old Requiem spell is not restored over it. The loop fix applies to retained legacy cleanup functions, while the live ultimate uses Ascension.

## Evidence

`inputs.json` records exact source maps and SHA-256 hashes. `merge-log.json` records donor changes and superseded edits. `verification.json` records function/object/archive preservation; `checks.json` records behavior coverage. All 168 existing hero checks were run against the combined source, plus 45 mass checks. The packed archive preserves 1,347 unrelated entries and 3,636 existing functions verbatim from the TF/Mundo-kit base. All 756 tested formation positions are walkable in the actual map pathing grid.

Compilation and archive readback pass. **Live Warcraft testing remains pending**, particularly simultaneous reveal, native Devour, gas clouds and model animation appearance. Automated tests use mocked Warcraft natives.

Rebuild in order with the bundled Python: `patch.py`, `checks.py`, compile `src/war3map.j` using the existing pjass/common.j/Blizzard.j, then `pack.py`. `Install.ps1` installs the checksum-verified new filename in both Warcraft Test directories and the shared release folder without replacing earlier versions. Gul'dan model/texture by Tauer: https://www.hiveworkshop.com/threads/guldan.295598/.
