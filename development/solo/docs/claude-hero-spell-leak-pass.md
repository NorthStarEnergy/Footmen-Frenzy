# Hero Spell Leak Pass — Location and Group Ownership

Behavior-preserving resource-ownership refactor of five hero systems in
`src/war3map.j`, taken from the `SF_Test1.7_v13` source of truth.

Baseline script SHA256 `1270C497A4535EBA95E122167D70042236A6D9850EB293A4C4057A4E9623A076`,
verified byte-identical to the packed `war3map.j` inside
`releases/SF_Test1.7_v13.w3x` before any edit.

No ability was rebalanced or redesigned. No `.w3x` was built.

---

## 1. Functions changed

Verified by extracting all 2,727 function bodies from the baseline and the
edited script and comparing them: **exactly six function bodies differ**, plus
one addition to the globals block. Function count is unchanged at 2,727.

| # | Function | System | Change |
|---|---|---|---|
| 1 | `Trig_HERO_Throw_Glaive_Loop_Func001Func001Func016Func001Func002C` | Throw Glaive | Distance test moved to coordinates |
| 2 | `Trig_HERO_Throw_Glaive_Loop_Func001Func001Func016Func001C` | Throw Glaive | Distance test moved to coordinates |
| 3 | `Trig_HERO_Throw_Glaive_Loop_Actions` | Throw Glaive | Flight path moved to coordinates |
| 4 | `Trig_Guardian_Force_Field_Cast_Actions` | Guardian Force Field | Caster angle read from coordinates |
| 5 | `Trig_HERO_Jaina_Ulti_Actions` | Jaina Ultimate | Handles moved to locals; group released |
| 6 | `Trig_HERO_Prison_Actions` | Prison | Wall points released before overwrite |

Globals block: added `real array sf_glaive_x` and `real array sf_glaive_y`
(with an explanatory comment) beside the existing `sf_*` helper globals.

**Examined and deliberately left unchanged:** every remaining function in the
five systems, including `Trig_HERO_Myrmidon_Sinkhole_start_Actions`,
`Trig_HERO_Myrmidon_Sinkhole_suck_Actions`, `SoloFootsFinishSinkhole`,
`SoloFootsEndSinkhole`, `SoloFootsClearSinkholeDummies`,
`SoloFootsCreateSinkholeDummy`, `Trig_HERO_Throw_Glaive_Actions`,
`Trig_Guardian_Force_Field_Loop_Actions`,
`Trig_Guardian_Force_Field_Damage_Actions`, `Trig_HERO_Prison_Func029A`,
`Trig_HERO_Prison_Func076A`, and `Trig_HERO_Prison_Wall_countdown_Actions`.
Reasons are in sections 5 and 6.

---

## 2. Before/after counts

Static counts of allocating calls (`GetUnitLoc`, `GetSpellTargetLoc`,
`PolarProjectionBJ`, `CreateGroup`, `GetUnitsInRangeOfLoc*`) against releasing
calls (`RemoveLocation`, `DestroyGroup`), over each system's function set.

| System | loc created | loc removed | grp created | grp destroyed |
|---|---|---|---|---|
| Sinkhole — before | 1 | 1 | 1 | 0 |
| Sinkhole — after | 1 | 1 | 1 | 0 |
| Throw Glaive — before | 10 | 3 | 0 | 0 |
| **Throw Glaive — after** | **2** | **2** | 0 | 0 |
| Guardian FF — before | 8 | 4 | 3 | 3 |
| **Guardian FF — after** | **7** | 4 | 3 | 3 |
| Jaina Ultimate — before | 6 | 2 | 1 | 0 |
| **Jaina Ultimate — after** | 5 | **5** | 1 | **1** |
| Prison — before | 9 | 9 | 1 | 1 |
| **Prison — after** | 9 | **13** | 1 | 1 |

Static counts understate the Throw Glaive win, because its allocations sat in a
0.02s loop. Per-execution leak rates:

| System | Leaked per execution — before | after |
|---|---|---|
| **Throw Glaive** | **2–7 locations per 0.02s tick, per player whose `udg_herO` is `E018`** — roughly 100–350 locations/second per such player | **0** |
| **Guardian Force Field** | 1 location per cast (`udg_Guardian_Point[0]`) | **0** |
| **Jaina Ultimate** | 4 locations + 1 group per cast | **0** |
| **Prison** | 0 on first cast; **4 locations per re-cast** while the previous wall was still standing | **0** |
| **Sinkhole** | 0 (already coordinate-based) | 0 |

