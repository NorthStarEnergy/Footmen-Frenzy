# Missile Caller Ownership Pass

Behavior-preserving resource-ownership audit of every gameplay caller of
`gg_trg_MissileCreate` and its directly connected callbacks.

- Source of truth: `src\war3map.j` from `SF_Test1.7_v18`
- Scope: caller/callback ownership only. No ability redesign, no MUI conversion,
  no change to the generated missile library.

---

## 0. Discrepancy against the brief (read this first)

The brief states there must remain **exactly 10** calls to
`TriggerExecute(gg_trg_MissileCreate)`.

**The pristine v18 source contains 9, not 10.** This was true before any edit and
is still true after. Verified two ways:

```
grep -n "gg_trg_MissileCreate" src\war3map.j
```

yields exactly three non-caller lines (declaration 2095, `CreateTrigger` 12748,
`TriggerAddAction` 12749) and nine `TriggerExecute` call sites. There is no
alternative launch path: `MissileCreate()` itself is called from exactly one
place, `Trig_MissileCreate_Actions` (line 12743), which is the trigger's own
action.

The nine call sites map one-to-one onto the nine in-scope systems, so the
"10" in the brief appears to be an off-by-one in the task description rather
than a missing caller. **The invariant enforced by this pass is therefore
"exactly 9, unchanged" — the count is identical before and after.** Flagging
for Codex to confirm before packaging.

---

## 1. The 9 missile caller locations

Line numbers are post-change. Pre-change numbers in parentheses where they differ.

| # | System | Function | Line |
|---|--------|----------|------|
| 1 | Searing Bullet | `Trig_Searing_Bullet_Actions` | 25786 |
| 2 | Cripple Wave | `Trig_Cripple_Wave_Actions` | 26628 |
| 3 | Staff of the River | `Trig_Staff_of_the_River_Actions` | 27529 (27525) |
| 4 | Guardian Energy Chamber Ally Cast | `Trig_Guardian_Energy_Chamber_Ally_Cast_Func006Func002A` | 30734 (30726) |
| 5 | Soviet Sniper Decoy Bomb Cast | `Trig_SovietSniper_Decoy_Bomb_Cast_Actions` | 31055 (31047) |
| 6 | Soviet Sniper Golovu Shot Loop | `Trig_SovietSniper_Golovu_Shot_Loop_Func002A` (nested) | 31618 (31610) |
| 7 | Thunder Axe | `Trig_Thunder_Axe_Actions` | 32079 (32071) |
| 8 | Hammer Cast | `Trig_Hammer_Cast_Actions` | 32291 (32283) |
| 9 | Mirror Image Finish | `Trig_Mirror_Image_Finish_Actions` (in loop) | 33195 (33187) |

Directly connected callbacks:

| Caller | Hook | Callback trigger |
|--------|------|------------------|
| Searing Bullet | `udg_Missile_onHit` | `gg_trg_Searing_Bullet_OnHit` |
| Cripple Wave | `udg_Missile_onHit` | `gg_trg_Cripple_Wave_OnHit` |
| Staff of the River | `udg_Missile_onHit` | `gg_trg_Staff_of_the_River_OnHit` |
| Guardian Energy Chamber | *(none set)* | — |
| Decoy Bomb Cast | `udg_Missile_onFinish` | `gg_trg_SovietSniper_Decoy_Bomb_Create_Bomb` |
| Golovu Shot Loop | *(none set)* | — |
| Thunder Axe | `udg_Missile_onHit` | `gg_trg_Axe_OnHit` |
| Hammer Cast | `udg_Missile_onHit` | `gg_trg_Hammer_OnHit` |
| Mirror Image Finish | *(none set)* | — |

---

## 2. Missile and callback ownership contract

### 2.1 Launch time — `MissileCreate` (library, line 6360)

```jass
function MissileCreate takes nothing returns nothing
    local integer missile= s__Missiles_create(GetLocationX(udg_MissileStart), ... )
    if udg_MissileRemoveLocations then
        call RemoveLocation(udg_MissileStart)
        call RemoveLocation(udg_MissileFinish)
    else
        set udg_MissileRemoveLocations=true
    endif
    set udg_MissileStart=null
    set udg_MissileFinish=null
    ...
```

**`udg_MissileStart` and `udg_MissileFinish` are consumed and removed by
`MissileCreate`.**

The `udg_MissileRemoveLocations` gate is a *one-shot opt-out*: a caller could set
it `false` to keep its locations for one launch, after which the flag
self-restores to `true`. Grep proves nothing ever opts out:

```
711 : boolean udg_MissileRemoveLocations= false   (declaration)
6367: set udg_MissileRemoveLocations=true         (self-restore inside MissileCreate)
8817: set udg_MissileRemoveLocations=true         (map init)
```

There is no `= false` assignment anywhere in gameplay code. **The flag is
therefore permanently `true`, and `MissileCreate` unconditionally destroys both
launch locations on every one of the 9 calls.**

Consequences that drove this pass:

