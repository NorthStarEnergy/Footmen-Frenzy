# Solo Foots 6 Player FFA v3

Current release: `release/Solo Foots 6 Player FFA v3.w3x`, installed in both local/OneDrive `Maps/Foots FFA` folders; v2 is archived. Includes the v26 Guardian/Gragus/Orianna refinements: deeper-blue fields +5% size, faster Gragus turning and deferred X drink animation, +25% Orianna X/V radii and V displacement, and feathered animated ground effects replacing fixed circles. Current pipeline: `../hero-polish/build.py`, `../hero-polish/pack.py`, `../hero-polish/Install.ps1`. Source and audits: `../hero-polish/solo`. Runtime and synchronized editor compilation, behavior checks and archive preservation pass. Live testing is pending.

## Historical v2 hero sync

Playable output: [Solo Foots 6 Player FFA v2.w3x](release/Solo%20Foots%206%20Player%20FFA%20v2.w3x).

The October 29 v2 update ports the complete Guardian, Orianna and Gragus hero systems and final WC3 button icons from `FF799X_Rx_WC3Icons_v25.w3x`. It includes the lantern runtime, custom lightning, model/texture/audio dependencies, buffs and cast-range fixes. Guardian is enabled and Orianna/Gragus are added to the existing eleven-category hero pool. Six-player selection, terrain, shops, economy, modes and other hero behavior are preserved. The World Editor custom script is synchronized with the playable script.

Both local and OneDrive `Maps/Foots FFA` installs are hash-verified; v1 is archived outside the active folder. Current source and release records are under `../hero-sync/solo`, with delivery paths in `../hero-sync/delivery.json`. Build with `../hero-sync/build.py`, validate/package with `../hero-sync/validate_pack.py`, then install with `../hero-sync/Install.ps1`. Those scripts use frozen v1/v8 inputs. The older build instructions below reproduce v1 only.

Validation: 6,819 structural/archive checks, hero behavior harnesses, and compilation of both runtime and editor scripts pass. All 1,197 untouched archive entries are preserved. Live Warcraft testing remains pending.

## Historical v1 layout notes

Derived from the newest local Solo Foots map found on October 28, 2026: `Solo_Foots_v1.8_8P_Compact_FFA_v3.w3x`. The original map is preserved. Its SHA-256 is recorded in `layout.json` and `verification.json`.

## Changes

- Exactly six playable slots and six independent FFA forces.
- Six radial bases fill the usable square. The previous exterior terrain and all obsolete static blockers are replaced by six narrow raised cliff dividers, open base ground, and a connected central arena.
- Each base has two owned towers, one owned upgrade shop, all eleven original neutral back-shop objects/pages, its own critter, and its own functional mode-selector base pet. Town halls continue to be created only for occupied slots.
- All base centers, hero arrivals, respawn/safe points, pet positions, lobby starts, editor placements, and minimap markers agree.
- One paged hero-selection tavern appears inside each active player's base. A successful choice removes that player's tavern. Fifteen seconds after the actual mass-start event, every active unpicked player receives a random hero and all remaining selection taverns disappear permanently.
- Separate force records fix KOTH income and research bookkeeping for all six players. The score board has six player rows. Old four-corner shop teleport/death zones are disabled because those coordinates now contain playable ground.
- The latest source's hero roster, unit statistics, economy, technology, mass count, second-hero farm system, assets, and game modes are retained. Opening formations follow the new sectors with slightly shorter files to fit ahead of the bases.
- World Editor custom script is synchronized with the runtime script. Terrain, placed objects and start locations remain editable. The editor binds existing placements instead of creating duplicates.

## Verification

Both runtime JASS and the editor wrapper pass pjass with the installed Warcraft API. `verification.json` records 1,954 checks, including full archive extraction, 13 changed payloads, and byte-for-byte preservation of 1,201 other payloads.

The actual selection function branches are executed in a Python harness with mocked Warcraft natives. Coverage includes paging, manual purchase, reentrant hero creation, exactly-once initialization, a leaving player, the 15-second timer, random fallback, repeated deadline calls and permanent closure. This is not an observed game-engine test.

A flood fill of the generated pathing confirms every walkable tile connects to the central arena. All 101 editor placements, six tavern positions and 516 opening-unit positions lie on reachable ground.

Live Warcraft III testing is pending. A running Warcraft III process was detected and left undisturbed. Test hero purchases, shop paging, tower research, six-player combat and the automatic fallback in a fresh match.

## Build

Use the bundled Python runtime at `C:/Users/User/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`.

1. `archive.py` extracts the original map with the existing local StormLib.
2. `inspect_source.py` records its placed-unit table.
3. `build.py` generates the revised payloads and layout preview.
4. `editor_source.py` synchronizes the editor script.
5. `verify.py` validates scripts and behavior, packages the map, adds its map-browser header and performs a complete archive round trip.

`layout-preview.png` is a schematic rendered from the generated terrain and placements; it is not an in-game screenshot. `delivery.json` records installed paths and hashes.
