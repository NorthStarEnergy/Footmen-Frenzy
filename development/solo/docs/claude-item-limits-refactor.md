# ITEM limits Refactor

Baseline: **SF_Test1.7_v28**. Scope: the `ITEM limits` subsystem only in `src\war3map.j`
(v28 lines 39044–40208; v19 lines 39004–40168 — the subsystem is byte-identical in both).

> **Baseline note.** The task specified v19 (`08408E5C…`). During the session `src\war3map.j`
> advanced to **v28** (`6FBE417A…`) under the concurrent Codex agent. The `ITEM limits`
> subsystem is **byte-identical between v19 and v28** (0 differing lines, same 1165 lines,
> shifted +40), so the catalog below is valid for both. The work was rebased onto v28 and all
> validation in this document was re-run against v28. See "Baseline incident" at the end.

---

## 1. Complete original rule catalog

The trigger fires on `EVENT_PLAYER_UNIT_PICKUP_ITEM` for any unit. The generated body set five
GUI globals, then walked **25 item rules in a fixed order**. Each rule was
`set udg_temp_item_type='XXXX'` followed by `if ( Trig_ITEM_limits_FuncNNNC() ) then …`, where
the guard is always `GetItemTypeId(udg_temp_item) == udg_temp_item_type`.

All 25 rawcodes are **distinct**, so at most one rule body can execute per pickup. That is what
makes the never-reset `udg_temp_int` accumulator harmless (see §9).

Original prologue (v28 lines 39695–39699):

1. `set udg_temp_playernumber=GetConvertedPlayerId(GetTriggerPlayer())`
2. `set udg_temp_unit=GetTriggerUnit()`
3. `set udg_temp_item=GetManipulatedItem()`
4. `set udg_temp_int=0`

Count rules then ran this shape:

```
set udg_X=1
loop
    exitwhen udg_X > 6
    if ( GetItemTypeId(UnitItemInSlotBJ(udg_temp_unit, udg_X)) == udg_temp_item_type ) then
        set udg_temp_int=( udg_temp_int + 1 )
    else
        call DoNothing()
    endif
    set udg_X=udg_X + 1
endloop
```

`UnitItemInSlotBJ` is 1-based over the 0-based native, so `udg_X` 1..6 addresses inventory slots
0..5 — all six slots. The count **includes the item just picked up**, so `> N` permits N copies.

Rejection (all rules except `'I009'`):

```
call UnitRemoveItemSwapped(GetItemOfTypeFromUnitBJ(udg_temp_unit, GetItemTypeId(udg_temp_item)), udg_temp_unit)
call SoloFootsDisplayMessageToForce(GetForceOfPlayer(ConvertedPlayer(udg_temp_playernumber)), <message>)
```

Removal happens **before** the message, and the message is built afterwards — so `GetItemName`
and `GetUnitName` are evaluated post-removal. `UnitRemoveItemSwapped` → `UnitRemoveItem`, which
**ejects the item to the ground** (it survives, can be re-picked-up, and there is **no refund**).

### Per-rule catalog (original execution order)