- A caller must **not** free `udg_MissileStart` / `udg_MissileFinish` afterwards —
  that is a double removal.
- A caller must **not** hand `MissileCreate` a location it still owns and intends
  to free itself (this is exactly the Mirror Image defect).
- To keep a location, a caller must pass an **owned copy**. The codebase's
  existing idiom for this is `OffsetLocation(p, 0, 0)` — already used at
  line 33188 for `udg_MIC_Point[0]`.

`RemoveLocation(null)` is a safe no-op, so a caller that leaves
`udg_MissileFinish` unset (Guardian Energy Chamber) neither leaks nor double-frees.

### 2.2 Callback time — the dispatcher

`s__Missiles_setup` (line 5731) **creates five fresh locations** before invoking
any callback:

| Global | Created at |
|--------|-----------|
| `udg_MissileStart` | 5733 |
| `udg_MissileFinish` | 5735 |
| `udg_MissilePosition` | 5761 |
| `udg_MissileLastPosition` | 5763 |
| `udg_MissileNextPosition` | 5765 |

`s__Missiles_update` (5826–5834) removes and re-creates the three positional
ones each tick. `s__Missiles_cleanup` (5838–5843) removes **all five** and nulls
them.

**Every one of those five is borrowed by callbacks.** Ability code may read them
freely (`GetLocationX`, `AddSpecialEffectLocBJ`, `CreateNUnitsAtLoc`,
`GetUnitsInRangeOfLocAll`, `SetUnitPositionLocFacingBJ`) but must **never**
`RemoveLocation` them. The dispatcher is the sole owner and sole cleanup point.

Audit result: **no callback in scope releases a borrowed handle.** No change was
needed on this axis, and none was made.

### 2.3 Temporary enumeration groups

Every temporary group in scope is destroyed exactly once:

- `bj_wantDestroyGroup=true` immediately before `ForGroupBJ(GetUnitsInRangeOfLocAll(...))`
  — Searing Bullet OnHit (25867), Cripple Wave OnHit (26705), Staff OnHit (27600),
  Axe OnHit (32195 pre / 32203 post), Hammer OnHit (32409 pre / 32417 post).
  `ForGroupBJ` consumes the flag and destroys the group.
- Explicit `DestroyGroup` — Golovu Shot `udg_SovietSniper_Group[0]` (created 31596,
  destroyed 31647) and `Group[1]` (created/destroyed per loop iteration);
  Mirror Image `udg_MIC_Illusions[0]` (created 33176, destroyed 33204).

**Shared/persistent groups are correctly never destroyed:** `udg_Guardian_EC_Group`,
`udg_SovietSniper_GS_Caster_Group`, `udg_SovietSniper_DB_Bomb_Group`,
`udg_MIC_Illusions[udg_MIC_CV]`, `udg_HU_Group`. `ForGroupBJ` over these is called
without setting `bj_wantDestroyGroup`, which is correct.

### 2.4 Array locations still owned by the ability after launch

Because `MissileCreate` only consumes `udg_MissileStart`/`udg_MissileFinish`, any
`udg_*_Point[]` array slot the ability created remains the ability's own
responsibility:

| Ability | Owned after launch | Freed at |
|---------|-------------------|----------|
| Searing Bullet | `udg_QS_Point[0]`, `[1]` | 25788–25789 |
| Cripple Wave | `udg_QS_Point_Copy[0]`, `[1]` | 26630–26631 **(fixed)** |
| Staff of the River | `udg_Jungle_Point[0]` (27504), `[1]` | 27531–27532 |
| Guardian EC | `udg_Guardian_Point[4]`, `[5]` | 30761 / 30737 |
| Golovu Shot | `udg_SovietSniper_Point[0]`, `[1]` | 31649 / per-iteration |
| Thunder Axe | `udg_NS_Point_Copy[0]`, `[1]` | 32081–32082 |
| Hammer Cast | `udg_NS_Point[0]`, `[1]` | 32293–32294 |
| Mirror Image | `udg_MIC_Point[0]`, `[1..level+1]` | 33203 / 33197 |

---

## 3. Audit verdict per system

