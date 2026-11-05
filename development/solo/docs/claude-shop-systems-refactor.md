# Shop Systems Refactor — SoloFoots v1.7

Baseline: `SF_Test1.7_v10`
Scope: `src\war3map.j` only (plus this doc). No map release built.

This refactor consolidates three shop-related subsystems that shared heavily
duplicated generated code:

1. Hero shop page navigation (`Trig_page_system_*`)
2. Four-team shop boundary blocking (`Trig_block_from_shop_t1..t4_*`)
3. Four-team blink-into-shop punishment (`Trig_kill_blink_shop_t1..t4_*`)

Behavior preservation was prioritized over line reduction. Each team keeps its
own `Conditions` and `Init` functions so per-team owner checks, displacement
vectors, warning strings and region registrations remain individually
auditable.

---

## 1. Original behavior catalog

### 1a. Page-system selector → target mappings (verified against baseline)

Order of evaluation preserved exactly (Func004 → Func013):

| # | Selector | Target |
|---|----------|--------|
| 1 | `h02U`   | `n02U` |
| 2 | `h02V`   | `n00R` |
| 3 | `h03P`   | `n03L` |
| 4 | `h03O`   | `n02U` |
| 5 | `h02X`   | `n02V` |
| 6 | `h03S`   | `n03Z` |
| 7 | `h02Y`   | `n02N` |
| 8 | `h03T`   | `n02V` |
| 9 | `h037`   | `n02Z` |
| 10| `h038`   | `n01Y` |

Per matching selector the original action did:
`GetUnitLoc(sold)` → `ClearSelectionForPlayer(owner)` → `RemoveUnit(sold)` →
`GetUnitsInRangeOfLocMatching(512, loc, typefilter)` →
`ForGroupBJ(group, SelectUnitForPlayerSingle)`. Trailing `DestroyGroup`.

Search radius: **512**. Selection basis: unit **type + proximity only** (no
owner restriction in the filter).

### 1b. Boundary-blocking owner checks + displacement vectors

| Team | Enemy-of check | Displacement (dx, dy) |
|------|----------------|-----------------------|
| T1   | `Player(0)`    | `+50, -50` |
| T2   | `Player(4)`    | `-50, -50` |
| T3   | `Player(7)`    | `-50, +50` |
| T4   | `Player(11)`   | `+50, +50` |

Original push: `OffsetLocation(GetUnitLoc(unit), dx, dy)` → `SetUnitPositionLoc`
→ `RemoveLocation`. (The inner `GetUnitLoc` location was leaked.)

### 1c. Boundary region registrations (28 total)

Each team `t{N}` registers `gg_rct_T{N}_SHOP_BLOCK_1 .. _7` (7 × 4 = 28) via
`TriggerRegisterEnterRectSimple`.

### 1d. Blink-kill owner checks + warning strings

| Team | Enemy-of check | Warning string |
|------|----------------|----------------|
| T1   | `Player(0)`    | `TRIGSTR_1109` |
| T2   | `Player(4)`    | `TRIGSTR_2332` |
| T3   | `Player(7)`    | `TRIGSTR_4019` |
| T4   | `Player(11)`   | `TRIGSTR_4495` |

### 1e. Blink-kill region registrations (12 total)

Each team `t{N}` registers `gg_rct_T{N}_SHOP_KILL_1 .. _3` (3 × 4 = 12).

### 1f. Blink punishment operation order + distance

1. `GetTriggerUnit()`
2. `GetUnitLoc(unit)` (caster loc)
3. `AngleBetweenPoints(casterLoc, GetRectCenter(gg_rct_ENTIRE_MAP))` → degrees
4. `PolarProjectionBJ(casterLoc, 350.00, angle)` → destination
5. `SetUnitPositionLoc(unit, dest)`
6. `UnitRemoveItemSwapped(GetItemOfTypeFromUnitBJ(unit,'ankh'), unit)`
7. `KillUnit(unit)`
8. `GetForceOfPlayer(GetTriggerPlayer())` → `DisplayTextToForce(force, warning)`
9. `DestroyForce(force)` → `RemoveLocation(dest)`

