# Thor Powerhit — location leak fix

Date: 2026-07-21
Scope: `src\war3map.j` only (single function body). No object data, no packaging.

## Source hashes

| Stage | SHA256 of `src\war3map.j` |
| --- | --- |
| Before | `3EC5395433963BFE6836526E71A7B35CADCAB1D7845DBF97BDA74F400C987363` |
| After  | `B452FA12445C8AB3F66E143DF9D82F3503AF8A53F149F130F45033166B1665C3` |

Before-hash matches the stated source of truth (SF_Test1.7_v17), verified with
`Get-FileHash -Algorithm SHA256` prior to editing.

## Functions changed

| Function | Change |
| --- | --- |
| `Trig_HERO_Thor_Powerhit_Conditions` | **unchanged** (rawcode `A0ED` intact) |
| `Trig_HERO_Thor_Powerhit_Func009Func005C` | **unchanged** (still reads `udg_temp_point`, still `IsTerrainPathableBJ(..., PATHING_TYPE_WALKABILITY) == true`) |
| `Trig_HERO_Thor_Powerhit_Actions` | **changed** — location ownership moved to locals; every created location released |
| `InitTrig_HERO_Thor_Powerhit` | **unchanged** (same event, same condition, same action) |

Exactly one function body was edited. No other region of `war3map.j` was
touched or reformatted.

## What changed in `Trig_HERO_Thor_Powerhit_Actions`

Three locals were added:

```jass
local location casterPoint=null
local location stepPoint=null
local location nextPoint=null
```

- `casterPoint` owns the caster location (was `udg_temp_point_caster`).
- `stepPoint` owns the current projectile step location (was `udg_temp_point`).
- `nextPoint` is the short-lived handle for the newly projected location, so the
  old one can be released only after the new one exists.

The globals `udg_temp_point_caster` and `udg_temp_point` are still assigned the
same values at the same points in the sequence — they are now *borrowed
references*, not owners. This is required: the pathability condition function
`Trig_HERO_Thor_Powerhit_Func009Func005C` reads `udg_temp_point`, and it was
left byte-for-byte unchanged, so the global must hold the current step location
at the moment the condition is evaluated. It does.

At the end, both locations are released once each (as before) and the borrowed
global references plus the locals are nulled, so nothing downstream can read or
re-release a dead location handle. The original code left both globals pointing
at removed locations; nulling is strictly safer (a stale handle can be
double-freed by an unrelated `RemoveLocation`, or alias a recycled handle id).

## Location-allocation counts

Let `L` = ability level, `N = 30 + 10*L` loop iterations, and `P` = number of
iterations in which the terrain is walkable (`0 <= P <= N`, terrain-dependent).

| | Created | Released | Leaked | Peak live |
| --- | --- | --- | --- | --- |
| Before | `2 + N + P` | `2` | **`N + P`** | `2 + N + P` (monotonic growth) |
| After  | `2 + N + P` | `2 + N + P` | **`0`** | `3` |

Allocation *count and order are identical* — the same `GetUnitLoc`,
`PolarProjectionBJ(+15.00)` and `PolarProjectionBJ(-16.50)` calls happen in the
same sequence with the same arguments. Only the release schedule changed.

Concrete per-cast leak, before → after:

| Level | `N` | Leak, no walkable steps (`P=0`) | Leak, all steps walkable (`P=N`) |
| --- | --- | --- | --- |
| 1 | 40 | 40 → **0** | 80 → **0** |
| 2 | 50 | 50 → **0** | 100 → **0** |
| 3 | 60 | 60 → **0** | 120 → **0** |
| 4 | 70 | 70 → **0** | 140 → **0** |
| 5 | 80 | 80 → **0** | 160 → **0** |
| 6 | 90 | 90 → **0** | 180 → **0** |

## Handle-ownership analysis

| Handle | Created by | Owner after fix | Released by | Notes |
| --- | --- | --- | --- | --- |
| caster location | `GetUnitLoc(udg_temp_unit)` | `casterPoint` (local) | `RemoveLocation(casterPoint)` at end | created here, so ownership is proven |
| initial target location | `GetUnitLoc(udg_temp_target)` | `stepPoint` (local) | first loop iteration, after its successor exists | created here |
| forward step location (`+15.00`) | `PolarProjectionBJ` | `nextPoint` → `stepPoint` | next projection, or the final `RemoveLocation(stepPoint)` | `PolarProjectionBJ` returns a fresh `Location`; caller owns it |
| pull-back location (`-16.50`) | `PolarProjectionBJ` | `nextPoint` → `stepPoint` | same as above | only allocated on the walkable branch, exactly as before |
| `udg_temp_point`, `udg_temp_point_caster` | — | **borrowed only** | never released via the global | nulled at exit |
| `bj_lastCreatedEffect` (FlakTarget) | `AddSpecialEffectLocBJ` | BJ global | `DestroyEffectBJ(GetLastCreatedEffectBJ())` — **unchanged** | left exactly as-is |
| `udg_temp_unit`, `udg_temp_target`, `udg_temp_player` | events/natives | not owned here | not destroyed | units/players are not this trigger's to free |
| `gg_trg_HERO_Thor_Powerhit` | `CreateTrigger` in init | map-lifetime | never | untouched |

No shared GUI handle is destroyed. The only handles freed are the four location
kinds this function itself allocates. Group/unit/effect ownership is unchanged.