| # | System | Verdict | Detail |
|---|--------|---------|--------|
| 1 | **Searing Bullet** | Clean — no change | `MissileStart`/`Finish` correctly left to `MissileCreate`. `QS_Point[0..1]` created 25764–25765, freed 25788–25789. No duplicate cleanup added, per the brief. |
| 1b | **Searing Bullet OnHit** | Clean — no change | Reads borrowed `udg_MissilePosition` only. `bj_wantDestroyGroup` set before `ForGroupBJ`. Dummy has timed life. |
| 2 | **Cripple Wave** | **DEFECT — fixed** | Created `udg_QS_Point_Copy[0..1]` but freed `udg_QS_Point[0..1]`. Wrong-variable cleanup: leaked both `_Copy` locations *and* issued `RemoveLocation` on Searing Bullet's already-freed handles. See §4.1. |
| 2b | **Cripple Wave OnHit** | Clean — no change | Same borrowed-position + `bj_wantDestroyGroup` shape as Searing Bullet OnHit. |
| 3 | **Staff of the River** | **DEFECT — fixed** | `PolarProjectionBJ(GetUnitLoc(GetTriggerUnit()), ...)`: the inner `GetUnitLoc` allocates a location that nothing frees. `PolarProjectionBJ` returns a *new* location and does not consume its argument. One leaked location per cast. See §4.2. |
| 3b | **Staff of the River OnHit** | **DEFECT — fixed** | `GetUnitsInRangeOfLocAll(425.00, GetUnitLoc(udg_MissileSource))`: the group is destroyed via `bj_wantDestroyGroup`, but the nested `GetUnitLoc` leaks. One leaked location per hit. See §4.3. |
| 4 | **Guardian Energy Chamber Ally Cast** | Clean — no change | `Guardian_Point[4]` created 30759 / freed 30761; `Point[5]` created 30713 / freed 30737, both balanced across the enum callback. `MissileStart` consumed by `MissileCreate`. `udg_Guardian_EC_Group` is persistent and correctly not destroyed. See §10 for a noted pre-existing quirk. |
| 5 | **Decoy Bomb Cast** | Clean — no change | `MissileStart` (`GetUnitLoc`) and `MissileFinish` (`GetSpellTargetLoc`) both consumed by `MissileCreate`. Nothing else allocated. |
| 5b | **Decoy Bomb Create Bomb** | Clean — no change | Reads borrowed `udg_MissileFinish` at 31080 and 31091 without releasing it — correct. `SovietSniper_Point[0]` created 31084 / freed 31142; `Point[1]` created and freed around each of the 6 effect placements. |
| 6 | **Golovu Shot Loop** | Clean — no change | `Point[0]` created 31602 / freed 31649. `Point[1]`, `Group[1]` created and released per trail iteration. `Group[0]` created 31604 / destroyed 31655. `MissileStart`/`Finish` consumed. Borrowed per-unit `udg_SovietSniper_GS_Point[cv]` correctly not destroyed here. |
| 7 | **Thunder Axe** | Clean — no change | `NS_Point_Copy[0..1]` created 32057–32058, freed 32081–32082 — correct array, unlike Cripple Wave. No duplicate cleanup added. |
| 7b | **Axe OnHit** | Clean — no change | Borrowed position only; `bj_wantDestroyGroup` set. Empowerment math untouched. |
| 8 | **Hammer Cast** | Clean — no change | `NS_Point[0..1]` created 32256–32257, freed 32293–32294. Empowerment branch (`AHUL` / `AHAM`, `udg_MissileData + 100*level`) untouched. |
| 8b | **Hammer OnHit** | Clean — no change | Borrowed position only; `bj_wantDestroyGroup` set. |
| 9 | **Mirror Image Finish** | **DEFECT — fixed** | Passed the stored `udg_MIC_Point[udg_MIC_Loop]` directly as `udg_MissileFinish`; `MissileCreate` removed it, then line 33189 (pre-change) removed it **again**. Double removal on a freed handle, once per illusion per cast. See §4.4. |

---

## 4. Exact functions changed

Four edits across four functions. Nothing else in the file was touched.

### 4.1 `Trig_Cripple_Wave_Actions` — wrong-variable cleanup

```diff
     call TriggerExecute(gg_trg_MissileCreate)
     //
-    call RemoveLocation(udg_QS_Point[0])
-    call RemoveLocation(udg_QS_Point[1])
+    call RemoveLocation(udg_QS_Point_Copy[0])
+    call RemoveLocation(udg_QS_Point_Copy[1])
 endfunction
```

Why this was a real bug and not just a leak: `udg_QS_Point[0..1]` belong to
Searing Bullet, which already freed them. Cripple Wave was calling
`RemoveLocation` on stale handle IDs. Warcraft III recycles handle IDs, so once
the ID had been reissued to an unrelated location this call would destroy
*that* object instead — a latent cross-system corruption, not merely wasted
memory. The `_Copy` locations it actually owned leaked every cast.

### 4.2 `Trig_Staff_of_the_River_Actions` — location leak in a nested call

```diff
 function Trig_Staff_of_the_River_Actions takes nothing returns nothing
+    local location jungleCastOrigin
     set udg_MonkeyKing=GetTriggerUnit()
...
-    set udg_MissileStart=PolarProjectionBJ(GetUnitLoc(GetTriggerUnit()), 150.00, udg_Jungle_Angle)
+    set jungleCastOrigin=GetUnitLoc(GetTriggerUnit())
+    set udg_MissileStart=PolarProjectionBJ(jungleCastOrigin, 150.00, udg_Jungle_Angle)
+    call RemoveLocation(jungleCastOrigin)
+    set jungleCastOrigin=null
```

`GetTriggerUnit()` is still evaluated at the same point in the same order, and
`PolarProjectionBJ` receives identical coordinates, so `udg_MissileStart` is
byte-for-byte the same position. The local is nulled before return.