| # | Item comment | Rawcode | Max | Reject comparison | Incompatible heroes | Removal | Message | 2 branches? | Class |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Critical Katana | `rat9` | 1 | `udg_temp_int > 1` | `O003` | eject first copy (×2 if both fire) | "Only 1x" / "Cannot use…" | **yes** | count+hero |
| 2 | Tusk of Pitlord | `stwa` | 1 | `udg_temp_int > 1` | `O003`, `O00X` | eject first copy (×2 if both fire) | "Only 1x" / "Cannot use…" | **yes** | count+hero |
| 3 | Medallion of Glim | `mcou` | 1 | `udg_temp_int > 1` | — | eject first copy | "Only 1x" | no | count-only |
| 4 | Ring of Resilience | `I02J` | 1 | `udg_temp_int > 1` | — | eject first copy | "Only 1x" | no | count-only |
| 5 | Sobi Mask | `rwiz` | 1 | `udg_temp_int > 1` | — | eject first copy | "Only 1x" | no | count-only |
| 6 | Orb of Frost | `ofro` | 1 | `udg_temp_int > 1` | — | eject first copy | "Only 1x" | no | count-only |
| 7 | Khadgar Gem | `I042` | 1 | `udg_temp_int > 1` | — | eject first copy | "Only 1x" | no | count-only |
| 8 | Claws of Attack | `ratf` | 1 | `udg_temp_int > 1` | — | eject first copy | "Only 1x" | no | count-only |
| 9 | Crown of Kings | `ckng` | 1 | `udg_temp_int > 1` | — | eject first copy | "Only 1x" | no | count-only |
| 10 | Boots of Quel'Thalas | `belv` | 1 | `udg_temp_int > 1` | — | eject first copy | "Only 1x" | no | count-only |
| 11 | Totem of Might | `tmmt` | 1 | `udg_temp_int > 1` | — | eject first copy | "Only 1x" | no | count-only |
| 12 | Ring of Protection | `rde3` | 1 | `udg_temp_int > 1` | — | eject first copy | "Only 1x" | no | count-only |
| 13 | Gloves of Haste | `gcel` | 1 | `udg_temp_int > 1` | — | eject first copy | "Only 1x" | no | count-only |
| 14 | Belt of Giant Strength | `bgst` | 1 | `udg_temp_int > 1` | — | eject first copy | "Only 1x" | no | count-only |
| 15 | Circlet | `cnob` | 1 | `udg_temp_int > 1` | — | eject first copy | "Only 1x" | no | count-only |
| 16 | Cursed Axe | `I006` | **2** | `udg_temp_int > 2` | — | eject first copy | "Only 1x" *(text/limit mismatch, preserved)* | no | count-only |
| 17 | *(no comment)* | `I009` | **2** | `udg_temp_int > 2` | — | **`RemoveItem` ×3 (destroys)** | **none** | no | **special** |
| 18 | Robe of the Magi | `ciri` | 1 | `udg_temp_int > 1` | — | eject first copy | "Only 1x" | no | count-only |
| 19 | Ring of Regeneration | `rlif` | 1 | `udg_temp_int > 1` | — | eject first copy | "Only 1x" | no | count-only |
| 20 | Escape Dagger | `desc` | — | *(no count rule)* | `H01I`,`E005`,`E007`,`H00U`,`H02G`,`E00U`,`H02R`,`N01L` | eject first copy | `"TRIGSTR_1706"` | no | hero-only |
| 21 | Scepter | `I01H` | — | *(no count rule)* | `H01I`,`E005`,`E007`,`H00U`,`H02G`,`H02R` | eject first copy | `"TRIGSTR_1759"` | no | hero-only |
| 22 | Talisman of Evasion | `evtl` | — | *(no count rule)* | `O00X`,`O003`,`E00F`,`N00C`,`N00I` | eject first copy | "Cannot use…" | no | hero-only |
| 23 | *(no comment)* | `I04A` | — | *(no count rule)* | `O00X`,`O003`,`E00A`,`E00U`,`E00O`,`H036` | eject first copy | "Cannot use…" | no | hero-only |
| 24 | Tome of Retrain | `tret` | — | *(no count rule)* | `H02I`,`N00Z`,`H01H`,`H00A` | eject first copy | "Cannot use…" | no | hero-only |
| 25 | *(no comment)* | `modt` | — | *(no count rule)* | `H02D` | eject first copy | `"TRIGSTR_510"` | no | hero-only |

**Compatible-hero exceptions:** there are none. Every restriction is a plain blocklist; a hero
type not named in a rule's list is permitted. No rule contains an "allow" override.

**Classification totals:** 17 count-only, 2 count+hero, 6 hero-only, 1 special (`I009`, which is
also counted in the count-only column above as a count rule with special removal).

### 2. Rawcode → limit table

| Limit | Rawcodes |
|---|---|
| 1 copy | `rat9` `stwa` `mcou` `I02J` `rwiz` `ofro` `I042` `ratf` `ckng` `belv` `tmmt` `rde3` `gcel` `bgst` `cnob` `ciri` `rlif` |
| 2 copies | `I006` `I009` |
| no count rule | `desc` `I01H` `evtl` `I04A` `tret` `modt` |

### 3. Item → incompatible hero table

