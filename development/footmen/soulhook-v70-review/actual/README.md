# Demon Knight — Soul Hook v70

Built only from `Veigar_Classic_v68/FF799X_Rx_Veigar_Classic_v68.w3x`
(SHA256 `ca55bf08…8b467b35`). v67 and v68 are preserved unchanged.

## What changed

- Demon Knight's **C slot** is now **Soul Hook** (`ADk5`). Blood Tithe (`ADk3`) is no longer on the hero.
- **Z Reaping Axe**, **W Pulverize** and **V Demon Ascension** are untouched.
- Blood Tithe's passive marks are therefore inactive: Soul Hook replaces the whole spell, not just the active half. The old `ADk3` object entry and the dead Blood Tithe code are still inside the map but unreachable.
- Map name is `Footmen Frenzy 799X Veigar Classic v70`.
- No new imported art, no new global variables, no other hero, item or system changed.

## Soul Hook (6 ranks)

Point-target hook, C hotkey, learn hotkey E.

| Rank | Mana | Cooldown | Magic damage | Stun | Learns at hero level |
|-----:|-----:|---------:|-------------:|-----:|---------------------:|
| 1 | 60 | 12.0 s | 120 | 0.5 s | 1 |
| 2 | 70 | 11.6 s | 160 | 0.6 s | 4 |
| 3 | 80 | 11.2 s | 200 | 0.7 s | 7 |
| 4 | 90 | 10.8 s | 240 | 0.8 s | 10 |
| 5 | 100 | 10.4 s | 280 | 0.9 s | 13 |
| 6 | 110 | 10.0 s | 320 | 1.0 s | 16 |

- **Cast range:** 450. **Travel:** about 0.25 s out (1800 units/s) and about 0.17 s home (2700 units/s).
- **Catch radius:** 150 around the flying head (300 wide), checked every tick on the way out.
- **Targets:** every eligible ground enemy the head passes. Buildings, flying units, magic-immune units, invulnerable units and locust/dummy units are excluded. Dead units and allies are ignored.
- **On catch:** magic damage, a short stun, a red burst effect, and a drag.
- **Drag:** each victim is pulled **partway** toward the caster, not all the way:
  - distance moved = 45% of the victim's distance to the caster, clamped to **150–400** and never closer than **100**;
  - drag speed 1280 units/s, direction recomputed every tick, so the victim is dragged toward the caster's current position;
  - the drag stops if terrain, a cliff or a building blocks the path, or if an obstacle displaces the victim by more than 8 units;
  - one drag per victim at a time, and one catch per victim per hook.
- **Visuals:** crimson `LEAS` lightning tether from caster to head, Death Coil missile head, Death Coil burst on each victim.
- **Cleanup:** the head expires after 1.5 s at the latest and every state is released if the caster dies.

## How it is implemented

Soul Hook reuses v68's Demon Knight state machine instead of adding a new system: kind 11 is the hook head, kind 12 is a dragged victim. Four new JASS functions (`DK_HookCast`, `DK_HookCatch`, `DK_HookChain`, `DK_HookStun`) and the tick branches share the existing `DK_*` arrays and `DK_Hash`, so the map's global block is byte-identical to v68.

`ADk5` is a Channel-based clone of Reaping Axe with base order `carrionswarm`, so it does not share a cooldown with Reaping Axe's `shockwave`. `ADk6` is a zero-damage Storm Bolt clone used only by the stun dummy.

## Unchanged Demon Knight values (for reference)

- **Reaping Axe (Z):** 1200 range, 180 radius, 110/150/190/230/270/310 magic damage per pass, 10 s cooldown, 70–95 mana. Return hits still pull enemies up to 100/150/200/350/450/550 toward the caster, stopping 100 away.
- **Pulverize (W):** passive, 25% chance on damaging attacks, 55/80/105/130/155/180 magic damage in 250 radius, 2 s proc cooldown.
- **Demon Ascension (V):** 15/18/21 s transform, 3/4/5% max-health regeneration per second, 60/80/100% attack speed, 25/30/35% movement speed, 40/50/60% cleave in 250 radius, plus 10 s Refuse Death. 150/175/200 mana, 180/150/120 s cooldown.

## Verification performed

Static and archive checks only:

- JassCheck parsed the full 64,998-line script.
- pjass compiled the script and the regenerated editor source against `common.j`/`Blizzard.j`.
- `war3map.w3a` and `war3map.w3u` object round-trips passed, and only the intended fields changed.
- The packed map was re-extracted member by member and every byte compared with the build inputs.
- Embedded runtime source, `FF_Runtime.j` and the packed script agree (`check_editor_runtime.py`: no missing, changed or unexpected functions/globals).
- The global declaration block is byte-identical to v68; changed functions are only `DK_Free`, `DK_Tick`, `DK_OnCast`, `DK_Init`, and the four new hook functions.
- Member count is 1373, identical to v68; the archive keeps v68's member set with the expected 12 members replaced.
- Archive preservation spot-check: terrain, pathing, doodads, units, regions, cameras, sounds, minimap and gameplay constants (`war3map.w3e`, `wpm`, `doo`, `war3mapUnits.doo`, `w3r`, `w3c`, `w3s`, `w3t`, `w3h`, `w3q`, `w3b`, `w3d`, `war3mapMap.blp`, `war3mapMisc.txt`, `war3map.w3i`, `shd`) are byte-identical to v68.
- v67 (`f51fd7d7…`) and v68 (`ca55bf08…`) hash-checked as unchanged after the build.

Final map SHA256: `f311fd6821d1746504a6cbfb93fdc0a23937758c3b6ff4843bff7b05f076fd9b`.

**Not tested in Warcraft.** Map loading, learn-panel layout, cast targeting, catch radius, stun duration, drag distance and collision handling, visuals, and multiplayer synchronisation are all unverified in the engine. No editor save or in-game playtest is claimed.

## Suggested playtest

1. Start a game, pick Demon Knight, and confirm the C slot shows Soul Hook with the chain-lightning icon and the E learn hotkey; Z/W/V must still be Reaping Axe, Pulverize and Demon Ascension.
2. Cast at a lone footman from maximum range: it should be hit in about a quarter second, take rank damage, be stunned briefly, and be pulled roughly 45% of the way, never closer than 100.
3. Cast into a clump of 4–6 units: all of them should be caught, damaged and stunned, and each should stop at a different distance.
4. Cast across a wall or cliff: the head may still reach, but victims must not be dragged through the obstacle.
5. Test magic-immune, flying, invulnerable and building targets — they must not be caught.
6. Verify cooldown and mana per rank, and that Blood Tithe marks/counter no longer appear anywhere.
7. Kill the Demon Knight mid-flight and confirm no lingering tether, effect or drag remains.