### 4.3 `Trig_Staff_of_the_River_OnHit_Actions` — location leak in range enum

```diff
 function Trig_Staff_of_the_River_OnHit_Actions takes nothing returns nothing
+    local location jungleEnumOrigin
     set udg_MissileDestroy=true
...
+    set jungleEnumOrigin=GetUnitLoc(udg_MissileSource)
     set bj_wantDestroyGroup=true
-    call ForGroupBJ(GetUnitsInRangeOfLocAll(425.00, GetUnitLoc(udg_MissileSource)), function Trig_Staff_of_the_River_OnHit_Func009A)
+    call ForGroupBJ(GetUnitsInRangeOfLocAll(425.00, jungleEnumOrigin), function Trig_Staff_of_the_River_OnHit_Func009A)
+    call RemoveLocation(jungleEnumOrigin)
+    set jungleEnumOrigin=null
 endfunction
```

The `GetUnitLoc` is hoisted to *before* `set bj_wantDestroyGroup=true` so that
the flag assignment stays immediately adjacent to `ForGroupBJ` and cannot be
disturbed. `GetUnitLoc` is still evaluated after
`SetUnitPositionLocFacingBJ(udg_MonkeyKing, ...)`, preserving the original
post-teleport enumeration origin and therefore the same healed target set.

### 4.4 `Trig_Mirror_Image_Finish_Actions` — double removal

```diff
             set udg_MissileStart=OffsetLocation(udg_MIC_Point[0], 0, 0)
-            set udg_MissileFinish=udg_MIC_Point[udg_MIC_Loop]
+            set udg_MissileFinish=OffsetLocation(udg_MIC_Point[udg_MIC_Loop], 0, 0)
             ...
             call TriggerExecute(gg_trg_MissileCreate)
             //
             call RemoveLocation(udg_MIC_Point[udg_MIC_Loop])
```

Fixed by matching the author's own idiom on the line directly above: hand
`MissileCreate` an **owned copy**, leaving the array slot's single cleanup point
(`RemoveLocation(udg_MIC_Point[udg_MIC_Loop])`) intact and correct.

The alternative — deleting the trailing `RemoveLocation` — would also have been
correct, but it would leave the array slot holding a dangling handle between
casts. The copy approach keeps "one owner, one cleanup point" true for both the
array slot and the missile's finish location. `OffsetLocation(p, 0, 0)` returns
identical coordinates, so illusion destinations and missile paths are unchanged.
It consumes no random numbers, so the RNG call sequence is untouched.

---

## 5. Before/after allocation and cleanup counts

Per single execution of the named function.

| Function | Locations allocated | Freed before | Freed after | Net leak before | Net leak after |
|----------|--------------------|--------------|-------------|-----------------|----------------|
| `Trig_Cripple_Wave_Actions` | 4 (`QS_Point_Copy[0]`, `[1]`, `MissileStart`, `MissileFinish`) | 2 by `MissileCreate` + 2 **wrong** handles | 2 by `MissileCreate` + 2 correct | **2 leaked, 2 stale frees** | 0 |
| `Trig_Staff_of_the_River_Actions` | 5 (`Jungle_Point[0]`, `[1]`, inner `GetUnitLoc`, `MissileStart`, `MissileFinish`) | 4 | 5 | **1** | 0 |
| `Trig_Staff_of_the_River_OnHit_Actions` | 1 (inner `GetUnitLoc`) + 1 group | 0 loc, 1 group | 1 loc, 1 group | **1** | 0 |
| `Trig_Mirror_Image_Finish_Actions` (per loop iteration) | 2 before / 3 after (`MIC_Point[i]`, `MissileStart` copy, + `MissileFinish` copy) | 3 removals over 2 handles | 3 removals over 3 handles | 0 leaked but **1 double free** | 0 |

Whole-pass totals:

| Metric | Before | After |
|--------|--------|-------|
| Confirmed location leaks per cast (across scope) | 4 | 0 |
| Stale/duplicate `RemoveLocation` calls per cast | 2 (Cripple Wave) + 1 per illusion (Mirror Image) | 0 |
| Temporary groups destroyed | all | all (unchanged) |
| Borrowed dispatcher handles released by ability code | 0 | 0 (unchanged) |
| `TriggerExecute(gg_trg_MissileCreate)` call sites | 9 | 9 |

---

## 6. Handle-ownership table