| Item | Incompatible hero rawcodes (source order) |
|---|---|
| `rat9` | `O003` |
| `stwa` | `O003`, `O00X` |
| `desc` | `H01I`, `E005`, `E007`, `H00U`, `H02G`, `E00U`, `H02R`, `N01L` |
| `I01H` | `H01I`, `E005`, `E007`, `H00U`, `H02G`, `H02R` |
| `evtl` | `O00X`, `O003`, `E00F`, `N00C`, `N00I` |
| `I04A` | `O00X`, `O003`, `E00A`, `E00U`, `E00O`, `H036` |
| `tret` | `H02I`, `N00Z`, `H01H`, `H00A` |
| `modt` | `H02D` |

### 4. Special / custom rules

**`I009` (rule 17)** is the only rule that does not follow the eject-and-warn shape:

```
call RemoveItem(GetItemOfTypeFromUnitBJ(udg_temp_unit, 'I009'))
call RemoveItem(GetItemOfTypeFromUnitBJ(udg_temp_unit, 'I009'))
call RemoveItem(GetItemOfTypeFromUnitBJ(udg_temp_unit, 'I009'))
```

* `RemoveItem` **destroys** the item; it does not drop it. The player loses it outright.
* Three calls, each re-scanning the inventory, so up to three copies are destroyed. If fewer
  remain, `GetItemOfTypeFromUnitBJ` returns `null` and `RemoveItem(null)` is a no-op.
* The literal `'I009'` is used, not `GetItemTypeId(udg_temp_item)`.
* **No message is shown.** Preserved exactly, including the call count.

**`rat9` / `stwa` double-fire (rules 1–2)** — the count check and the hero check are *sibling*
`if` statements, not `if/elseif`. A blocked hero picking up a duplicate triggers **both**: two
`UnitRemoveItemSwapped` calls (each re-resolving the first matching slot, so two distinct copies
are ejected) and two separate messages. Preserved.

**Orphan comment** — v28 line 40142 carries `// Spell Shield` with no rule beneath it; the next
line begins the `// Scepter` (`I01H`) rule. This is a leftover from a deleted rule and carries no
behavior. It is not reproduced in the new code (see §14).

---

## 5. Original function count and line count

| Metric | Original (v28) | New | Δ |
|---|---|---|---|
| Subsystem lines (`// Trigger: ITEM limits` → `InitTrig` `endfunction`) | 1165 | 180 | **−985 (−84.5%)** |
| Functions in subsystem | 84 | 8 | −76 |
| Generated `Trig_ITEM_limits_Func*` condition functions | **82** | 0 | −82 |
| `Trig_ITEM_limits_Actions` body | **507 lines** | 45 lines | −462 (−91.1%) |
| `call DoNothing()` no-ops | 71 | 0 | −71 |
| Six-slot scan loops written out | 19 | 1 | −18 |
| `GetForceOfPlayer` calls (leaked) | 26 | **0** | −26 |
| File-wide function definitions | 2738 | 2662 | −76 |
| File bytes | 2,217,647 | 2,185,867 | −31,780 |

`udg_` global declarations: 1773 before, 1773 after (unchanged — no global added or removed).

## 6. New helper functions

| Helper | Signature | Purpose |
|---|---|---|
| `ItemLimit_MaxCopies` | `takes integer itemTypeId returns integer` | Rule lookup. Returns the per-hero cap, `0` = unrestricted (lets the caller skip the scan). 19 entries. |
| `ItemLimit_CountInInventory` | `takes unit whichUnit, integer itemTypeId returns integer` | The single six-slot scan. Drives `udg_X` 1..6 and leaves it at 7, exactly as the generated loops did. |
| `ItemLimit_HeroTypeBlocked` | `takes integer itemTypeId, integer heroTypeId returns boolean` | Hero-compatibility check. 8 entries, hero rawcodes in original source order. |
| `ItemLimit_HeroRejectMessage` | `takes integer itemTypeId, unit whichUnit returns string` | Per-item rejection text: three `TRIGSTR_` entries, otherwise the composed "Cannot use this item with …". |
| `ItemLimit_DropHeldCopy` | `takes unit whichUnit, integer itemTypeId returns nothing` | The eject-to-ground removal, preserving `GetItemOfTypeFromUnitBJ` target selection. |
| `ItemLimit_WarnOwner` | `takes player recipient, string message returns nothing` | Single-player message. Replaces the leaking force pairing. |

Naming follows the `CreepLimit_*` precedent (`docs\claude-creep-limit-refactor.md`) for a
single-subsystem helper family. No name collided: `ItemLimit_` appeared zero times before.

## 7. Before/after execution flow