Movement distance: **350**. Direction: **toward map center**. Ankh removal
**precedes** `KillUnit`. Warning goes to the **triggering player's** force.
(The caster loc and the `GetRectCenter` loc were both leaked.)

---

## 2. Functions replaced

- Page system: 30 generated helpers removed —
  `Trig_page_system_Func004..Func013` (each: `...Func005002003` filter,
  `...Func006A` select callback, `...C` selector condition) plus the ten
  inline `if/else DoNothing` branches in `Trig_page_system_Actions`.
- Block shop: four 4-line `..._Actions` bodies collapsed to one-line calls.
- Kill blink: four ~11-line `..._Actions` bodies collapsed to one-line calls.

Unchanged and retained per team: every `..._Conditions` and every
`InitTrig_...` (region registrations, event/condition/action wiring).

---

## 3. New helper functions

| Helper | Purpose |
|--------|---------|
| `SF_PageSelectFilter` | Shared enum filter: `GetUnitTypeId(GetFilterUnit()) == sf_page_target_type`. Replaces 10 per-page filters. |
| `SF_PageSelectEnum` | Shared enum callback: `SelectUnitForPlayerSingle(GetEnumUnit(), udg_temp_player)`. Replaces 10 identical callbacks. |
| `SF_PageTargetForSelector` | Selector→target lookup (table of 10 pairs); returns 0 for non-selectors so unrelated sold units skip all page work. |
| `SF_ShopBlockPush` | Shared displacement: `SetUnitPosition(u, GetUnitX(u)+dx, GetUnitY(u)+dy)`. Called with each team's vector. |
| `SF_ShopKillBlinkPunish` | Shared blink punishment (push 350 toward center, strip ankh, kill, warn owning force). Called with each team's warning string. |

---

## 4. New callback-state global

```
integer sf_page_target_type=0
```

Declared adjacent to the existing `sf_` globals. **Why required:** JASS
`boolexpr` filter functions take no arguments, so the shared
`SF_PageSelectFilter` cannot receive the target rawcode as a parameter. It is
passed through this global instead.

**Safety:** the global is set on the line immediately before the synchronous
`GroupEnumUnitsInRange`, which runs the filter and returns before any other
statement executes. The subsystem contains no waits or timers, so no second
page event can interleave between the assignment and the enum. This is the
only new global and the only change outside the three shop code regions.

---

## 5. Handle-ownership analysis

- **Page system.** New `group g` and `boolexpr filt` are created locally,
  used, then `DestroyGroup`/`DestroyBoolExpr` and nulled — fully owned and
  cleaned. The original leaked one `GetUnitLoc` location per navigation (now
  eliminated: coordinate enumeration uses `GetUnitX/Y`, no location created).
  The original also unconditionally `DestroyGroup(udg_temp_unitgroup)` even for
  unrelated sold units, destroying a shared GUI global this subsystem did not
  create on that path; the refactor no longer touches `udg_temp_unitgroup` at
  all, so no foreign handle is destroyed.
- **Block shop.** Coordinate math removed the leaked `GetUnitLoc` location; no
  handle is created, so nothing to clean.
- **Kill blink.** `udg_temp_playergroup` force is created via
  `GetForceOfPlayer` and destroyed after use, exactly as before (kept). The
  two leaked locations (caster loc, `GetRectCenter` loc) are eliminated because
  the angle/projection is now computed from `GetUnitX/Y` and
  `GetRectCenterX/Y` — no `location` handle is created at all. No global
  group/force/trigger owned elsewhere is destroyed.

---

## 6. Behavior-preservation comparison

- **Page navigation.** `GetUnitsInRangeOfLocMatching(512, GetUnitLoc(u), f)`
  is, by BJ definition, `GroupEnumUnitsInRangeOfLoc` on the loc's X/Y, which is
  identical to the native `GroupEnumUnitsInRange(g, GetUnitX(u), GetUnitY(u),
  512, f)`. Radius, type-only filter (no owner restriction added), and
multi-match enumeration behavior (`ForGroup` calls the same single-selection
BJ for every match) is unchanged. This preserves the original result but does
not guarantee that multiple matching units remain selected simultaneously. Order of
  operations preserved: read coords → clear selection → remove sold unit →
  enumerate → select. Unrelated sold units now early-`return` (target 0) and
  perform no selection clear, no removal, no enumeration — matching the
  original, whose per-branch conditions all failed.
