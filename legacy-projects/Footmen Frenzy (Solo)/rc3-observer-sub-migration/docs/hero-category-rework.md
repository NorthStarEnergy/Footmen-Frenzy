# Hero category rework — rc3 12p two-altar layout

Date: 2026-07-27
Base build: `FF799W_rc3_MicroArena_v2.w3x` / `work/war3map_v4b_merged.j` (SHA256 `e18836791901d2690b11e39596969cf17de4a92813784d4bf887f277f111318d`)

Authored from the user's spoken revisions. This file is the source of truth for the
new `udg_hero_category[]` table and the two-tavern split.

## Layout

- `udg_numberofSDcategories`: **11 -> 18** (non-W3C branch only; the `= 6` branch is
  W3C mode and runs its own table in `Trig_W3C_JASS_Actions`)
- **Main altar** (existing `'n02I'` per team, `udg_real_shop[1..4]`): categories **1-11**, 11 picks.
- **Carry altar** (new `'n02I'` per team): categories **12-18**, 7 picks.
- Every group must hold >= 4 heroes so all four teams draw uniquely (stocking removes
  the unit from its category group as it is dealt).
- Unchanged exclusions: category 0 (Halpmeh, Blooddancer, The NooK, Santa, Guardian)
  and hero index 99 `H02W` DA KILLA are not stocked in either altar.

## Main altar — categories 1-11 (54 heroes)

| Cat | N | Heroes |
|---|---|---|
| 1 | 4 | Paladin, Death Knight, Strongest Man Ever, The Summoner |
| 2 | 5 | Priestess of the Moon, Ravage, Ranger, Sylvanus, Man's Best Friend |
| 3 | 6 | Dark Ranger, Nerubian Queen, HatoUP, Dino Din, Angel of Doom, Ship's Doctor |
| 4 | 5 | Thrall, The Guard, Troll, Chieftan's Companion, Keeper of the Grove |
| 5 | 7 | Shadow Hunter, Heavenly Death Healer, Mad Wizard, Tactician, Dark Sorceress, Drunken Templar, Medivh |
| 6 | 4 | Blademaster, Jaood, Shadow, CattleBruiser |
| 7 | 4 | Akama, WooJ, Wheelchair Warlock, Thor |
| 8 | 5 | Monkey King, Soviet Sniper, Ratling Gunner, Deadeye, Sea Giant |
| 9 | 4 | Demon Hunter, Expohate, Lawyer, Architect |
| 10 | 4 | Firelord, Beastmaster, Shredder, Dark Necromancer |
| 11 | 6 | Falcon, Alchemist, Pander Prospero, Pirate, Corruptor, Witch Doctor |

## Carry altar — categories 12-18 (32 heroes)

Carry pool = the original categories 9/10/11 (32 heroes), repartitioned.

| Cat | N | Heroes |
|---|---|---|
| 12 | 5 | Hydralisk, Crypt Lord, Lich, Dread Lord, Tinker |
| 13 | 5 | Tauren Chieftain, Zeus, W-a-r-l-o-c-k, Edge, Warrior Mage |
| 14 | 5 | Warden, Brewmaster, Reaper, Far Seer, Sea Witch |
| 15 | 4 | Elemental Spirit, Archangel, Mountain King, Footgirl |
| 16 | 4 | Archmage, Blood Mage, Pit Lord, Shadow Shifter |
| 17 | 4 | Myrmidon Warrior, Avalanche, Dragon Tamer, Jaina |
| 18 | 5 | Fox, YETI, The Craziest Cat Ever, Shere-Khan, Reptile |

Roster CLOSED 2026-07-27. All 32 carries placed; every group >= 4.

## Totals

54 main + 32 carry = 86 = the full pool previously held in categories 1-11.

## Known integration points (script)

- `Trig_set_hero_stats_Actions` — the default `udg_hero_category[1..91]` table (rewrite here).
- `Trig_W3C_JASS_Actions` — separate W3C-mode category table, gated on `udg_version_W3C`.
  Uses its own smaller scheme; must be checked before shipping W3C mode.
- `Trig_Start_SD_*` — creates `udg_real_shop[1..4]` (`'n02I'` at `udg_SDtavern[1..4]`),
  then stocks one random hero per category via `GetRandomSubGroup(1, udg_hero_category_group[c])`.
- `udg_carryhero`/`carryhero2`/`carryhero3` — recorded from categories 9/10/11 today;
  must be re-pointed at the new carry categories and at the carry altar for the
  "SD only 1x carry" removal in `Trig_TP_hero_*`.