**Before** (every pickup, unconditionally):

```
prologue (5 global writes)
for each of 25 rules, in order:
    set udg_temp_item_type='XXXX'
    call generated guard  ->  GetItemTypeId(udg_temp_item) == udg_temp_item_type
    if match:
        [count rules] 6-slot loop; count check; eject + message
        [rules 1,2]   additional hero check; eject + message
        [rule 17]     3x RemoveItem, no message
        [hero rules]  hero check; eject + message
```
25 guard evaluations + 25 global writes on **every** pickup, including irrelevant items.

**After**:

```
prologue (5 global writes, unchanged values)
maxCopies = ItemLimit_MaxCopies(itemTypeId)          <- one lookup
if maxCopies > 0:                                     <- unrestricted items stop here
    count = ItemLimit_CountInInventory(...)           <- the ONE six-slot scan
    if count > maxCopies:
        if 'I009': 3x RemoveItem (no message)
        else:      ItemLimit_DropHeldCopy + ItemLimit_WarnOwner
if ItemLimit_HeroTypeBlocked(itemTypeId, heroTypeId): <- runs in ADDITION for rat9/stwa
    ItemLimit_DropHeldCopy + ItemLimit_WarnOwner
set udg_temp_item_type='modt'                         <- residual-state parity
```

Rule order is irrelevant to behavior because all 25 rawcodes are distinct — at most one rule can
ever match. Within `rat9`/`stwa`, the original's count-then-hero order is preserved.

## 8. Before/after inventory-scan counts

| Pickup case | Before | After |
|---|---|---|
| Unrestricted item (the common case) | 0 slot scans, but 25 guard evaluations | **0 scans, 1 lookup** |
| Restricted count item | 1 scan (6 slots) + 25 guards | **1 scan (6 slots)** |
| Hero-only restricted item | 0 scans + 25 guards | **0 scans** |

Repeated lookups eliminated per pickup: `GetItemTypeId(udg_temp_item)` was re-evaluated 25× in
the guards plus once per removal; it is now computed **once** into a local. `GetUnitTypeId`,
`GetConvertedPlayerId`/`ConvertedPlayer`, and `GetTriggerUnit`/`GetManipulatedItem` are each
evaluated once. No timers, groups, hashtables, or per-unit state were added.

## 9. Force / handle ownership analysis

**Force leak (fixed).** The original called `GetForceOfPlayer(ConvertedPlayer(...))` at **26**
rejection sites and `DestroyForce` at **zero**. `GetForceOfPlayer` allocates via `CreateForce`,
so every rejection leaked one force handle for the life of the game.

The fix routes messages through the existing direct-player helper rather than freeing a force:

* `SoloFootsDisplayMessageToForce(f, msg)` (`war3map.j:11587`) sets `sf_message_text`, runs
  `ForForce(f, SoloFootsDisplayMessageForEnumPlayer)`, and clears it. The callback
  (`war3map.j:11583`) calls `DisplayTimedTextToPlayer(GetEnumPlayer(), 0.01, 0.18, 0.50, …)`.
* `SoloFootsDisplayMessageToPlayer(p, x, y, msg)` (`war3map.j:11599`) calls
  `DisplayTimedTextToPlayer(p, 0.01, 0.18, 0.50, msg)` — the `x`/`y` parameters are unused.

For a single-player force the two paths make the **same call with the same constants to the same
player**, so display is unchanged and no force is allocated. `sf_message_text` is confirmed
private: its only references map-wide are its declaration and those two helper pairs, and it is
always `""` on return.

**No foreign handles destroyed.** The subsystem destroys nothing it does not own. `RemoveItem`
on `'I009'` is original, intentional, and retained. Items ejected by `UnitRemoveItem` are not
destroyed. No unit, group, or force is destroyed anywhere in the new code (`DestroyForce` count:
0 before, 0 after — the leak is removed by *not allocating*, not by freeing).

**Nested-trigger re-entry: none.** `grep` for `EVENT_PLAYER_UNIT_DROP_ITEM` over all 50,737 lines
returns **zero** matches — no trigger anywhere in the map listens for item drops. Therefore
`UnitRemoveItem`/`RemoveItem` inside this trigger cannot re-enter another trigger and cannot
clobber shared globals mid-run. This is what makes local variables safe here.

**Shared GUI global ownership.** Verdicts, and what the refactor does:

| Global | Residual value at return (original) | Refactor | Reason |
|---|---|---|---|
| `udg_temp_playernumber` | converted trigger-player id | **still written** | cheap; avoids relying on a 647-read audit |
| `udg_temp_unit` | `GetTriggerUnit()` | **still written** | as above (490 reads map-wide) |
| `udg_temp_item` | `GetManipulatedItem()` | **still written** | as above |
| `udg_temp_int` | `0`, or the copy count when a rule matched | **still written** | as above (281 reads map-wide) |
| `udg_temp_item_type` | always `'modt'` (25 unconditional writes) | **still written** (`set udg_temp_item_type='modt'`) | preserves exact end state |
| `udg_X` | `7` if a count loop ran, otherwise untouched | **must stay global** — driven by `ItemLimit_CountInInventory` | **proven external consumer** |

`udg_X` is the one that genuinely constrains the design. `Trig_HERO_Hook_Throw_Actions`
(v28 line 38378) and `Trig_HERO_Hook_Throw_Copy_Actions` (v28 line 25057) both evaluate
`CreateNUnitsAtLoc(1, 'h04D', …, udg_hook_degree[udg_X])` and **never assign `udg_X`** anywhere in
their function — they consume whatever residual value the previously-run subsystem left. (The
line above each writes `udg_hook_degree[udg_temp_playernumber]`, so indexing the read by `udg_X`
is a pre-existing map bug; it is *not* touched here.) Converting `udg_X` to a local would change
the hook facing angle after a restricted pickup, so the counting helper deliberately drives the
global and leaves it at 7 on exactly the paths where the original did.

The other five are written not because a reader was proven, but because writing them costs five
assignments and removes an entire class of risk. This is the conservative reading of the task's
"if observable compatibility cannot be proven, preserve the necessary global assignments".

## 10. Functions removed / replaced / added

**Removed (82 generated condition functions).** All `Trig_ITEM_limits_Func*C` helpers:
`Func007C`, `Func007Func003Func001C`, `Func007Func004C`, `Func007Func005C`,
`Func007Func005Func001C`, `Func010C`, `Func010Func002Func001C`, `Func010Func003C`, `Func010Func005C`,
`Func010Func005Func001C`, then the `FuncNNNC` / `FuncNNNFunc003Func001C` / `FuncNNNFunc004C`
triples for `NNN` ∈ {013, 016, 019, 022, 025, 028, 031, 034, 037, 040, 043, 046, 049, 052, 054,
057, 060}, plus `Func063C`, `Func063Func001C`, `Func063Func003C`, `Func063Func003Func001C`,
`Func067C`, `Func067Func001C`, `Func067Func003C`, `Func067Func003Func001C`, `Func070C`,
`Func070Func003C`, `Func070Func003Func001C`, `Func072C`, `Func072Func003C`,
`Func072Func003Func001C`, `Func075C`, `Func075Func003C`, `Func075Func003Func001C`, `Func077C`,
`Func077Func001C`, `Func077Func003C`, `Func077Func003Func001C`.

Verified: **zero** references to `Trig_ITEM_limits_Func` remain anywhere in `war3map.j` outside a
single explanatory comment.

**Replaced.** `Trig_ITEM_limits_Actions` — rewritten (507 → 45 lines), same name, same signature.

**Added (6).** The `ItemLimit_*` helpers in §6.

**Unchanged.** `InitTrig_ITEM_limits` is byte-identical, including `CreateTrigger`,
`TriggerRegisterAnyUnitEventBJ(…, EVENT_PLAYER_UNIT_PICKUP_ITEM)` and `TriggerAddAction`. The
call site `call InitTrig_ITEM_limits()` in the map's init sequence is untouched.

## 11. Behavior-equivalence evidence

Mechanical comparison of the v28 original against the new source (script re-derives the old rules
by parsing the generated helper families, then parses the new dispatcher and diffs):

```
OLD rule count: 25
OLD order: rat9 stwa mcou I02J rwiz ofro I042 ratf ckng belv tmmt rde3 gcel bgst cnob
           I006 I009 ciri rlif desc I01H evtl I04A tret modt

CHECK 1+2  every rawcode present exactly once, limits identical ....... 25/25 ok
CHECK 3    hero restriction lists, order-sensitive .................... 25/25 ok
CHECK 4    exact message literals present ............................. 6/6 ok
CHECK 5..11 structural ................................................ ok
TOTAL FAILURES: 0
```