- **Block displacement.** `OffsetLocation(GetUnitLoc(u), dx, dy)` followed by
  `SetUnitPositionLoc` yields the same destination as
  `SetUnitPosition(u, GetUnitX(u)+dx, GetUnitY(u)+dy)`. Each team's vector is
  passed literally and unchanged.
- **Blink punishment.** The inline math reproduces
  `AngleBetweenPoints` (`bj_RADTODEG * Atan2(cy-y, cx-x)`) and
  `PolarProjectionBJ` (`+350*Cos(angle*bj_DEGTORAD)`,
  `+350*Sin(angle*bj_DEGTORAD)`) operation-for-operation, including the
  degree↔radian round-trip, so the destination is identical. Ankh removal
  still precedes `KillUnit`; warning string and recipient force
  (`GetTriggerPlayer`) unchanged; death credit / resurrection untouched.

---

## 7. Parser output

```
OK   C:\Users\Ryan1\Documents\Solo Foots Development\src\war3map.j (8,805 top-level declarations)
```

---

## 8. Static registration / mapping counts

| Check | Expected | Found |
|-------|----------|-------|
| Page selector→target pairs | 10 | 10 |
| `SHOP_BLOCK` `TriggerRegisterEnterRectSimple` | 28 | 28 |
| `SHOP_KILL` `TriggerRegisterEnterRectSimple` | 12 | 12 |
| Warning strings (each ×1) | 4 | 4 |
| Team owner slots (0/4/7/11, ×2 = block+kill) | 8 | 8 |
| Page search radius `512.00` | present | present |
| Blink movement `350.00` | present | present |
| Ankh removal precedes `KillUnit` | yes | yes |
| Leftover dead page helpers | 0 | 0 |

---

## 9. Remaining uncertainties

- The refactor deliberately stops touching `udg_temp_unitgroup` in the page
  system. In the baseline, an unrelated sold unit caused a `DestroyGroup` on
  whatever that shared global last held (in practice an already-destroyed
  group from another `SELL`-event trigger — a harmless no-op). Skipping it is
  safer and behavior-equivalent in the realistic case, but a reviewer relying
  on that stale destroy as a side effect should confirm nothing else depends
  on it. No dependency was found.
- Coordinate-vs-location math equivalence is exact in theory; only in-game
  confirmation guarantees no float edge-case differs at map extremes.

---

## 10. Exact in-game test matrix

Page navigation:
1. As each of players in T1–T4, buy every page selector (`h02U`, `h02V`,
   `h03P`, `h03O`, `h02X`, `h03S`, `h02Y`, `h03T`, `h037`, `h038`) and confirm
   the matching target page unit (`n02U`, `n00R`, `n03L`, `n02U`, `n02V`,
   `n03Z`, `n02N`, `n02V`, `n02Z`, `n01Y`) is selected.
2. Confirm the selector unit is removed and prior selection is cleared on each
   purchase.
3. Sell / buy a non-selector unit (e.g. a normal creep) and confirm no
   selection change, no removal, no console error.
4. Place two of the same target-page unit within 512 range and confirm the
   resulting selection matches the v10 baseline. The trigger enumerates both,
   but `SelectUnitForPlayerSingle` may leave only the last enumerated unit selected.

Boundary blocking:
5. Walk an enemy unit into each of the 28 `SHOP_BLOCK` regions (7 per team) and
   confirm it is pushed in the team's direction (T1 +x/-y, T2 -x/-y,
   T3 -x/+y, T4 +x/+y).
6. Walk a friendly (non-enemy) unit into the same regions and confirm no push.

Blink punishment:
7. Blink an enemy unit holding an `ankh` into each of the 12 `SHOP_KILL`
   regions; confirm it is moved ~350 toward map center, loses the ankh, dies
   (does not auto-resurrect), and the correct team warning appears
   (`TRIGSTR_1109/2332/4019/4495`) to the intruder's owner only.
8. Confirm a friendly unit entering the kill regions is unaffected.