Loop invariant: at the top of every iteration exactly one live step location is
held (`stepPoint`), plus `casterPoint`. `nextPoint` is non-null only between the
`PolarProjectionBJ` call and the immediately following `RemoveLocation` +
reassign, so no location is ever released while still referenced, and no
location is released twice.

## Proof that constants and operation order are unchanged

Requirement-by-requirement, against the original text:

1. **Rawcode** — `Trig_HERO_Thor_Powerhit_Conditions` still returns false unless
   `GetSpellAbilityId() == 'A0ED'`. Function not edited.
2. **Target-unit spell behavior** — `GetTriggerUnit()` / `GetSpellTargetUnit()` /
   `GetOwningPlayer` / `GetConvertedPlayerId` assignments are the same four
   statements, in the same order, to the same globals.
3. **Loop count** — literally `exitwhen udg_X > ( 30 + ( 10 * udg_abilitylevel ) )`,
   with `udg_abilitylevel` still from
   `GetUnitAbilityLevelSwapped(GetSpellAbilityId(), udg_temp_unit)`, `udg_X`
   still initialised to 1 and incremented by 1 at the end of the body.
4. **15.00 forward step** — `PolarProjectionBJ(stepPoint, 15.00, udg_temp_degree)`;
   `stepPoint` holds precisely the location `udg_temp_point` held at that point
   in the original.
5. **-16.50 and pathability** — the `if ( Trig_HERO_Thor_Powerhit_Func009Func005C() ) then`
   / `else call DoNothing()` structure is intact, the condition function is
   unedited, and it is still evaluated *after* the unit has been moved and the
   effect created — i.e. against the post-step `udg_temp_point`, exactly as
   before. The branch body still projects by `- 16.50` at `udg_temp_degree`.
6. **Angle, facing, positioning native, effect** — `udg_temp_degree` still comes
   from `AngleBetweenPoints(udg_temp_point_caster, udg_temp_point)` computed from
   the caster and initial target locations before the loop;
   `SetUnitPositionLocFacingBJ(udg_temp_target, udg_temp_point, udg_temp_degree)`
   is the same native call with the same arguments (collision/pathing behavior of
   `SetUnitPositionLoc` therefore identical); the effect path is still
   `"Abilities\\Spells\\Human\\FlakCannons\\FlakTarget.mdl"` created with
   `AddSpecialEffectLocBJ` and destroyed with
   `DestroyEffectBJ(GetLastCreatedEffectBJ())`.
7. **Damage / stun / targeting / ownership / balance** — this function contains
   no damage, stun or ownership code, and none was added or removed.
8. **Leaks** — see the table above: 0 leaked locations.
9. **Locals** — three locals added, all released and nulled before return.
10. **Shared GUI handles** — none destroyed; see ownership table.
11. **Unrelated systems** — Transmute, inactive-player removal, KOTH, shops,
    spawning, Colossals, camera, anti-maphack and all other hero abilities are
    outside the edited function and were not modified.
12. **No reformatting** — the diff is confined to one function body.

Statement-order diff (executable statements only, ignoring the added
`RemoveLocation`/null bookkeeping): identical sequence. Every added statement is
either a `RemoveLocation` of a location that is already unreachable by the
original code, or a `set ... = null`.

## Parser output

```
> tools\bin\JassParseCheck\JassParseCheck.exe src\war3map.j
OK   C:\Users\Ryan1\Documents\Solo Foots Development\src\war3map.j (8,860 top-level declarations)
```

Exit code `0`.

## In-game test matrix

Not executed here (no build/packaging was performed, per instructions). Run
after Codex packages the `.w3x`.

| # | Case | Setup | Expected |
| --- | --- | --- | --- |
| 1 | Level 1, open terrain | Thor lvl-1 Powerhit on a footman in open field | Target slides 40 steps forward, FlakTarget puffs along the path, same total distance as v17 |
| 2 | Level 6, open terrain | Max-level Powerhit, open field | 90 steps, visibly ~2.25x the level-1 distance; no stutter |
| 3 | Level 1, blocked terrain | Cast into cliff/tree wall | Target stops against the blocker exactly as in v17; effects still spawn along attempted path |
| 4 | Level 6, blocked terrain | Max level into a building/cliff | Same stop behavior as v17; no unit displaced through pathing |
| 5 | Level 6, toward map edge | Cast so the path runs off the playable area | Target clamps at the boundary; no crash, no desync |
| 6 | Walkable/unwalkable mix | Cast across a shoreline or bridge seam | `-16.50` pull-back triggers on the walkable segments only; final resting spot matches v17 |
| 7 | Target dies mid-cast | Kill the target during the slide (or cast on a near-dead unit) | No crash; loop completes; no lingering effects |
| 8 | Caster dies mid-cast | Kill Thor immediately after the spell effect fires | Slide completes as in v17; no crash |
| 9 | Rapid repeated casts | 20+ back-to-back casts, several Thors if possible | Memory/handle count stable; no progressive frame-time growth (this is the regression the fix targets) |
| 10 | Multiplayer sanity | Two players, simultaneous casts | No desync; both slides resolve identically on both clients |
| 11 | Cross-system sanity | Cast during KOTH capture, near shops, near Colossals | Unrelated systems unaffected; `udg_temp_point` consumers elsewhere behave normally |

Regression watch for #9: before the fix each cast leaked 40–180 location
handles; a hundred casts leaked up to 18,000. Post-fix the live handle count
should return to baseline after each cast.

## Changed files

- `src\war3map.j`
- `docs\claude-thor-powerhit-leak-fix.md`