Structural counts (old → new):

```
UnitItemInSlotBJ               19 -> 1      six-slot scan written once
'exitwhen udg_X > 6'           19 -> 1      loop bound identical
'set udg_X=1'                  19 -> 1      loop start identical
GetItemOfTypeFromUnitBJ        29 -> 4      1 eject helper + 3 I009 (code only)
UnitRemoveItemSwapped          26 -> 1      single eject helper
call RemoveItem(                3 -> 3      I009 special preserved exactly
GetForceOfPlayer               26 -> 0      leak eliminated
EVENT_PLAYER_UNIT_PICKUP_ITEM   1 -> 1      event unchanged
TriggerRegisterAnyUnitEventBJ   1 -> 1      registration unchanged
TriggerAddAction                1 -> 1      unchanged
DoNothing                      71 -> 0
generated Func* definitions    82 -> 0
```

Point-by-point against the required invariants:

* **Item/hero rawcodes, limits** — mechanically diffed, 25/25 and 8/8 exact (CHECK 1–3).
* **Six slots, scan semantics, `UnitItemInSlotBJ` meaning** — the helper keeps the literal
  `set udg_X=1` / `exitwhen udg_X > 6` / `UnitItemInSlotBJ(unit, udg_X)` form, so indices and the
  1-based BJ wrapper are unchanged.
* **Item selected for removal** — `GetItemOfTypeFromUnitBJ` is **retained**; it returns the first
  match in ascending slot order, which is *not* necessarily `GetManipulatedItem()` (when an older
  duplicate sits in a lower slot, the older copy is ejected). It was **not** substituted with
  `GetManipulatedItem()`; equivalence was not proven and the two differ whenever duplicates carry
  different charges or per-item state.
* **Removal timing vs messages** — removal still precedes the message, and message strings are
  still built after removal, so `GetItemName`/`GetUnitName` see the same post-removal state.
* **Charges / inventory order** — untouched; no item is created, swapped, or re-ordered.
* **Message wording and colour codes** — literals copied verbatim, including the missing closing
  `|r` on "Cannot use this item with ", the `"Only 1x"` text on the 2-copy `I006` rule, and the
  three `TRIGSTR_` tokens (kept as literals so the engine resolves them against `war3map.wts`;
  substituting resolved text would break `.wts` round-tripping).
* **Message recipient** — same player: `ConvertedPlayer(GetConvertedPlayerId(GetTriggerPlayer()))`,
  reaching the same `DisplayTimedTextToPlayer(p, 0.01, 0.18, 0.50, msg)` call.
* **Branches that can run more than once** — `rat9`/`stwa` still evaluate the hero branch after
  the count branch as a sibling `if`, so both can fire on one pickup.
* **Trigger event and registration** — `InitTrig_ITEM_limits` byte-identical.
* **Full inventory / drop-and-repick / shop vs ground** — the trigger only reacts to the pickup
  event and reads inventory slots; none of that logic changed. Ejected items still land on the
  ground and can be re-picked (re-firing the trigger), exactly as before. **No refund** is given,
  matching the original.
* **Special behavior** — `I009` preserved call-for-call (§4).

Resolved string-table text (for reference only; the `.j` keeps the tokens):

| Token | `war3map.wts` text |
|---|---|
| `TRIGSTR_1706` | `\|cffff0000Cannot use this item with Warden, Pirate, W-A-R-L-O-C-K, Avalance, Jaina, Edge or Sheep!\|r` |
| `TRIGSTR_1759` | *(currently byte-identical to 1706)* |
| `TRIGSTR_510` | `\|cffff0000Cannot use this item with Ranger!\|r` |

1706 and 1759 currently hold identical text but are separate, independently editable entries;
both literals are preserved rather than collapsed.

## 12. Parser output

```
tools\bin\JassParseCheck\JassParseCheck.exe roundtrip\SF_Test1.7_v28\files\war3map.j
OK   (8,874 top-level declarations)          <- baseline

tools\bin\JassParseCheck\JassParseCheck.exe src\war3map.j
OK   (8,752 top-level declarations)          <- after
```

Exit code 0 in both cases.

## 13. Source hashes