- Classic (non-SD) mode stocks `udg_hero[1..47]` split 11/12/12/12 across the four
  taverns and does not use categories — needs its own carry/non-carry split.

## BUILT 2026-07-27 — `FF799W_rc3_CarryTavern_v1.w3x`

Source: `work/war3map_carrytav.j` (SHA256 `9ca2b561e4426c066b0f801dc1a35a42bfe68eac98a01d627fec6dde872c77f1`),
derived from `work/war3map_v4b_merged.j`. Packed map SHA256 prefix `ee19caeb5fcfaf21`,
44,441,706 bytes. Copies in `Maps\newtest\` and `Maps\799b\`.

### The 9 edits

| # | Site | Change |
|---|---|---|
| C1 | globals, before `endglobals` | `CarryTav_shop/label/hero/count/locked` arrays |
| C2 | before `// Trigger: Start SD` | `CarryTav_*` system: `ShopFor`, `Register`, `MakeAltar`, `CreateAltars`, `LockTeam` |
| C3 | `Trig_Start_SD_Actions` | `udg_numberofSDcategories` 11 -> 18 (non-W3C branch) |
| C4 | `Trig_Start_SD_Actions`, non-mirror branch | `if udg_numberofSDcategories >= 12 then call CarryTav_CreateAltars()` |
| C5 | `Trig_Start_SD_Func022Func041Func001Func001Func001A` | stock routes through `CarryTav_ShopFor(team, cat)`; carries recorded via `CarryTav_Register` (replaces the three `udg_carryhero*` if-blocks) |
| C6 | `Trig_TP_hero_Func007Func019Func001Func003C` | carry threshold `>= 9` -> `>= 12` |
| C7 | `Trig_TP_hero_Actions` "SD only 1x carry" | three `AddUnitToStockBJ(udg_carryhero*…)` -> `call CarryTav_LockTeam(udg_teamnumber[…])` |
| C8 | `Trig_init` group-alloc loop | `exitwhen ( i > 12 )` -> `i > 18` — **blocker**: `udg_hero_category_group[13..18]` were null, so categories 13-18 would never have stocked |
| C9 | `Trig_MODE_new_Func014Func005Func001C` | "No Transmute" mode keyed off category `== 8`; the old cat-8 set (Falcon, Alchemist, Pander Prospero, Pirate, Corruptor, Witch Doctor) moved wholesale to cat 11, so the check is now `== 11` |

### Carry altar placement

Four extra `'n02I'` at `(-3072, 128)` `(-2304, 128)` face 130, `(-2304, -640)` `(-3072, -640)` face 310 —
teams 1/2/3/4 respectively, 271 units diagonally outward from each main altar. Verified against
`war3map.wpm`: all four are walkable, >= 128 from the room walls, and inside the team's own
`gg_rct_T{n}_SD_TAVERN` vision quadrant. Whole room is `gg_rct_TAVERN_AREA` (-3264,-800)-(-2080,288),
walkable interior X -3200..-2240, Y -736..224.

### Label

Unit renamed `Carry Tavern |cffff8000(MAX 1)|r` plus a permanent text tag "CARRY TAVERN - MAX 1"
(gold, zOffset 200) shown only to the owning team via `SetTextTagVisibility` inside a
`GetLocalPlayer()`/`IsPlayerInForce(udg_team[n])` guard (visibility-only, no handle created locally).

### Max-1 semantics

Team-wide, matching the pre-existing "SD only 1x carry" rule: the first player on a team to buy a
category-12-18 hero triggers `CarryTav_LockTeam`, which sets stock 0/0 on all 7 carries in that
team's carry altar and prints a notice to `udg_team[n]`. No restore on repick — same as before.

### Validation

JassParseCheck OK (9,685 declarations); function/endfunction balanced 3025/3025; 0 duplicate
function names; 502 `InitTrig_`; all 91 `udg_hero_category[]` assignments rewritten (77 changed);
compact repack per the 42,035,123 truncation rule (reclaimed 4.65 MB of orphaned script, 49.09 MB
-> 44.44 MB); round-trip 1207 files, script SHA exact, `ArchiveSize` == file size, one block at/after
the cut, `war3map.w3u` unchanged. **Not runtime-tested.**

### Deliberately not done

- **Classic / AP / mirror / W3C modes** keep one altar — they don't use the category table
  (W3C runs 6 categories, so `CarryTav_CreateAltars` is skipped there).
- `udg_carryhero`/`carryhero2`/`carryhero3` and `Trig_Start_SD_Func022Func041Func001Func001Func001Func002C/003C/004C`
  are now unreferenced. Left in place rather than deleted.
- `Trig_debug` group readout still loops categories 1-6 only (debug-only, harmless).