The Throw Glaive loop body is gated only on `GetUnitTypeId(udg_herO[udg_X]) == 'E018'`,
not on a glaive actually being in flight, so the pre-existing leak ran for every
Sentinel player on every tick for as long as the loop trigger was enabled.

The Sinkhole group shown as created-but-not-destroyed is
`udg_waterfall[playerNumber]`, lazily created once per player in
`SoloFootsClearSinkholeDummies` and then reused for the rest of the game. That
is a deliberate persistent group, not a leak. `sf_sinkhole_enum_group` is
created once in `InitTrig_HERO_Myrmidon_Sinkhole_suck` and reused via
`GroupClear`, which is the correct pattern already.

---

## 3. Handle-ownership table

| Handle | Creator | Lifetime | Cleanup point |
|---|---|---|---|
| `sf_glaive_x/y[player]` | `Trig_HERO_Throw_Glaive_Loop_Actions` (first tick, when `udg_glaive_active` is still true) | One glaive flight | None needed — reals, not handles |
| `udg_temp_point`, `udg_temp_point_caster` (Glaive cast) | `Trig_HERO_Throw_Glaive_Actions` | Within the cast action | `RemoveLocation` at end of same function (pre-existing, correct) |
| `udg_Guardian_FF_Point[index]` | `Trig_Guardian_Force_Field_Cast_Actions` | Until that field expires | `RemoveLocation` in `Trig_Guardian_Force_Field_Loop_Actions` before the compaction transfer (pre-existing, correct) |
| `udg_Guardian_Point[0..3]` | `Trig_Guardian_Force_Field_Loop_Actions` on the expiry tick | Consumed by `Trig_Guardian_Force_Field_Damage_Actions` within the same tick | `RemoveLocation` in the wall loops of the same function (pre-existing, correct) |
| `udg_Guardian_Group[0]`, `[1]` | `Trig_Guardian_Force_Field_Damage_Actions` | Within that action | `DestroyGroup` in the same function (pre-existing, correct) |
| `casterPoint` (Jaina) | `Trig_HERO_Jaina_Ulti_Actions` local | Whole action, across all three sleeps | `RemoveLocation` at end of function |
| `orbPoint` (Jaina) | `Trig_HERO_Jaina_Ulti_Actions` local | One orb creation | `RemoveLocation` immediately after each `CreateNUnitsAtLoc` |
| `lightningPoint` (Jaina) | `Trig_HERO_Jaina_Ulti_Actions` local | The chain-lightning enumeration | `RemoveLocation` right after the pick |
| `chainCandidates` (Jaina) | `GetUnitsInRangeOfLocMatching` | The `GroupPickRandomUnit` call | `DestroyGroup` right after the pick |
| Jaina filter boolexpr | `Condition(...)` | The enumeration | Destroyed inside `GetUnitsInRangeOfLocMatching`, which calls `DestroyBoolExpr` (verified in `Blizzard.j`) — no action needed |
| `udg_prison_wall_point_1..4[player]` | `Trig_HERO_Prison_Actions` | Until the player's wall timer expires | `RemoveLocation` in `Trig_HERO_Prison_Wall_countdown_Actions`, **or** in `Trig_HERO_Prison_Actions` on re-cast (new) |
| `udg_prison_block_point_1..4[player]` | `Trig_HERO_Prison_Actions` | Within the cast action | `RemoveLocation` + null at end of same function (pre-existing, correct) |
| `udg_temp_unitgroup` (Prison) | `GetUnitsInRangeOfLocMatching` | Within the cast action | `DestroyGroup` at end of same function (pre-existing, correct) |
| `udg_waterfall[player]` | `SoloFootsClearSinkholeDummies`, once | Whole game | Intentionally persistent; emptied, never destroyed |
| `udg_waterfall_mid[player]` | `Trig_HERO_Myrmidon_Sinkhole_start_Actions` | Until the sinkhole ends | `RemoveLocation` + null in `SoloFootsEndSinkhole` (pre-existing, correct) |
| `sf_sinkhole_enum_group` | `InitTrig_HERO_Myrmidon_Sinkhole_suck`, once | Whole game | Intentionally persistent; `GroupClear` before each reuse |