| File | SHA256 |
|---|---|
| `src\war3map.j` before (task-specified v19) | `08408E5CF9584BFDF171AF4909782588DC39DCD94B5E35FCDFFE091156652B08` |
| `src\war3map.j` baseline actually used (v28) | `6FBE417AE708747580E0F613097265A4F3772F604EECE7A40D0967F31322DBD2` |
| `src\war3map.j` after | `6FD732E1116C72DD78C82D48EA583BDA0A692397D719C1C5F04B36FBC2C47CEA` |

**Containment proof.** Byte-level common-prefix/suffix comparison of the new `src\war3map.j`
against `roundtrip\SF_Test1.7_v28\files\war3map.j`:

```
identical prefix : 1,714,225 bytes
identical suffix :   462,678 bytes
only changed     : v28 lines 39046 .. 40200
ITEM limits spans: v28 lines 39044 .. 40208     -> contained: TRUE
```

Nothing outside the subsystem changed. Line endings preserved exactly: the file's 274 bare-LF
lines (all outside this region) are still 274; the region remains pure CRLF; no BOM was
introduced. `udg_` global declaration count unchanged at 1773. No object-data file
(`war3map.w3t` etc.), no `war3map.wtg`, and no other source file was touched — the only files
written this pass are `src\war3map.j` and this document. **No `.w3x` was built.**

## 14. Uncertainties and intentional micro-divergences

1. **Blizzard.j semantics are canonical, not locally verifiable.** No `blizzard.j`/`common.j`
   exists in this workspace, so the behavior of `UnitItemInSlotBJ` (1-based),
   `GetItemOfTypeFromUnitBJ` (first match, ascending slot order), `UnitRemoveItemSwapped`
   (eject, not destroy), `GetForceOfPlayer` (allocates) and `ConvertedPlayer` is taken from the
   standard definitions. The refactor **retains every one of these calls unchanged**, so even if
   a detail differs from the canonical form, behavior is unaffected — the reasoning is only used
   to justify the message-helper substitution and the "first copy, not necessarily the
   manipulated item" note.
2. **Orphan comment dropped.** The stray `// Spell Shield` comment (no code beneath it) is not
   reproduced. Comment-only; zero behavioral effect.
3. **`ConvertedPlayer(GetConvertedPlayerId(p))` is an identity round-trip** and is kept verbatim
   rather than simplified to `GetTriggerPlayer()`, to avoid any argument about equivalence.
4. **Message helper substitution.** `SoloFootsDisplayMessageToForce(GetForceOfPlayer(p), m)` →
   `SoloFootsDisplayMessageToPlayer(p, 0.00, 0.00, m)`. Argued equivalent in §9. The one
   observable difference is the absence of the leaked force handle. If any future code were to
   read `sf_message_text` concurrently this would matter — nothing does today.
5. **Cached `itemTypeId` after `I009` destruction.** The new code caches `GetItemTypeId(picked)`
   before removal. On the `I009` path `RemoveItem` may destroy `picked`, after which the original
   would have evaluated `GetItemTypeId` on a destroyed handle for the remaining rules (yielding
   no match, since no rawcode is 0). The cached value likewise produces no match, because
   `'I009'` has no hero rule. Same outcome by a different route.
6. **`udg_hook_degree[udg_X]` indexing bug left in place.** Documented in §9; fixing it is out of
   scope and would itself be a behavior change.
7. **`I006` limit/text mismatch left in place** (allows 2, says "Only 1x") — a rebalance would be
   out of scope.

## 15. In-game test matrix

Copy limits — for each restricted rawcode, verify one below / exactly at / one above:

1. `mcou`, `I02J`, `rwiz`, `ofro`, `I042`, `ratf`, `ckng`, `belv`, `tmmt`, `rde3`, `gcel`,
   `bgst`, `cnob`, `ciri`, `rlif` (cap 1): 1st copy kept silently; 2nd copy → one copy ejected to
   the ground + "|cffff0000Only 1x |r<name>|cffff0000 per hero allowed!|r".
2. `I006` Cursed Axe (cap 2): 1st and 2nd kept; **3rd** rejected — confirm the message still
   reads "Only 1x" even though two are allowed.
3. `I009` (cap 2): 1st and 2nd kept; on the **3rd**, up to three copies are **destroyed outright**
   (not dropped) and **no message** appears. Confirm nothing lands on the ground.