| Handle | Created by | Owner | Single cleanup point | Notes |
|--------|-----------|-------|---------------------|-------|
| `udg_MissileStart` (launch) | caller | `MissileCreate` | `MissileCreate` 6364 | Consumed unconditionally |
| `udg_MissileFinish` (launch) | caller | `MissileCreate` | `MissileCreate` 6365 | Consumed unconditionally; `null` is safe |
| `udg_MissileStart` (callback) | `s__Missiles_setup` 5733 | dispatcher | `s__Missiles_cleanup` 5839 | **Borrowed** — never free in ability code |
| `udg_MissileFinish` (callback) | `s__Missiles_setup` 5735 | dispatcher | `s__Missiles_cleanup` 5840 | **Borrowed** |
| `udg_MissilePosition` | `s__Missiles_setup` 5761 / `update` 5829 | dispatcher | `update` 5826 / `cleanup` 5841 | **Borrowed** |
| `udg_MissileLastPosition` | `setup` 5763 / `update` 5831 | dispatcher | `update` 5827 / `cleanup` 5842 | **Borrowed** |
| `udg_MissileNextPosition` | `setup` 5765 / `update` 5833 | dispatcher | `update` 5828 / `cleanup` 5843 | **Borrowed** |
| `udg_QS_Point[0..1]` | Searing Bullet 25764 | Searing Bullet | 25788–25789 | |
| `udg_QS_Point_Copy[0..1]` | Cripple Wave 26606 | Cripple Wave | 26630–26631 | **Fixed this pass** |
| `udg_Jungle_Point[0..1]` | Staff cast 27504 | Staff cast | 27531–27532 | |
| `jungleCastOrigin` (local) | Staff cast 27510 | Staff cast | 27512, nulled 27513 | **Added this pass** |
| `jungleEnumOrigin` (local) | Staff OnHit 27598 | Staff OnHit | 27601, nulled 27602 | **Added this pass** |
| `udg_Guardian_Point[4]` | Guardian EC 30759 | Guardian EC | 30761 | |
| `udg_Guardian_Point[5]` | Guardian EC 30713 | Guardian EC | 30737 | |
| `udg_SovietSniper_Point[0]` (bomb) | Create Bomb 31084 | Create Bomb | 31142 | |
| `udg_SovietSniper_Point[1]` (bomb) | Create Bomb, 6 sites | Create Bomb | after each effect | |
| `udg_SovietSniper_Point[0]` (golovu) | Golovu 31602 | Golovu | 31649 | |
| `udg_SovietSniper_Point[1]` (golovu) | Golovu, per iteration | Golovu | per iteration 31644 | |
| `udg_SovietSniper_Group[0]` | Golovu 31604 | Golovu | `DestroyGroup` 31655 | |
| `udg_SovietSniper_Group[1]` | Golovu, per iteration | Golovu | `DestroyGroup` per iteration | |
| `udg_NS_Point_Copy[0..1]` | Thunder Axe 32057 | Thunder Axe | 32081–32082 | |
| `udg_NS_Point[0..1]` | Hammer Cast 32256 | Hammer Cast | 32293–32294 | |
| `udg_MIC_Point[0]` | Mirror Image 33165 | Mirror Image | 33203 | Copied for `MissileStart` |
| `udg_MIC_Point[1..level+1]` | Mirror Image 33171 | Mirror Image | 33197 per iteration | Copied for `MissileFinish` **(fixed this pass)** |
| `udg_MIC_Illusions[0]` | Mirror Image 33176 | Mirror Image | `DestroyGroup` 33204 | |
| `GetUnitsInRangeOfLocAll(...)` groups | BJ call | `ForGroupBJ` | via `bj_wantDestroyGroup` | 5 OnHit sites |
| `udg_Guardian_EC_Group`, `udg_SovietSniper_GS_Caster_Group`, `udg_SovietSniper_DB_Bomb_Group`, `udg_MIC_Illusions[cv]`, `udg_HU_Group` | init / gameplay | **shared, persistent** | never destroyed | Correctly never released |

---

## 7. Preserved constants and behavior

Every value below was verified unchanged by the line-level diff in §9.