---

## 4. Preserved values

Every rawcode, order, distance, angle, duration, and interval below was left
exactly as found. Arithmetic replacements were expanded from the `Blizzard.j`
definitions of the BJ wrappers they replace, so results are identical:

- `AngleBetweenPoints(A,B)` → `bj_RADTODEG * Atan2(B.y - A.y, B.x - A.x)`
- `DistanceBetweenPoints(A,B)` → `SquareRoot(dx*dx + dy*dy)`, `dx = B.x - A.x`
- `PolarProjectionBJ(src,d,a)` → `src.x + d*Cos(a*bj_DEGTORAD)`, `src.y + d*Sin(a*bj_DEGTORAD)`
- `SetUnitPositionLocFacingBJ(u,loc,f)` → `SetUnitPosition(u, loc.x, loc.y)` + `SetUnitFacing(u, f)`
- `IssuePointOrderLocBJ(u,o,loc)` → `IssuePointOrder(u, o, loc.x, loc.y)`

### Myrmidon Sinkhole (untouched)
Abilities `A05Y`, `A05Z`. Units `h029` (rim dummy), `h02A` (stomper), `h02B`.
Timed life `BTLF` 0.50s. Orders `"stomp"`, `"stop"`. Crater
`TerrainDeformationCraterBJ(0.50, false, center, 250.00, 100.00)`. Eight rim
offsets: (-75,0), (-50,-50), (0,-75), (50,-50), (75,0), (50,50), (0,75),
(-50,50). Pull radius `300.00 + 100.00 * level`. Pull step 1.0 unit per tick
toward centre. Tick 0.05s. Duration 60 ticks.

### Throw Glaive
Hero `E018`. Dummy `h053`. Ability pairs by branch: `A0MB`/`A0MT`, `A0MD`/`A0MS`,
`A0MC`/`A0MW`, `A0ME`/`A0MU`, `A0MF`/`A0MV`, `A0MA`/`A0MX`. Hop thresholds
`< 20`, `>= 20`, `>= 30`, `>= 40`, `>= 45`, `>= 50`, `>= 55`, `>= 57`. Step
distance 20.00 per tick. Return-trip abort distance 1300.00. Catch distance
100.00. Facing forced to 0.00 every tick. Tick 0.02s. The `- 0.00` / `+ 0.00`
no-op angle assignments in the first five hop branches are retained verbatim.

### Guardian Force Field
Abilities `AFFD` (detonate), `AFFS` (stun). Dummy `dmmy`. Durations per level
3.00 / 3.00 / 3.50 / 4.00 / 5.00 / 5.00. Wall offsets 128.00 and 256.00 at
`angle ± 90.00`. Pathing blocker radius 64, `PATHING_TYPE_ANY`. Damage/stun
radius 225.00. Dummy timed life 0.25s, `BTLF`. Effect scale 0.95 (field) and
1.75 (death visual), time scale 2.50. Models `SC2ForceField_ByEpsilon.mdx` and
`Abilities\Spells\NightElf\Blink\BlinkCaster.mdl`. Order `"stomp"`. Tick 0.02s.

### Jaina Ultimate
Ability `A048`. Orbs `h01L`, `h01M`, `h01N`. Orb abilities `A063`, `A064`,
`A065`. Orb ring radius 80.00 at 0, 120.00 and 240.00 degrees — the first angle
is still the integer literal `0`, exactly as before. Orders `"stomp"`,
`"rainoffire"`, `"chainlightning"`. Chain-lightning search radius 512. Sleeps
1.00s, 1.00s, 2.00s.

### Prison
Ability `A0GL`. Walls `h02T` (points 1 and 3) and `h02S` (points 2 and 4).
Blocker destructable `YTpb`. Dummy `h01K` with `A0GW` (death and decay) and
`ANsi` (silence). Timed life `BTLF`: 26.10s for death and decay, 0.10s for
silence. Gather AoE 500.00. Wall ring radius 280.00. Wall angles 45.00, 135.00,
225.00, 315.00. Blocker angles 0.00, 90.00, 180.00, 270.00. Durations by level
6.00 / 6.50 / 7.00. Wall HP by level 400 / 500 / 700. Spell cooldown 300.00s.
Text tag size 9.00, colour 100/100/100, height 25.00. Countdown tick 1.00s.
Silence only at ability level 3. Escapees are relocated to the centre of
`gg_rct_EXILE`; neutral-passive, neutral-aggressive and structure units are
dropped from the group instead.