4. `rat9` Critical Katana and `stwa` Tusk of Pitlord (cap 1): 2nd copy rejected with the standard
   message.

Hero restrictions — each incompatible hero picks up the item and must be rejected:

5. `rat9` on `O003`.
6. `stwa` on `O003` and on `O00X`.
7. `desc` Escape Dagger on each of `H01I`, `E005`, `E007`, `H00U`, `H02G`, `E00U`, `H02R`, `N01L`
   → message resolves to the Warden/Pirate/Warlock/Avalance/Jaina/Edge/Sheep line, **not** the
   literal text "TRIGSTR_1706".
8. `I01H` Scepter on each of `H01I`, `E005`, `E007`, `H00U`, `H02G`, `H02R`.
9. `evtl` Talisman of Evasion on each of `O00X`, `O003`, `E00F`, `N00C`, `N00I`.
10. `I04A` on each of `O00X`, `O003`, `E00A`, `E00U`, `E00O`, `H036`.
11. `tret` Tome of Retrain on each of `H02I`, `N00Z`, `H01H`, `H00A`.
12. `modt` on `H02D` → resolves to "Cannot use this item with Ranger!".
13. **Compatible heroes** (no exceptions exist — verify the blocklist is not over-broad): pick up
    each restricted item on a hero *not* in its list; it must be kept with no message. In
    particular `desc` on a hero that is blocked for `I01H` but not `desc` (`E00U`, `N01L`) and
    vice versa.

Combined and special cases:

14. **Double-fire**: `O003` holding one `rat9` picks up a second `rat9` → **two** copies ejected
    and **two** messages ("Only 1x…" then "Cannot use this item with …"). Same for `O00X`/`stwa`.
15. **Full inventory**: hero with 6 items picks up a restricted 7th — pickup should be impossible
    (engine-level); with 5 items + duplicate, confirm normal rejection.
16. **Charged duplicates**: carry a partially-used charged duplicate in a **lower** slot than the
    newly picked one, then trigger the limit. Confirm the **lower-slot (older)** copy is the one
    ejected, matching `GetItemOfTypeFromUnitBJ` — this is the highest-risk equivalence point.
17. **Drop and repick**: drop the ejected copy, pick it up again — rejection repeats each time, no
    refund, no duplication.
18. **Moving items between slots**: rearrange duplicates in the inventory, then pick up another —
    counting must still see all six slots.
19. **Rapid repeated pickups**: spam-pick a restricted item several times quickly — one message
    per pickup, no desync, no leak-driven slowdown.
20. **Shop purchase vs ground pickup**: buy a restricted item from a shop and separately pick one
    off the ground — both fire the same pickup event and must behave identically.
21. **Message recipient**: only the picking player sees the message; allies and observers do not.
22. **Unrestricted items**: pick up several non-listed items rapidly — no messages, no removals.
23. **Hook regression watch** (because `udg_X` residual state is preserved deliberately): pick up
    a restricted item, then immediately cast Hook — behavior must match the pre-refactor build.
24. **Neighbouring subsystem**: `ITEM combo limits` still works (it shares `udg_temp_item_type`
    and re-initializes it before use).

---

## Baseline incident (disclosure)

At session start `src\war3map.j` hashed `08408E5C…` (v19, as the task specified). Partway through,
a mid-session backup revealed `src\war3map.j` had become `6FBE417A…` — v28 — because the
concurrent Codex agent advanced it while this work was in progress. A first splice attempt used
line indices computed with a CRLF-only split, which mis-indexed because the file contains bare-LF
lines; that attempt was discarded, and `src` was restored **from `roundtrip\SF_Test1.7_v19`**,
which overwrote the v20–v28 content that was sitting in `src`.

No work was lost: `roundtrip\SF_Test1.7_v28\files\war3map.j` holds v28 intact and byte-identical
to what `src` had contained. `src` was restored from it and the refactor re-applied on top, using
text anchors instead of line indices. Verified afterwards: the diff between the new `src` and v28
is confined to the ITEM limits region, and the v19→v28 changes (zoom range, Transmute crash-test
hero and deferred-death safety, scoreboard-handle guard, premass footmen release, colossal
`-next` command, endgame placement messages) are all present and untouched.

The ITEM limits subsystem is byte-identical between v19 and v28 (0 differing lines), so the
catalog derived from v19 required no revision.