| Category | Preserved values |
|----------|-----------------|
| Ability rawcodes | `A0OE`, `A0OF`, `A0Q4`, `S007`, `A0R7`, `AENC`, `ADEC`, `A08W`, `AGSS`, `A0L0`, `A0UF`, `ANSP`, `AHAS`, `AHAM`, `AHUL`, `AMIR`, `AMRD` |
| Unit / buff / misc rawcodes | `dmmy`, `o013`, `umir`, `BTLF`, `BENC`, `B01J` |
| Missile models | Deadly Plumage HD Gold, ArcaneMissileComplete, Scepter of the Tides, ManaFlareTarget, HeroTinkerFactoryMissle, Konstrukt_SniperMissile01, Axe Missile-Small, Storm Bolt, MirrorImageMissile |
| Speeds | 1800, 2200, 1200 (Staff), 1200 (Guardian), 700, 3000, 1175, 1300, 1200 (Mirror) |
| Scales | 0.60, 1.00, 3.00, 1.50, 1.20, 1.10, 2.00, 1.25, 1.00 |
| Collisions | 60, 100, 90, 25, 75, 70 |
| Arcs | 30.00 (Guardian), 40.00 (Decoy), 0.00 (Golovu) |
| Vision | 300.00 (Searing, Cripple, Staff, Axe, Hammer) |
| Start/Finish Z | 90/90, 90/90, 90/90, 90/90, 90/25, 90/90, 90/90, 90/90 |
| Projection distances | 1500, 1300, 150 + 1000, 2000, 1200, 1200, 150 (Mirror) |
| AoE radii | 110 (Searing), 175 (Cripple), 425 (Staff), 180 (Axe), 110 (Hammer), 100 (Golovu trail) |
| Damage tables | `QS_Damage` 150–750; `QS_Damage_Copy` 80–500; `NS_Damage_Copy` 70–375; `NS_Damage` 100–550; `HU_Damage_Per_Lvl`; `SovietSniper_DB_Damage_Per_Lvl` 25–150 |
| Healing | `Jungle_Heal` 80/120/175/225/275/350 |
| Orders | `"thunderbolt"`, `"cripple"`, order id `852274` (Mirror Image) |
| Timed life | 0.20s dummies; 2.00s `AMRD` dummy; `udg_DDE_Duration=2.00` |
| Target filters | All `IsUnitEnemy`/`IsUnitAlly`/`STRUCTURE`/`MECHANICAL`/`MAGIC_IMMUNE`/`IsUnitVisible`/`BlzIsUnitInvulnerable` condition chains byte-identical |
| Callback assignments | All `udg_Missile_onHit` / `udg_Missile_onFinish` assignments unchanged |
| `udg_MissileData` encoding | Unchanged, including Hammer/Axe `level + 100*AHAM` empowerment encoding and the `> 6` / `- 6` decode |
| Hammer empowerment | `AHUL` check, `HU_Group` removal, `B01J` buff removal, `Hammer_Ulti_Loop` disable, travel-distance scaling `* (1 + travelled/1200)` — all unchanged |
| Golovu trail | Spacing `50.00 * i`, count `60 + 5*level`, 100.00 pickup radius, 128.00 muzzle offset — unchanged |
| Mirror Image | `GetRandomDirectionDeg()`, `+90.00` step, 150.00 radius, `GroupPickRandomUnit` selection order — unchanged |
| RNG | No random call added, removed, or reordered. `OffsetLocation` and `GetUnitLoc` consume no randoms. |
| Staff movement/healing | `SetUnitPositionLocFacingBJ(udg_MonkeyKing, udg_MissilePosition, udg_Jungle_Angle)` and heal loop unchanged; enum origin still sampled after the teleport |
| Timing | No timer, period, or trigger registration altered |

Also untouched, as required: end-game tracking, Transmute safety, Thor Powerhit,
KOTH, shops, spawning, camera, Colossals, anti-maphack, object data, and the
entire generated missile library (`s__Missiles_*`, `s__MissileEffect_*`,
`MissileCreate`, `sa__Missiles_*`).

---

## 8. Parser output

```
> tools\bin\JassParseCheck\JassParseCheck.exe src\war3map.j
OK   C:\Users\Ryan1\Documents\Solo Foots Development\src\war3map.j (8,870 top-level declarations)
EXIT=0
```

Top-level declaration count is unchanged from the pristine source (no functions
added or removed; the two new declarations are function-scoped locals).

Call-site invariant:

```
> (Select-String -Path src\war3map.j -Pattern "TriggerExecute\(gg_trg_MissileCreate\)").Count
9
```

Unchanged from the pristine source. See §0.

---

## 9. Source hashes

| State | SHA256 | Bytes |
|-------|--------|-------|
| Before (`SF_Test1.7_v18`) | `2C9A719C2DBDBD74DAE35CB2B2176C27E80063748578A67BB6D398CD47A863C6` | 2,213,998 |
| After | `08408E5CF9584BFDF171AF4909782588DC39DCD94B5E35FCDFFE091156652B08` | 2,214,338 |

Reference copy used to confirm the baseline:
`roundtrip\SF_Test1.7_v18\files\war3map.j` — hashes identically to the stated
expected value.

### Verification that nothing outside the scoped functions changed

A full line-level comparison against the pristine v18 source returns exactly
13 added and 5 removed lines and nothing else:

```
=> [    call RemoveLocation(udg_QS_Point_Copy[0])<CR>]
=> [    call RemoveLocation(udg_QS_Point_Copy[1])<CR>]
=> [    local location jungleCastOrigin<CR>]
=> [    set jungleCastOrigin=GetUnitLoc(GetTriggerUnit())<CR>]
=> [    set udg_MissileStart=PolarProjectionBJ(jungleCastOrigin, 150.00, udg_Jungle_Angle)<CR>]
=> [    call RemoveLocation(jungleCastOrigin)<CR>]
=> [    set jungleCastOrigin=null<CR>]
=> [    local location jungleEnumOrigin<CR>]
=> [    set jungleEnumOrigin=GetUnitLoc(udg_MissileSource)<CR>]
=> [    call ForGroupBJ(GetUnitsInRangeOfLocAll(425.00, jungleEnumOrigin), function Trig_Staff_of_the_River_OnHit_Func009A)<CR>]
=> [    call RemoveLocation(jungleEnumOrigin)<CR>]
=> [    set jungleEnumOrigin=null<CR>]
=> [            set udg_MissileFinish=OffsetLocation(udg_MIC_Point[udg_MIC_Loop], 0, 0)<CR>]
<= [    call RemoveLocation(udg_QS_Point[0])<CR>]
<= [    call RemoveLocation(udg_QS_Point[1])<CR>]
<= [    set udg_MissileStart=PolarProjectionBJ(GetUnitLoc(GetTriggerUnit()), 150.00, udg_Jungle_Angle)<CR>]
<= [    call ForGroupBJ(GetUnitsInRangeOfLocAll(425.00, GetUnitLoc(udg_MissileSource)), function Trig_Staff_of_the_River_OnHit_Func009A)<CR>]
<= [            set udg_MissileFinish=udg_MIC_Point[udg_MIC_Loop]<CR>]
```