---

## 5. Behaviour notes and uncertainty

### Intentional deviation — Jaina Ultimate no longer writes the shared temp globals

`Trig_HERO_Jaina_Ulti_Actions` previously stored its points in
`udg_temp_point` and `udg_temp_point_caster` and released them **after three
`TriggerSleepAction` calls totalling four seconds**. Those are shared globals:
any other trigger firing during those four seconds overwrites them, so the two
`RemoveLocation` calls at the end were as likely to free another trigger's
location as their own. That is a pre-existing wrong-free, not just a leak.

The points are now locals, so the function owns exactly what it frees. The
observable consequences:

- The function no longer writes `udg_temp_point` / `udg_temp_point_caster`.
  Verified safe: a scan for functions that *read* either global without first
  assigning it found only `Trig_ITEM_packhorse_pickup_Func007Func003C`, which is
  a condition helper of `Trig_ITEM_packhorse_pickup_Actions` — and that action
  assigns the global itself before evaluating the condition. There is no
  cross-trigger reader depending on a value Jaina left behind.
- The function no longer frees another trigger's location mid-flight. This can
  only improve stability; nothing depended on the old behaviour.

`udg_orb[]` and `udg_X` were **left global on purpose**: the filter function
`Trig_HERO_Jaina_Ulti_Func030003001003` reads `udg_orb[3]`, so localising the
orb array would break the filter. Their existing exposure to overlapping casts
is unchanged by this pass and is called out in the test matrix.

### Guardian Force Field — `udg_Guardian_Point[0]` is no longer written on cast

The cast created a location for the caster position, used it for one
`AngleBetweenPoints` call, and never released it. The angle is now computed from
`GetUnitX`/`GetUnitY` and the location is gone.

Nothing reads `udg_Guardian_Point[0]` between the cast and the loop's own write:
the cast's own wall loop iterates indices 1–6, and
`Trig_Guardian_Force_Field_Damage_Actions` only reaches `udg_Guardian_Point[0]`
on its `else` branch, which requires `udg_Guardian_FF_Level[udg_Guardian_FF_Index] > 6`.
`Guardian_FF_Duration_Per_Lvl` is only defined for levels 1–6, so a level above
6 would already give the field a duration of 0.00 and expire it on the first
tick. **Residual uncertainty:** if a level-7+ force field is ever made
reachable, that branch would read whatever the loop last stored in
`udg_Guardian_Point[0]` rather than the caster position from the most recent
cast. Both are stale reads; neither is correct. Flagged rather than "fixed",
because the correct value there cannot be determined from the script.

### Intentionally untouched — Guardian Force Field cast, `udg_Guardian_Point[1..6]`

The `Trig_Guardian_Force_Field_Cast_Actions` branch that loops indices 1–6 calls
`CPP_Add_Pathing`, `AddSpecialEffectLocBJ` and finally `RemoveLocation` on
`udg_Guardian_Point[1]` through `[6]` — **but nothing in the script ever assigns
those indices in that function**. Index 6 is never assigned anywhere at all. The
block therefore operates on stale locations from the loop (already freed there)
or on null. Ownership cannot be proven, the `RemoveLocation` calls may be double
frees, and any change risks altering pathing-blocker placement. **Left exactly
as found.** This is the single largest unresolved ownership question in the five
systems and is worth a dedicated pass.

### Intentionally untouched — Guardian Force Field per-expiry polar projections

The four `PolarProjectionBJ` calls on the expiry tick are already balanced by
`RemoveLocation` in the wall loops, so they leak nothing. They were not converted
to coordinates because they are consumed by `Trig_Guardian_Force_Field_Damage_Actions`
via `GetUnitsInRangeOfLocAll` and `SetUnitPositionLoc`. Replacing those with
`GroupEnumUnitsInRange` would risk changing enumeration order, which is
observable through damage application order. Preserving enumeration order was
ranked above removing an already-balanced allocation.

### Sinkhole — the reported leak is in unreachable code

