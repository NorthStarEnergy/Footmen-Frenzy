# Item Pipeline Phase 2

Scope: the contiguous item subsystem in `src\war3map.j` from `// Trigger: ITEM combo limits`
through the end of `// Trigger: ITEM Scepter` — 27 triggers.

- Base for this pass: **SF_Test1.7_v30**, `src\war3map.j` = `3856A504…`
- Result: `src\war3map.j` = `DC532AE2…`
- Changed line range: **39453–40840** (was 39453–40912 in v30; net −72 lines)
- Nothing was built, packed, or delivered. See [Build status](#12-build-status).

> **Baseline incident.** The task specified baseline **v29** (`6FD732E1…`). Partway through the
> read pass `src\war3map.j` advanced to **v30** (`3856A504…`) under the concurrent Codex agent,
> which also produced `releases\SF_Test1.7_v30.w3x` and `roundtrip\SF_Test1.7_v30\`. Per the
> workspace rules the older source was **not** restored; this work was rebased onto v30. The
> scoped subsystem is **byte-identical between v29 and v30** — 1460 lines, 0 ordered mismatches,
> shifted +227 — so the catalog below is valid for both. v30's own changes are 13 hunks confined
> to the globals block (~2610), the spectator-camera/zoom block (15845–16171) and the
> anti-maphack tail (49189–49200); they share no globals with this subsystem. Full detail in
> [§11](#11-baseline-incident-detail).

---

## 1. Behavior catalog

All 27 triggers use `TriggerRegisterAnyUnitEventBJ` (any unit, any player). "Loc" = location
allocations vs `RemoveLocation` calls, measured on code lines only.

| # | Trigger (final line) | Event | Condition / rawcode | Key behavior | Loc | Nested-trigger risk |
|---|---|---|---|---|---|---|
| 1 | ITEM combo limits (39453) | PICKUP_ITEM | none (guards inline) | 3 mutual-exclusion rules; 6-slot scan; ejects first held copy per conflicting slot | 0/0 | none — see §4 |
| 2 | ITEM packhorse pickup (39540) | ISSUED_TARGET_ORDER | `GetUnitTypeId == 'hrdh'` | packhorse blocked from tomes/powerups; `RemoveItem` if item within 200 range | 2/2 | none |
| 3 | ITEM packhorse buy (39624) | SELL_ITEM | buying unit **not** hero | 4 rawcodes refunded by `RemoveItem` + `CreateItemLoc` at buyer | 1/1 | **SELL_ITEM** also runs `Turn on Triggers when items sold` |
| 4 | ITEM tomes on lv18 (39708) | PICKUP_ITEM | item `'tkno'` | <18 → `UnitUseItem`; else eject first held copy | 0/0 | **`UnitUseItem` fires USE_ITEM** (3 registrants) |
| 5 | ITEM Thunderfury Staff (39743) | SPELL_EFFECT | `'A0QM'` | enemy → dummy `'A0QN'` purge; ally → `'A0QE'` at ability level | 2/2 | dummy order is async |
| 6 | ITEM Thunderfury Shock Damage (39800) | SPELL_EFFECT | `'A0QN'` | 450 normal damage to spell target | 0/0 | fired *by* #5's dummy |
| 7 | ITEM Scroll of Beast start (39822) | SPELL_EFFECT | `'A0EH'` | 5s cooldown on `'A0EH'` for every allied hero map-wide | 0/0 | none |
| 8 | ITEM Scroll of Invisibility (39860) | SPELL_EFFECT | `'A06E'` | 500 AoE non-enemies → dummy `'A06B'` lvl 2 invisibility | 1/1 | none |
| 9 | ITEM Scroll of Frenzy (39912) | SPELL_EFFECT | `'A0KZ'` | 1000 AoE allies minus structures/dead/magic-immune/mechanical → berserk; consumes `'I02P'` | 1/1 | **`UnitUseItem` on dummy** |
| 10 | ITEM Purge the Dead (40004) | SPELL_EFFECT | `'A0O8'` | 800 AoE dead non-hero non-structure → `RemoveUnit` + overhead effect | 1/1 | none |
| 11 | ITEM Scroll of AntiMagic (40070) | SPELL_EFFECT | `'A07T'` | 400 AoE, **random 26** subgroup → dummy `Aams` | 1/1 | none |
| 12 | ITEM Scroll of Inner Fire (40113) | SPELL_EFFECT | `'A0CM'` | 600 AoE non-enemies → dummy `'A0CN'` innerfire | 1/1 | none |
| 13 | ITEM Rune of Inner Fire (40155) | PICKUP_ITEM | item `'I01J'` | 900 AoE, same dummy body as #12; **does not remove the rune** | 1/1 | none |
| 14 | ITEM Scroll of Illusion (40199) | SPELL_EFFECT | `'A0D8'` | 400 AoE → dummy carries `'I023'`, `UnitUseItemTarget` | 1/1 | **`UnitUseItemTarget` fires USE_ITEM** |
| 15 | ITEM God Wards (40240) | SPELL_EFFECT | `'A0GB'` | `'o002'` ward, 90s `'Bhwd'` timed life | 1/1 | none |
| 16 | ITEM God Wards Copy (40269) | SPELL_EFFECT | `'A0WI'` | identical body to #15 (now shares it) | 1/1 | none |
| 17 | ITEM Interchange (40293) | SPELL_EFFECT | `'A0DA'` | swaps caster/target positions, `CHIM` lightning, 60s timer + matching cooldown | 2/2 | **`PolledWait(1.00)`** suspends mid-action |
| 18 | ITEM Interchange pickup (40336) | PICKUP_ITEM | holds `'I01D'` | re-applies remaining interchange cooldown | 0/0 | none |
| 19 | ITEM Forked Fury NEW (40360) | ATTACKED | attacker is hero | 4-in-16 proc on `'rat6'`, dummy forked lightning, 9s cooldown | 1/1 | none |
| 20 | ITEM Orb of Frost (40447) | ATTACKED | attacked unit has `'B00L'` | dummy `'A06R'` frostnova on the attacked unit | 1/1 | none |
| 21 | ITEM Wall Convert Press (40480) | SPELL_EFFECT | `'A08C'` | builds 3-button per-player dialog | 0/0 | none |
| 22 | ITEM Wall Convert execute (40515) | DialogEvent ×12 | button identity | grants `'tcas'` / `'tgrh'` / `'I01G'` to `udg_herO[]` | 0/0 | none |
| 23 | ITEM Wall (40578) | CONSTRUCT_FINISH | `'h02S'` or `'h02T'` | wall ID 1..20 ring, 40s timed life, timer + floating text | 1/1 | enables #24 |
| 24 | ITEM Wall countdown (40631) | periodic 1.00s | — | updates/destroys the 20 wall text tags; self-disables when idle | 0/0 | none |
| 25 | ITEM Wall taunt (40670) | SPELL_EFFECT | `'A09A'` | 550 AoE enemies ordered to attack caster | 1/1 | none |
| 26 | ITEM Illusion (40736) | SPELL_FINISH | `'AIil'` | if any `'rat6'` held, kills all non-hero units of the caster's type | 0/0 | none |
| 27 | ITEM Scepter (40809) | SPELL_EFFECT | `'A08I'` | dummy `'A08H'` flamestrike, 10s life | 1/1 | none |

### 1.1 ITEM combo limits — full rule detail

Three rules, executed in this fixed order. All three rawcodes are **distinct**, so at most one
rule body runs per pickup.

| # | Item | Rawcode | Conflicts with | Message | Removal |
|---|---|---|---|---|---|
| 1 | Slippers | `rag1` | `hval`, `evtl` | `TRIGSTR_8259` | eject first held `rag1` |
| 2 | Soldiers Mask | `hval` | `rag1`, `evtl` | `TRIGSTR_10260` | eject first held `hval` |
| 3 | Talisman of Evasion | `evtl` | `hval`, `rag1` | `TRIGSTR_10343` | eject first held `evtl` |

Shape of every rule (preserved exactly):

```
set udg_temp_item_type = <T>                 // unconditional, before the guard
if GetItemTypeId(udg_temp_item) == <T> then
    set udg_X = 1
    loop
        exitwhen udg_X > 6                   // UnitItemInSlotBJ is 1-based -> slots 0..5
        if slot(udg_X) is conflictA or conflictB then
            UnitRemoveItemSwapped(GetItemOfTypeFromUnitBJ(udg_temp_unit,
                                  GetItemTypeId(udg_temp_item)), udg_temp_unit)
            <message to the owning player>
        endif
        set udg_X = udg_X + 1
    endloop
endif
```

Four properties that are easy to "optimize" away and were deliberately kept:

1. **The scan does not break on the first conflict.** It tests all six slots and fires a removal
   plus a message for *each* conflicting slot. A hero holding both conflicting types gets
   **two removals and two messages**.
2. **Once held copies run out, `GetItemOfTypeFromUnitBJ` returns null.** `UnitRemoveItem(u, null)`
   is a no-op, so later passes still print their message but remove nothing. This asymmetry is
   observable and preserved.
3. **The removed item is not `GetManipulatedItem()`.** `GetItemOfTypeFromUnitBJ` returns the first
   match in ascending slot order; when an older duplicate sits in a lower slot, that older copy is
   dropped. Duplicates can differ in charges and per-item state, so the original selection is kept
   verbatim — this was an explicit non-goal to "fix".
4. **The item is ejected, not destroyed.** `UnitRemoveItem` drops it to the ground; it survives,
   can be re-picked-up, and there is no gold refund.

### 1.2 Shared GUI globals

| Global | Written by | Read by | Residual after combo limits |
|---|---|---|---|
| `udg_temp_playernumber` | all | many | converted id of the triggering player |
| `udg_temp_unit` | all | many | the picking-up unit |
| `udg_temp_item` | #1 #2 #3 #4, and #14's enum body | #1 #4 | the manipulated item |
| `udg_temp_int` | #1 #26 | #26 | `0` — set and never read by #1, as before |
| `udg_temp_item_type` | **only** `ITEM limits` and `ITEM combo limits` | same two | `'evtl'` (last of the three) |
| `udg_X` | #1 #26 and ~90 other triggers | see below | `7` if a rule fired, otherwise unchanged |
| `udg_temp_point` / `_caster` | most | most | stale handle (matches every sibling trigger) |
| `udg_temp_unitgroup` / `2` | #8–#14 #20 #25 #26 | same | destroyed handle |
| `udg_dummy` | #5 #8 #9 #11–#14 #19 #20 #27 | same | last dummy created |
| `sf_message_text` | message helpers only | message helpers only | **not observable** — see §3.2 |
| `bj_lastRemovedItem` | `UnitRemoveItemSwapped` | nothing in this subsystem | last ejected copy |

**`udg_X` must not become a local.** `Trig_HERO_Hook_Throw_Actions` and its `_Copy` twin index
`udg_hook_degree[udg_X]` without ever assigning `udg_X`, so its residual value is genuinely
observable across triggers. The refactored loop still drives the global 1→7 exactly as before.
This constraint was established in `docs\claude-item-limits-refactor.md` and is unchanged here.

---

## 2. What changed

### 2.1 ITEM combo limits — dispatcher refactor

Nine generated condition helpers plus a 57-line `Actions` body became two helpers plus a 28-line
`Actions` body, reusing two helpers the v29 `ITEM limits` pass already introduced.

**Removed (9):** `Trig_ITEM_combo_limits_Func007C`, `_Func007Func003Func001C`,
`_Func007Func003Func001Func003C`, `_Func010C`, `_Func010Func003Func001C`,
`_Func010Func003Func001Func003C`, `_Func013C`, `_Func013Func003Func001C`,
`_Func013Func003Func001Func003C`.

**Added (2):**

- `ItemCombo_SlotConflicts(firstTypeId, secondTypeId)` — reads slot `udg_X` of `udg_temp_unit`
  once instead of once per rawcode. `GetItemTypeId` and `UnitItemInSlotBJ` are pure queries, so
  collapsing the two reads is equivalent; the original short-circuited on the first match, which
  changes nothing observable.
- `ItemCombo_Enforce(firstTypeId, secondTypeId, message)` — the six-slot scan, removal and message.

**Reused (0 new):** `ItemLimit_DropHeldCopy` and `ItemLimit_WarnOwner`, both defined at line
39386/39395, well before first use here.

`GetItemTypeId(udg_temp_item)` was hoisted into a local for the three guards. Justification: the
three rawcodes are distinct so at most one body runs; no body writes `udg_temp_item`; and nothing
in a body can fire another trigger (§4). The value is therefore provably constant across the three
tests. Inside the loop the call is still re-evaluated per iteration, matching the original.

### 2.2 Leak fixes

| Fix | Sites | Proof |
|---|---|---|
| `SoloFootsDisplayMessageToForce(GetForceOfPlayer(p), m)` → `ItemLimit_WarnOwner(p, m)` | 9 | §3.2 |
| Purge the Dead: second `GetSpellTargetLoc()` → reuse `udg_temp_point` | 1 | §3.3 |
| Forked Fury: added missing `RemoveLocation(udg_temp_point)` | 1 | §3.4 |

Force leaks in region: **9 → 0**. Location allocations **22 → 20** against 20 `RemoveLocation`
calls; every trigger in the subsystem is now individually balanced.

### 2.3 Dead code removed (3)

- `Trig_ITEM_Scroll_of_Beast_start_Func003002002001` / `_Func003002002002` — the GUI emitted these
  alongside the predicate it then inlined via `GetBooleanAnd`; both were unreferenced.
- `Trig_ITEM_Wall_countdown_Func001Func002001` — a `GetForLoopIndexA()` predicate orphaned when
  that body was earlier converted to a local-indexed loop.

Each was confirmed to occur exactly once in the whole file (the definition) before removal.

### 2.4 Consolidations (7 functions removed, 1 added)

- **Enum filter ×5 → 1.** Scroll of Invisibility, Scroll of AntiMagic, Scroll of Inner Fire, Rune
  of Inner Fire and Scroll of Illusion each carried a byte-identical
  `return ( IsUnitEnemy(GetFilterUnit(), udg_temp_player) == false )`. Replaced by
  `ItemScroll_FilterNotEnemy`. The predicate is pure — one global read, one native call, no side
  effects, no ordering dependency — so one definition is equivalent for all five. Each caller still
  builds its own `boolexpr` via `Condition()`, which `GetUnitsInRangeOfLocMatching` destroys, so
  allocation behavior is unchanged.
- **Inner-fire dummy body ×2 → 1.** `Trig_ITEM_Rune_of_Inner_Fire_Func008A` was byte-identical to
  `Trig_ITEM_Scroll_of_Inner_Fire_Func007A` (same dummy type, ability, level, timed life and order,
  same globals in the same sequence). The Rune trigger now calls the Scroll body, which is defined
  earlier in the file.
- **God Wards body ×2 → 1.** `Trig_ITEM_God_Wards_Copy_Actions` was byte-identical to
  `Trig_ITEM_God_Wards_Actions`. Only the *condition* rawcodes differ (`'A0WI'` vs `'A0GB'`), and
  both are untouched. `InitTrig_ITEM_God_Wards_Copy` now registers the shared body.

### 2.5 `DoNothing()` no-ops

24 → 17 within the region, all in `else` branches that the refactor eliminated. `DoNothing` is a
stock no-op native; dropping a call has no observable effect.

### 2.6 Function inventory

| | Region | Whole file |
|---|---|---|
| Before | 138 | 2676 |
| After | 122 | 2660 |

19 removed, 3 added (`ItemCombo_SlotConflicts`, `ItemCombo_Enforce`, `ItemScroll_FilterNotEnemy`).
`function`/`endfunction` balanced at 2660 each.

---

## 3. Equivalence arguments

### 3.1 Combo rules

Verified mechanically, not by eye: `compare-combo-rules.ps1` reconstructs each rule from the v30
generated source (walking `set udg_temp_item_type=…` → `Trig_ITEM_combo_limits_FuncNNNC` →
`…Func003Func001Func003C`) and from the final dispatcher, then compares them field by field.

```
rule 1: item rag1->rag1  conflicts [evtl,hval]->[evtl,hval]  msg TRIGSTR_8259 ->TRIGSTR_8259   scan 1..6->1..6  MATCH
rule 2: item hval->hval  conflicts [evtl,rag1]->[evtl,rag1]  msg TRIGSTR_10260->TRIGSTR_10260  scan 1..6->1..6  MATCH
rule 3: item evtl->evtl  conflicts [hval,rag1]->[hval,rag1]  msg TRIGSTR_10343->TRIGSTR_10343  scan 1..6->1..6  MATCH

rule order preserved                          : True  [rag1>hval>evtl]
udg_temp_item_type assignment order preserved : True
prologue udg_temp_int=0                       : True/True
final residual udg_temp_item_type             : evtl
first-copy removal (not GetManipulatedItem)   : True/True
recipient is the owning player                : True/True
```

### 3.2 Force-message replacement

```
SoloFootsDisplayMessageToForce(GetForceOfPlayer(p), m)
    GetForceOfPlayer -> CreateForce + ForceAddPlayer          (never destroyed = leak)
    -> sf_message_text = m
    -> ForForce(f, SoloFootsDisplayMessageForEnumPlayer)
       -> DisplayTimedTextToPlayer(p, 0.01, 0.18, 0.50, m)
    -> sf_message_text = ""

ItemLimit_WarnOwner(p, m) -> SoloFootsDisplayMessageToPlayer(p, 0, 0, m)
    -> DisplayTimedTextToPlayer(p, 0.01, 0.18, 0.50, m)
```

The force contains exactly one player, so `ForForce` runs the body exactly once with
`GetEnumPlayer() == p`. Both paths bottom out in the same native with the same five arguments; the
on-screen result is identical. The only divergence is the `sf_message_text` residual (`""` vs
unchanged). That global is read in exactly one place —
`SoloFootsDisplayMessageForEnumPlayer` — which is only ever reached from the two `…ToForce`
helpers, and both assign it immediately before calling `ForForce`. The residual is therefore
unobservable. `SoloFootsDisplayMessageToPlayer` ignores its `x`/`y` parameters, matching the 20
existing call sites elsewhere in the script.

### 3.3 Purge the Dead location

`udg_temp_point` is assigned `GetSpellTargetLoc()` on the immediately preceding line; the second
call returned a *different* handle with the *same* coordinates and was never released.
`GroupEnumUnitsInRangeOfLoc` reads only x/y from the location, and nothing between the two lines
can move the spell target. Reusing `udg_temp_point` is therefore equivalent and removes one leaked
location per cast.

### 3.4 Forked Fury location

The generated body allocated `GetUnitLoc(udg_herO[…])` into `udg_temp_point` and never released
it — on an `EVENT_PLAYER_UNIT_ATTACKED` trigger that is one leaked handle per proc. The location's
only consumer is the `CreateNUnitsAtLoc` call, so the release was added at the end of the same
branch, after every existing statement, leaving all ordering intact. The new residual — a stale
handle in `udg_temp_point` — is exactly what all 16 other location-using triggers in this
subsystem already leave behind.

---

## 4. Reentrancy and shared-global audit

**Which item operations can synchronously fire another trigger?**

| Operation | Fires | Registrants in this map |
|---|---|---|
| `UnitRemoveItem` (eject to ground) | DROP_ITEM | **none** — `EVENT_PLAYER_UNIT_DROP_ITEM` is not registered anywhere in the script |
| `UnitUseItem` / `UnitUseItemTarget` | USE_ITEM | **3** — `HERO break loop if tp`, `…_Copy`, `Guardian Energy Chamber Tome Of Retraining` |
| `RemoveItem` after a sale | SELL_ITEM | **2** — `Turn on Triggers when items sold`, `ITEM packhorse buy` |
| item pickup | PICKUP_ITEM | **25** — including 4 in this subsystem |
| `PolledWait` (Interchange) | — | suspends the action; any trigger may run in the gap |

**The combo-limits loop is provably reentrancy-free.** Its only two effects are
`UnitRemoveItem` (no registrant) and `DisplayTimedTextToPlayer` (fires nothing). `udg_temp_item`,
`udg_temp_unit` and `udg_X` therefore cannot be clobbered mid-scan, which is what makes the hoist
in §2.1 sound. This is the reason the hoist was applied *there* and nowhere else.

**Where reentrancy does bite (unchanged, documented only).** Both USE_ITEM hook triggers write
`udg_temp_playernumber`. So `UnitUseItem` in `ITEM tomes on lv18`, and the dummy `UnitUseItem` /
`UnitUseItemTarget` in Scroll of Frenzy and Scroll of Illusion, can overwrite that global
mid-action. None of those three triggers reads `udg_temp_playernumber` after the call, so the
existing behavior is accidentally safe. It is fragile, not broken — nothing was changed.

**Scratch globals that cannot safely be localized:** `udg_X` (read by the Hook triggers without
assignment, §1.2), `udg_temp_item_type` (residual is part of the contract with `ITEM limits`),
`udg_dummy`, `udg_temp_point`, `udg_temp_unitgroup` — all are read by enum/filter callbacks that
take no parameters and can only communicate through globals.

**Scenario coverage.**

- *Rapid pickups* — each pickup is a separate synchronous trigger run; no state survives between
  them except the residuals in §1.2, all preserved.
- *Charged duplicates* — the "first copy in slot order" removal is preserved verbatim; a stacked
  duplicate with different charges is still the one dropped when it sits lower.
- *Shop purchases* — `ITEM packhorse buy` fires on SELL_ITEM alongside
  `Turn on Triggers when items sold`; ordering between them is unchanged (registration order
  untouched).
- *Ground pickups* — identical path to shop pickups for combo limits.
- *Full inventory* — a sixth-slot pickup still scans slots 1..6 and can eject the picked copy
  immediately.
- *Item moved between slots* — changes which copy `GetItemOfTypeFromUnitBJ` returns; preserved,
  because slot order is the selector.
- *Death during item effects* — dummy units carry `'BTLF'` timed life and expire independently of
  the caster; Interchange's `PolledWait` path holds only a `local lightning`, which is safe.
- *Multiplayer ownership* — every message now goes to `ConvertedPlayer(udg_temp_playernumber)` or
  `GetOwningPlayer(unit)`, the same recipient the one-player force resolved to. No message became
  global and no `GetLocalPlayer` path was touched, so there is no desync surface.

---

## 5. Verification results

| Check | Result |
|---|---|
| `JassParseCheck` — v29 stated baseline | **OK** (8,752 top-level declarations) |
| `JassParseCheck` — v30 rebase base | **OK** (8,783) |
| `JassParseCheck` — final `src\war3map.j` | **OK** (8,802) |
| Diff confined to scope | lines 1–39452 byte-identical; entire 9,066-line tail byte-identical |
| Combo rules | 3/3 mechanically MATCH (§3.1) |
| `InitTrig_` definitions, whole file | 479 → 479 |
| `InitTrig_` in region | 27 → 27, each defined once **and** called from an initializer |
| `CreateTrigger` / `TriggerRegister*` / `AddCondition` / `AddAction` in region | 27/38/24/27 → 27/38/24/27 |
| `function` / `endfunction` balance | 2660 / 2660 |

The declaration count rises while functions fall because the parser counts top-level comment
blocks; 45 explanatory comment lines were added.

### 5.1 Leak reductions (region, code lines only)

| | v30 | final |
|---|---|---|
| `GetForceOfPlayer` (one leaked force per message) | **9** | **0** |
| location allocations | 22 | 20 |
| `RemoveLocation` | 20 | 20 |
| per-trigger location balance | 2 unbalanced | **all 17 balanced** |
| group allocations / `DestroyGroup` | 11 / 14 | 11 / 14 |
| `DoNothing()` no-ops | 24 | 17 |

Per-proc impact: Forked Fury leaked a location on **every** hero attack that reached the proc
check, and the nine force sites leaked on every rejection message.

---

## 6. Deliberately unchanged

Each of these is a real defect. None could be shown behavior-preserving to fix, so all were left
alone per the task's standing instruction.

1. **`DestroyGroup` on a group this trigger never created.** `ITEM Scroll of Invisibility` and
   `ITEM Scroll of Inner Fire` both end with `DestroyGroup(udg_temp_unitgroup2)`, which they never
   assign; `ITEM Orb of Frost` ends with `DestroyGroup(udg_temp_unitgroup)`, likewise. They destroy
   whatever another trigger last left there — potentially an already-destroyed handle, whose id may
   since have been recycled to an unrelated group. Removing the calls would *create* a leak and
   change behavior; keeping them preserves it. **This is the highest-risk item in the subsystem and
   wants its own pass.** Orb of Frost is on `EVENT_PLAYER_UNIT_ATTACKED`, so it fires often.
2. **Purge the Dead leaks one effect per killed unit.** `AddSpecialEffectTargetUnitBJ` is never
   destroyed. Adding `DestroyEffect` would trigger the model's death animation immediately, a
   visible change on a unit that is about to be `RemoveUnit`-ed. Not provably equivalent.
3. **Rune of Inner Fire never consumes the rune.** A PICKUP_ITEM trigger with no removal. Looks
   wrong; may well be intentional. Gameplay, not cleanup.
4. **`ITEM packhorse pickup` calls `GetItemLoc` on a possibly-null item.** `GetOrderTargetItem()`
   returns null for unit-target orders. Harmless today; not touched.
5. **`ITEM Scroll of Frenzy` starts a cooldown on `'A07C'` while the trigger keys on `'A0KZ'`.**
   Rawcode mismatch preserved — changing it is a balance decision.
6. **`udg_temp_playernumber` clobbering via USE_ITEM** (§4). Accidentally safe; left as is.
7. **`ITEM Wall` reuses 20 timers by ring index.** A 21st wall inside 40s reuses a live timer and
   its text tag. Preserved.

---

## 7. Remaining risks

- **Untested in-game.** Everything below the parser is static reasoning. No Warcraft III run has
  happened.
- **Multi-branch combo rules** are the subtlest preserved behavior. If a rule ever gains a rawcode
  that overlaps another rule's, the "at most one body runs" premise behind the hoist in §2.1 breaks.
  A comment in the source states this precondition.
- **Cross-trigger helper reuse.** `ITEM combo limits` now depends on `ItemLimit_DropHeldCopy` and
  `ItemLimit_WarnOwner`, and Rune of Inner Fire / God Wards Copy depend on their siblings' bodies.
  Deleting or reordering those triggers now breaks a second one. Definition-before-use order was
  verified for all five links.
- **The stale-`DestroyGroup` trio** (§6.1) remains live.
- **Concurrent-agent drift.** The other agent advanced the source once mid-session and may again.
  Re-hash before any further edit.

---

## 8. Recommended in-game test order

Run in this order — earlier tests establish the invariants later ones depend on.

**A. Combo limits (the refactored rule engine)**

1. Pick up Slippers `rag1` with an empty inventory → kept, no message.
2. Hold Soldiers Mask `hval`, pick up `rag1` → `rag1` ejected to ground, one `TRIGSTR_8259`.
3. Hold Talisman `evtl`, pick up `rag1` → ejected, one message.
4. **Hold both `hval` and `evtl`, pick up `rag1` → expect TWO removals and TWO messages.** This is
   the multi-branch behavior; a single message means the scan wrongly breaks early.
5. Mirror 2–4 for `hval` (expect `TRIGSTR_10260`) and `evtl` (expect `TRIGSTR_10343`).
6. Hold two `rag1` copies with different charges plus a conflicting item; confirm the copy in the
   **lower slot** is the one dropped, not the one just picked up.
7. Rearrange the duplicates between slots and repeat 6 — the dropped copy should follow slot order.
8. Full inventory (6/6), pick up a conflicting item → ejects immediately, no slot corruption.
9. Two players simultaneously trip rules → each sees only their own message.
10. Buy a conflicting item from a shop rather than looting it → same result as 2.
11. Confirm the ejected item is on the ground, re-pickable, and no gold was refunded.
12. Regression on the neighbouring `ITEM limits` trigger (shared helpers): pick up a 2nd
    Claws of Attack `ratf` → "Only 1x" and one ejection.

**B. Force-message sites**

13. Packhorse (`hrdh`) ordered onto a tome → refusal message, horse moves back, tome removed
    within 200 range.
14. Non-hero buys Tome of Power `tkno`, Staff of Teleportation `stel`, Tome of Greater XP `tgxp`,
    `I041` → four distinct messages, item recreated at buyer (except `I041`).
15. Illusion `AIil` while holding `rat6` → `TRIGSTR_1701` to the caster only, illusions die.
16. In every case confirm the message reaches **only** the owning player.

**C. Consolidated bodies**

17. Scroll of Inner Fire `A0CM` (600 AoE) — allies buffed, enemies not.
18. Rune of Inner Fire `I01J` pickup (900 AoE) — same buff; rune is **not** consumed (expected).
19. God Wards `A0GB` and God Wards Copy `A0WI` — both spawn `o002`, both expire at 90s.
20. Scroll of Invisibility, Scroll of AntiMagic, Scroll of Illusion — shared filter still excludes
    enemies only.

**D. Leak-fix sites**

21. Purge the Dead `A0O8` on a field of corpses — heroes and structures survive, others vanish.
22. Forked Fury: attack repeatedly with `rat6` for several minutes; confirm the proc still fires
    ~4/16 with a 9s cooldown and that no slowdown accumulates.

**E. Untouched but adjacent (regression only)**

23. Interchange `A0DA` — positions swap, lightning clears after ~1s, 60s cooldown matches timer.
24. Wall `h02S`/`h02T` — countdown text updates, wall dies at 40s, text tag disappears.
25. Wall taunt, Orb of Frost, Scepter, Thunderfury (enemy and ally targets), Scroll of Frenzy,
    Scroll of Beast cooldown, tomes at level 17 vs 18.
26. Long soak: 20+ minutes of normal play watching for the §6.1 stale-group symptoms — units
    unexpectedly skipped by an AoE scroll.

---

## 9. Hashes

| Artifact | SHA256 |
|---|---|
| `src\war3map.j` — stated baseline (v29) | `6FD732E1116C72DD78C82D48EA583BDA0A692397D719C1C5F04B36FBC2C47CEA` |
| `src\war3map.j` — actual rebase base (v30) | `3856A5045AA14ADEDAF514FE357910137BFC70029D7D2F41F037D04ABE292C54` |
| `src\war3map.j` — **final** | `DC532AE2FE309C804ECE344A80831F369CC09FEE6E2EFFE9A0A3D6B8B8C3593D` |
| `roundtrip\SF_Test1.7_v29\files\war3map.j` | `6FD732E1…` (identical to v29 src) |
| `roundtrip\SF_Test1.7_v30\files\war3map.j` | `3856A504…` (identical to v30 src) |

---

## 10. Files touched

- `src\war3map.j` — lines 39453–40840 only.
- `docs\claude-item-pipeline-phase-2.md` — this file (new).

No object data, release, roundtrip folder, or Warcraft III delivery folder was read for write or
modified.

---

## 11. Baseline incident detail

- **Detected:** a grep mid-analysis returned line numbers ~227 higher than the read that preceded
  it. An immediate re-hash showed `src\war3map.j` = `3856A504…`, not the expected `6FD732E1…`.
- **Cause:** the concurrent Codex agent built `SF_Test1.7_v30` at 17:39–17:40 and updated the
  source in place. `src\war3map.j` was byte-identical to `roundtrip\SF_Test1.7_v30\files\war3map.j`,
  confirming a completed build rather than a partial write.
- **Response:** the older v29 source was **not** restored. All analysis was re-anchored to v30.
- **Impact assessment:** v29 → v30 is +238/−11 lines (net +227) across 13 hunks — globals near
  2610, the spectator-camera/zoom block 15845–16171, and the anti-maphack tail 49189–49200. The new
  globals are `zoom___*`, `SoloCam_*` and `AntiMH_*`; none is read or written by this subsystem.
  The scoped region was compared line-by-line between v29 and v30: **1460 vs 1460 lines, 0 ordered
  mismatches**. The behavior catalog is therefore valid against both.
- **Follow-up:** re-hash immediately before any further edit to this file.

---

## 12. Build status

**Nothing was built or packaged.** No `.w3x` was produced, no release was created, no roundtrip
folder was written, and no Warcraft III delivery folder was touched. The only verification run was
the offline `JassParseCheck` parser against the three script files listed in §5. Producing a
testable map requires the documented build command, which was deliberately **not** run:

```
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\Build-VerifiedMap.ps1 `
    -Version SF_Test1.7_v31 -BaseMap releases\SF_Test1.7_v30.w3x -Deliver
```