### Line-ending note for Codex

The source uses **mixed line endings**: 50,507 CR and 50,660 LF in the pristine
file, i.e. predominantly CRLF with 153 bare-LF lines. All nine inserted lines
were written with CRLF to match their neighbours, and the CR/LF ratio moved
exactly in step (+8 CR, +8 LF for the net +8 lines). Any tooling applied
downstream must preserve this mix — a blanket `dos2unix`/`unix2dos` pass will
silently rewrite ~50k lines and destroy diff reviewability.

---

## 10. Remaining uncertainties

Left unchanged and documented, per the "leave uncertain ownership unchanged" rule.

1. **Guardian Energy Chamber never sets `udg_MissileFinish`.** At line 30713 it
   sets `udg_MissileStart` and `udg_MissileTarget` but no finish location. Since
   `MissileCreate` nulls `udg_MissileFinish` after every launch and
   `s__Missiles_cleanup` nulls it after every callback, the global is `null` at
   this point, so `GetLocationX/Y(null)` yields `0.0` and the missile's impact
   coordinate is **(0, 0)** — the far corner of the map. `RemoveLocation(null)`
   is a safe no-op, so this is *not* a leak or double-free and is out of scope
   for this pass. It is, however, very likely a latent gameplay bug: the ability
   probably intends to home on `udg_Guardian_Unit[5]`. Changing it would alter
   finish coordinates, which the brief forbids. **Recommend a separate ticket.**

2. **Missile homing semantics.** I could not find a code path where
   `s__Missiles_target` causes the missile to track its target unit; movement
   appears to be driven purely by the origin/impact coordinate pair. If the
   library does home on target somewhere I did not locate, uncertainty (1) is
   harmless in practice. This does not affect any change made here.

3. **`udg_QS_Point[0..1]` stale-handle blast radius.** The Cripple Wave fix stops
   *new* stale frees, but I did not audit whether any other system in the map
   reads `udg_QS_Point[]` between a Searing Bullet cast and a Cripple Wave cast.
   Nothing in scope does. Out-of-scope readers were not surveyed.

4. **`udg_MIC_Point[]` array bounds.** Mirror Image writes slots
   `1..udg_MIC_Level+1`. If `AMIR` is ever levelled beyond the array's declared
   size this would fault, but that is pre-existing and unrelated to ownership.

5. **`Trig_Mirror_Image_Create_Illusions_Actions`** (line ~33100) also creates and
   frees `udg_MIC_Point[0]`. It is a different trigger from Mirror Image *Finish*
   and was not in scope, so it was read but not audited in depth. The two
   functions do not overlap in time (Create runs on cast, Finish on summon), but
   they share the same array slot — worth a look in a future pass.

6. **Searing Bullet OnHit dummy leak-adjacent behavior.** `udg_QS_Dummy` is a
   global reassigned on every hit with a 0.20s timed life. Concurrent hits within
   200ms will overwrite the global before the previous dummy expires. The dummy
   still dies on its own timer so nothing leaks, but the `IssueTargetOrderBJ` in
   the enum callback may target the newer dummy. This is an MUI concern, which
   the brief explicitly excludes. Same shape in Cripple Wave, Axe, and Hammer OnHit.

---

## 11. In-game test plan

### 11.1 Per-ability functional tests

For each of the nine systems, confirm damage/heal numbers, model, speed, arc,
AoE, and applied buff match the §7 table.