The pull loop named in the brief,
`Trig_HERO_Myrmidon_Sinkhole_suck_Func001Func001Func007A`, creates three
locations per enumerated unit (`GetUnitLoc` twice plus `PolarProjectionBJ`) and
frees none. **It is dead code.** The live pull loop is inside
`Trig_HERO_Myrmidon_Sinkhole_suck_Actions` and already uses `GetUnitX`/`GetUnitY`,
`Atan2` and `SetUnitPosition` with the shared `sf_sinkhole_enum_group`.

A whole-file scan shows exactly one occurrence of each of the following — the
definition itself, with no caller and no `ExecuteFunc` string reference (the
script's only seven `ExecuteFunc` calls all name library initialisers):

```
Trig_HERO_Myrmidon_Sinkhole_suck_Func001Func001Func001001002
Trig_HERO_Myrmidon_Sinkhole_suck_Func001Func001Func001A
Trig_HERO_Myrmidon_Sinkhole_suck_Func001Func001Func004002003
Trig_HERO_Myrmidon_Sinkhole_suck_Func001Func001Func007A      <-- the leaky one
Trig_HERO_Myrmidon_Sinkhole_suck_Func001Func001Func009C
Trig_HERO_Myrmidon_Sinkhole_suck_Func001Func001C
Trig_HERO_Myrmidon_Sinkhole_suck_Func001Func001Func009Func001A
Trig_HERO_Myrmidon_Sinkhole_suck_Func001Func001Func009Func005A
Trig_HERO_Myrmidon_Sinkhole_end_Func005A
```

They leak nothing at runtime, so removing them is not required by this pass and
would enlarge the diff for no behavioural gain. **Left in place.** Recommended as
a separate dead-code pass, where deletion can be reviewed on its own merits.

### Prison — wall and blocker array lifecycles (the requested determination)

- **Blocker points** (`udg_prison_block_point_1..4`) do **not** persist. They are
  created, consumed by `CreateDestructableLoc` and the debug text tags, then
  freed and nulled inside the same cast action. No change needed.
- **Wall points** (`udg_prison_wall_point_1..4`) **do** persist between creation
  and delayed cleanup: they survive the cast action and are freed by
  `Trig_HERO_Prison_Wall_countdown_Actions` when that player's
  `udg_prison_timer` drops below 1.00s.
- The gap: a **re-cast by the same player before expiry** overwrote all four
  slots, and the countdown only ever frees what the array currently points at,
  so the previous cast's four locations became unreachable.
- Safe to free on re-cast because every consumer of the previous cast's wall
  points is synchronous within `Trig_HERO_Prison_Actions` — `CreateNUnitsAtLoc`
  and `CreateTextTagLocBJ` — and has long since returned. After the action
  returns, the only remaining reader is the countdown's own `RemoveLocation`.
  Restarting `udg_prison_timer[player]` on the new cast supersedes the old
  countdown anyway.
- The new guard mirrors the countdown's existing null-checked block, so a slot
  is never double freed and slots are nulled after release.
- Different players use different `udg_temp_playernumber` indices, so
  overlapping casts from different players never touch each other's slots.

`Trig_HERO_Prison_Func029A` was reviewed and needed no change: it already uses
`GetRectMinX`/`GetRectMaxX` coordinate arithmetic and creates no handle. It
removes units from `udg_temp_unitgroup`, which is the cast action's own group,
destroyed at the end of that action.

### Throw Glaive — pre-existing behaviour deliberately kept

`DisableTrigger(GetTriggeringTrigger())` on the finishing tick disables the
shared loop trigger for **all** players, not just the one whose glaive landed.
This is a pre-existing defect. It was left untouched because fixing it changes
spell behaviour, which this pass is not allowed to do. Worth a follow-up.

`udg_glaive_location` is now unused. Its declaration was left in the globals
block rather than removed, to keep the diff confined to the leak fix.

---

## 6. In-game test matrix

Sinkhole is included as a regression check only — its live code was not
modified.

| # | Scenario | Systems | Expected |
|---|---|---|---|
| 1 | Cast repeatedly, back to back, at max rate | Glaive, GFF, Jaina, Prison | Identical visuals and timing to v13; no slow drift in frame time over a long game |
| 2 | Re-cast Prison on the same player **before** the previous wall expires | Prison | New wall replaces old; old text tags and blockers still clean up; no orphaned blockers left standing |
| 3 | Two or more players cast Prison simultaneously in different places | Prison | Each wall expires on its own timer; neither player's walls, tags or blockers vanish early |
| 4 | Two players cast Jaina Ultimate within four seconds of each other | Jaina | Known pre-existing `udg_orb[]` / `udg_X` race — record what happens; this pass did not change it |
| 5 | Jaina Ultimate with **no enemy in 512 range** of the lightning orb | Jaina | Third orb issues chain lightning with no target and nothing errors, exactly as before |
| 6 | Guardian Force Field at each level 1–6, letting each expire naturally | GFF | Correct wall count (1/1/3/3/5/5), correct stun/damage placement, blockers removed on expiry |
| 7 | Guardian Force Field detonated early rather than expiring | GFF | Same cleanup path; no leftover pathing blockers |
| 8 | Throw Glaive full outward flight to the 1300.00 abort distance | Glaive | Glaive travels the same distance and speed as v13, then is removed |
| 9 | Throw Glaive return phase — walk the hero so the glaive catches up at 100.00 | Glaive | Return curve tracks the hero identically; glaive disappears on catch |
| 10 | Throw Glaive while the caster dies mid-flight | Glaive | Same behaviour as v13 (path continues toward the dead hero's last position) |
| 11 | Throw Glaive cast by two Sentinel players at once | Glaive | Both glaives fly correctly; confirm the pre-existing shared-trigger disable on first landing behaves as it did in v13 |
| 12 | Prison cast where every gathered unit is a structure or neutral | Prison | Nobody is teleported; walls still build and expire |
| 13 | Prison caster dies immediately after casting | Prison | Walls, tags and blockers still expire on schedule |
| 14 | Spell interrupted / stopped during cast for each of the five | all | No stuck state, no permanent blockers, no permanent dummies |
| 15 | Sinkhole cast, re-cast, and cancelled mid-channel | Sinkhole | Regression check only — unchanged from v13 |
| 16 | Long game (30+ min) with heavy Sentinel and Guardian play | Glaive, GFF | Handle count should now stay flat where it previously climbed |

Test 16 is the one that actually demonstrates the fix; tests 1–15 are the
guard against having changed behaviour while doing it.

---

## 7. Parser result and diff summary

```
tools\bin\JassParseCheck\JassParseCheck.exe src\war3map.j
OK   C:\Users\Ryan1\Documents\Solo Foots Development\src\war3map.j (8,850 top-level declarations)
```

Verification performed:

- **Parser:** OK, 8,850 top-level declarations.
- **Change containment:** all 2,727 function bodies extracted from baseline and
  edited script and compared — exactly the 6 functions in section 1 differ.
  Function count unchanged.
- **Line endings:** 50,469 of 50,469 lines CRLF, matching the baseline's
  50,412 of 50,412. No line-ending damage. (A raw `diff` reports extra hunks on
  this file; those are CRLF resync artifacts — byte comparison of the affected
  lines shows them identical, and `diff --strip-trailing-cr` reports only the
  eight real hunks.)
- **Dangling references:** no remaining use of `udg_glaive_location` outside its
  declaration; no `GetUnitLoc`, `PolarProjectionBJ`, `DistanceBetweenPoints`,
  `AngleBetweenPoints` or `RemoveLocation` left anywhere in the Throw Glaive
  loop path.
- **BJ semantics:** every replaced wrapper was read from the installed
  `Blizzard.j` and confirmed not redefined inside `war3map.j`.

Resulting script SHA256:
`9AAB4E796EBDE41C7F987DE533E11AF73EA6019DDE9EA90C2D5907F679F37280`
(baseline was `1270C497A4535EBA95E122167D70042236A6D9850EB293A4C4057A4E9623A076`).

Content diff: 8 hunks, `+57` net lines.

| Region | Lines | Nature |
|---|---|---|
| globals block | +6 | Two `real array` declarations plus comment |
| Throw Glaive conditions ×2 | +6 | Coordinate distance tests |
| Throw Glaive loop | +2 | Coordinate flight path; one `RemoveLocation` dropped |
| Guardian FF cast | +1 | Coordinate angle; one `GetUnitLoc` dropped |
| Jaina Ultimate | +42 | Locals, per-orb releases, group release, comments |
| Prison cast | +16 | Guarded release of previous wall points, comment |

---

## Files changed

- `src/war3map.j`
- `docs/claude-hero-spell-leak-pass.md` (this file)

No `.w3x` was built or packaged, and no other file was touched.
