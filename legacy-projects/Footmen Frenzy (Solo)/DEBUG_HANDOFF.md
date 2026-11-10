# Solo Foots Debug Handoff

## Current test map

- File: `releases/SF_Test1.7_v85.w3x` (also delivered to `C:\Users\Ryan1\Documents\Warcraft III\Maps\Solo Foots\GPT\SF_Test1.7_v85\`)
- Base map: `releases/SF_Test1.7_v83.w3x`
- Map SHA-256: `13C1B4BA2061F7AC9F961BC172639935D718804124D2B5543AE705CE3FA480BF`
- Build source: `src/war3map.j`, `src/war3map.w3u`, `src/war3map.w3a`, `src/war3map.w3q`, `src/war3map.w3t`, `src/war3map.wts`
- JASS parser (pjass): **passed clean, zero errors** against the shared `JassHelper/common.j` (which now also declares `GetPlayerRacePreference`, added during this pass since it was genuinely missing)
- Object tables (w3u/w3a/w3q): all round-trip to the last byte
- **In-game load: not yet tested** (v82's own in-game status was also never confirmed — see below)

## v85: Lobby-safe rebuild of the 2K Overdrive change

- v84 was reported to crash while entering the lobby after being packed with
  `ReplaceWar3MapScript`. v85 was rebuilt directly from the known v83 map with
  the documented two-stage `MpqAdd` replacement flow.
- Exact extraction comparison against v83 shows only `war3map.j` changed.

## v84: Enable Overdrive with 2K mode

- Selecting the existing 2K/777 Club mode now also sets
  `udg_mode_overdrive=true`, activating the FF799X unit-upgrade port added in
  v83.
- Normal mode continues to use the default `udg_mode_overdrive=false` value.

## v83: Overdrive tech-tree ported from FF799X

Solo already carried the *original* simpler Overdrive system (income bonus,
base-ability cooldown via `A082`, the base-aura grants, the windwalk-adjacent
`BASE__Overdrive_Start/END` timers) — that part is old and shared lineage with
FF799X. What solo was missing was the newer per-unit tech-tree layer FF799X
grew afterward: 8 units, ~54 per-unit upgrades, 28 auto-spawn toggle
abilities, and the `FFOD_*` script functions that drive them. This pass ports
that layer in.

**Object data added** (whole entries copied from FF799X, all `TRIGSTR_`
references resolved to literal text since solo's `war3map.wts` doesn't define
FF799X's string ids):
- `war3map.w3u`: +1 new unit (`h060`/Soldier). `h05G` (Captain) already
  existed in solo with its own stats (base=hfoo, 480 HP) — only its missing
  name/tooltip/ubertip fields were added, stats untouched. Same for the 5
  units solo already had (`h014`/`h018`/`hdhw`/`n04X`/`ngh2`) — display
  fields only, no stat changes.
- `war3map.w3a`: +27 new abilities (`A1A0`-`A1AR` spawn toggles, minus one
  that already existed).
- `war3map.w3q`: +54 new upgrades (the full per-unit tech tree).

**Script wiring added to `src/war3map.j`:**
- 8 `FFOD_*` functions + `Trig_Overdrive_Windwalk` ported verbatim from
  FF799X's fixed build (both known FF799X bugs — missing `A1AC` install,
  `ffsp12` targeting the wrong slot — are already corrected in this port).
- `Trig_Update_base_variable_Actions`: installs the 28 spawn-toggle abilities
  on the base building.
- `Trig_Upgrades_level_Actions`: added the racial-tech clamp guard.
- `SoloFootsSpawnApplyStats`: applies `FFOD_ApplyUnitTech` per spawned unit.
- `SoloFootsSpawnForIndex`: spawns via `FFOD_SpawnType` (Undead T0 -> Ghoul
  override).
- `SoloFootsSpawnPlayerBand`: gated on a new `ffgs_spawn_enabled_player[]`
  flag array (defaulted `true` for every player/index in `InitGlobals`, since
  JASS booleans default `false` and this array didn't exist in solo before).

**Research buttons:** an earlier pass on FF799X wrongly concluded these
upgrades had no research buttons anywhere — that check looked at the `upgr`
field (Techtree - Upgrades Used, which appears on combat units) instead of
`ures` (Techtree - Upgrades Available, which appears on buildings and is what
actually generates command-card research buttons). FF799X already has all 54
wired via `ures` on its Tier Zero (`hbar`) tech-tree's four Tier 1 buildings
-- `h00W` (Human), `h00H` (Orc), `h00Z` (Undead), `h002` (NightElf) -- but
FF799X puts **all 54 on all 4** regardless of race, which likely overflows
the 12-slot command-card grid.

Solo's copies of those same 4 buildings existed but had none of the 54 wired
(`ures` only had 2 entries: `Rhar`,`Rhme`). This pass wires them in,
**filtered by race** rather than copying FF799X's all-54-everywhere pattern:
- `h00W` (Human): 23 upgrades (Rr01, Rm01-3, Rs01-2, Rsl1-2, Rcp1-2, Rft1-2,
  Rdm1-2, Rmo1, Rk01-4, Rd01-4)
- `h00H` (Orc): 14 upgrades (Rrd1-2, Rot1-3, Rbz1-4, Rta1-2, Rdt1-2, Rgr1)
- `h00Z` (Undead): 11 upgrades (Rba1-2, Rda1-2, Rgh1, Rfi1, Rmg1, Rab1, Rbn1,
  Rwr1, Rwl1)
- `h002` (NightElf): 6 upgrades (Rar1, Rhu1-2, Rdr1, Rdy1, Rdd1)

Each building's own racial tech (`Rhan`/`Robs`/`Rugf`/`R004`) was already
present separately and untouched.

## Resolved: the black screen after the lobby countdown

## Resolved: the black screen after the lobby countdown

Builds v73 through v80 crashed before the loading screen. `war3map.w3u` was corrupt —
`tools/PatchPageSelectorUnits.py` walked the modification list without accounting for the
4-byte end-of-modification marker, so its three additions were spliced into the middle of
an unrelated modification and were themselves written 4 bytes short.

Both patch scripts now regenerate from the clean `roundtrip/SF_Test1.7_v73/files/`
baseline and validate the whole table before writing. See [BUILD.md](BUILD.md).

Every build with the corrupt table has been moved to `releases/broken-w3u/` and
`Maps\Random Tests\BROKEN-w3u\`, except two that are git-tracked and were published:
`releases/SF_Test1.7_v73.w3x` and `releases/SF_Test1.7_v77.w3x`. Both are broken and
should be superseded by a corrected published build.

## Requested merge rules

- Use latest rc3 UI/zoom work.
- Do not take taverns.
- Do not change start-of-game triggers.
- Remove/disable swap system.
- Current filename format: `SF_Test1.7_v**.w3x`.

## Open items

- The map has never been loaded in Warcraft III on this line of builds. Everything below
  is unverified until it boots and plays through a full game.
- Loading screen subtitle and body text (`STRING 998`, `STRING 999` in `war3map.wts`) are
  still blank. The title is set.
- The lobby name says `Test50` while the filename says `v82`. The two version schemes have
  been drifting apart since `Test49` / `v73`.
- Admin commands (`-reveal`, `-debugmode`, `-killa`, `-hero`, `-fog`) are keyed to
  hardcoded battletags and gated on `udg_admin_level >= 90`. Confirm the account list is
  current before any public release.