| # | Ability | Test |
|---|---------|------|
| 1 | Searing Bullet (`A0OE`) | Cast at each of levels 1–6. Confirm 150/250/350/450/550/750 magic damage in a 110 radius and `thunderbolt` (`A0OF`) applied. Gold plumage missile, speed 1800. |
| 2 | Cripple Wave (`A0Q4`) | Levels 1–6 → 80/160/250/300/400/500 in a 175 radius, `cripple` (`S007`) applied. **Regression focus:** cast Searing Bullet, then Cripple Wave, repeatedly and in both orders — the old stale-handle free lived exactly here. |
| 3 | Staff of the River (`A0R7`) | Confirm Monkey King teleports to impact, Culling Slash effect plays, and allies within 425 heal for 80/120/175/225/275/350. Missile spawns 150 units ahead of the caster, travels 1000, speed 1200. |
| 4 | Guardian Energy Chamber (`AENC`) | Ally hero within 800 with ≥50 mana cost and ≥4s cooldown gets mana back; ManaFlare missile fires. **Note the (0,0) destination quirk in §10.1** — record where the missile actually flies so Codex can decide on a follow-up. |
| 5 | Decoy Bomb (`ADEC`) | Bomb lands at the spell target point, 3 TNT barrels + 3 land mines appear around it, flamestrike warning plays for 2s, bomb joins the loop group. |
| 6 | Golovu Shot (`A08W`) | Wind-up → unleash. Confirm rail trail spacing (one impact every 50 units, `60 + 5*level` steps), 100-radius pickup along the line, slow dummy (`AGSS`) at origin. |
| 7 | Thunder Axe (`A0L0`) | Levels 1–6 → 70/110/140/220/275/375 in 180 radius, `A0UF` thunderbolt, distance scaling up to +100% at 1200 travel. |
| 8 | Hammer (`ANSP`) | Levels 1–6 → 100/175/225/275/400/550 in 110 radius, `AHAS`. Then cast `AHAM` ulti and re-cast Hammer: confirm empowered damage adds `HU_Damage_Per_Lvl`, `B01J` buff clears, `AHUL` is removed, and `Hammer_Ulti_Loop` disables when `HU_Group` empties. |
| 9 | Mirror Image (`AMIR`) | See §11.4. |

### 11.2 Repeated and simultaneous casts

- Cast each ability 20+ times back-to-back at max attack speed / zero cooldown;
  watch for handle-count growth or desync.
- Two or more heroes casting the **same** ability at the same instant.
- Two or more heroes casting **different** in-scope abilities within the same
  0.03s missile tick — specifically Searing Bullet + Cripple Wave, and
  Hammer + Thunder Axe (shared `NS_*` globals).
- A Staff of the River missile in flight while a second Staff cast begins.
- Overlapping Golovu Shot channels from two snipers.

### 11.3 Edge cases

| Case | Expectation |
|------|-------------|
| No valid target in AoE | Missile still spawns, travels, expires; no error, no dummy left behind |
| Target dies mid-flight | Missile continues to its impact point; OnHit conditions reject the corpse |
| Caster dies mid-flight | Missile continues; `udg_MissileSource` damage credit degrades gracefully, no crash |
| Caster dies during Golovu wind-up | Channel aborts, caster leaves `GS_Caster_Group`, loop trigger disables when group empties |
| Cast toward a map edge / corner | Finish point clamps or missile hits boundary; `onBoundaries` path does not leak |
| Cast at a cliff / unwalkable tile | Staff teleport resolves to a legal position |
| Target magic-immune / invulnerable / a structure / mechanical | Filtered out per the §7 filters; no damage, no order issued |
| Target in fog | Searing Bullet / Cripple Wave `IsUnitVisible` check rejects |
| Decoy Bomb cast on the map edge | Bomb, barrels, and mines all place; `SovietSniper_Point[1]` freed each time |
| Ability levelled up mid-flight | `udg_MissileData` was captured at launch; damage uses the launch-time level |

### 11.4 Mirror Image — every level

Test `AMIR` at **every** level the map allows (1 through max).

For each level:
- Confirm `level` illusions spawn, all are hidden then shown together.
- Confirm `level + 1` units (caster + illusions) are placed via
  `GroupPickRandomUnit`, each at 150 units from the origin, at
  `GetRandomDirectionDeg()` + `n*90°`.
- Confirm `level + 1` mirror-image missiles fire, one per placed unit.
- Confirm the caster becomes vulnerable, unpauses, and returns to 100% scale.
- **Regression focus (double free):** run 30+ consecutive Mirror Image casts at
  max level. The pre-fix code double-freed one location per illusion per cast, so
  this is the highest-value soak test in the pass. Watch for handle-ID reuse
  symptoms: units teleporting to wrong offsets, missiles flying to (0,0), or
  unrelated abilities misbehaving afterwards.
- Cast Mirror Image, then immediately cast Staff of the River / Searing Bullet,
  to confirm no cross-contamination of recycled handle IDs.

### 11.5 Callback tests

- **onHit** (Searing, Cripple, Staff, Axe, Hammer): confirm `udg_MissileDestroy=true`
  ends the missile, the borrowed `udg_MissilePosition` is readable inside the
  callback, and effects spawn at the true impact point.
- **onFinish** (Decoy Bomb): confirm the bomb spawns at the borrowed
  `udg_MissileFinish` even when the missile expires by duration rather than collision.
- Confirm no callback leaves `bj_wantDestroyGroup` set true on exit (it is
  consumed by `ForGroupBJ` in every scoped path).
- Long-session soak: 30+ minutes with all nine abilities in rotation, monitoring
  handle count for a flat trend.

---

## 12. Files changed

1. `src\war3map.j` — four edits in four functions (§4).
2. `docs\claude-missile-caller-ownership-pass.md` — this document.

No `.w3x` was built or packaged.
