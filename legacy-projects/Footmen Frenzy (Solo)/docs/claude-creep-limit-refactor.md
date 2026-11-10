# Creep Purchase Limit Refactor

Baseline: SF_Test1.7_v9. Scope: `Trig_limit_amount_of_creeps_*` subsystem only in `src\war3map.j` (previously ~lines 21898–22169).

## Original rule catalog

The trigger fired on `EVENT_PLAYER_UNIT_SELL` (every unit sale, all shops). Rejection condition was a flat OR-chain of 15 generated functions, each testing `GetUnitTypeId(udg_temp_unit) == <rawcode> and udg_temp_int > <N>`. Since every rawcode is distinct, decision order never mattered — exactly one rule can match a given purchase.

| # | Rawcode | Original condition | Effective max per team |
|---|---------|--------------------|------------------------|
| 1 | `n005` | count > 2 | 2 |
| 2 | `n00T` | count > 2 | 2 |
| 3 | `o00H` | count > 2 | 2 |
| 4 | `n011` | count > 1 | 1 |
| 5 | `n006` | count > 4 | 4 |
| 6 | `o00K` | count > 1 | 1 |
| 7 | `n00Q` | count > 2 | 2 |
| 8 | `nws1` | count > 1 | 1 |
| 9 | `n033` | count > 1 | 1 |
| 10 | `nftr` | count > 2 | 2 |
| 11 | `n03M` | count > 1 | 1 |
| 12 | `uobs` | count > 1 | 1 |
| 13 | `h03B` | count > 3 | 3 |
| 14 | `ushd` | count > 1 | 1 |
| 15 | `n00U` | count > 1 | 1 |

Count semantics (original): enumerate ALL units in the playable map whose type equals the sold unit's type and that are allies of the buying player (`IsUnitAlly` — includes the buyer's own units), then remove dead units (`IsUnitDeadBJ`) from the group, then count. The just-sold unit is alive and owned by the buyer at event time, so it is included in the count.

Original action sequence:
1. `udg_temp_unit = GetSoldUnit()`
2. `udg_creep_gold_cost = BlzGetUnitIntegerField(sold, UNIT_IF_LUMBER_BOUNTY_AWARDED_BASE)` (gold cost is smuggled through the lumber-bounty field), then the field is zeroed
3. Debug mode: display "Creep Gold Cost: N" to the buyer
4. Full-map enumeration into `udg_creep`, dead removal, `udg_temp_int = count`
5. `udg_temp_playergroup = GetForceOfPlayer(buyer)`
6. If any rule matched: `RemoveUnit(sold)`, message `"Sorry, only (count-1) <name> allowed per team! - you have been refundend <cost> Gold."`, `AdjustPlayerStateBJ(cost, buyer, GOLD)`
7. `GroupClear(udg_creep)`; `DestroyForce(udg_temp_playergroup)`; `DestroyGroup(udg_temp_unitgroup)`

## Implementation summary

Replaced 19 generated functions with 3 named functions plus the rewritten Actions:

- `CreepLimit_MaxAllowed(unitTypeId)` — table-driven if/elseif lookup returning the per-team cap, `0` = unrestricted. All 15 rawcodes and limits transcribed 1:1 from the table above.
- `CreepLimit_CountFilter()` — single filter: same type as sold unit AND ally of buyer AND not dead. (Folds the original's post-enumeration dead-removal pass into the filter — same resulting count.)
- `CreepLimit_CountLivingTeamCopies()` — enumerates the playable map into a **local** group, counts, destroys group and boolexpr (mirrors the `GetUnitsInRectMatching` BJ's own boolexpr cleanup).
- `Trig_limit_amount_of_creeps_Actions` — reads cost, zeroes the lumber-bounty field, does the debug print, then looks up the cap **first** and only enumerates when the sold type is actually restricted. Rejection path (remove → message → refund, in that order) is byte-identical text and identical call order.

Full-map scan reduction: for the overwhelmingly common case (unrestricted unit sold), no enumeration happens at all. For restricted types, one enumeration still runs (per the safety rule: no persistent counters were introduced, since deaths/removals/ownership changes are not all hooked in this subsystem). The dead-removal `ForGroup` pass and the second full group walk (`CountUnitsInGroup` after removal) are gone.

Handle-cleanup fixes (all local to this trigger):
- **Group leak fixed**: original created a fresh group every sale via `GetUnitsInRectMatching` into `udg_creep` but only ever called `GroupClear`, never `DestroyGroup` — one leaked group handle per purchase. Now a local group is created and destroyed per (restricted) purchase. The `udg_creep` global remains declared/initialized but is no longer written by this trigger (it was referenced nowhere else).
- **Force leak fixed**: debug print used an inline `GetForceOfPlayer(...)` whose force was never destroyed. Now held in a local and destroyed.
- **Foreign destroy removed**: `call DestroyGroup(udg_temp_unitgroup)` destroyed a global group this trigger never sets (it belongs to other triggers, which destroy it themselves). Removed. Since every other writer of `udg_temp_unitgroup` destroys it after use, this line was a no-op on an already-destroyed handle in practice.

## Behavior-preservation notes

- Limits, rawcodes, and the `>` comparisons are unchanged (see table).
- Team counting: same predicate (`IsUnitAlly(unit, buyer)` over the playable map, alive only, sold unit included).
- Rejection: `RemoveUnit` still happens **before** the message (so `GetUnitName` is called on the just-removed unit, exactly as before), message string is unchanged including the "refundend" typo and the `count-1` arithmetic, and the refund amount is exactly the value read from the lumber-bounty field at sale time.
- Debug cost print: unchanged text, still shown to the buyer on every sale when `udg_mode_debugmode` is true, still printed before any limit logic.
- Lumber-bounty field is still zeroed on **every** sold unit (restricted or not) — this side effect matters to bounty behavior and is preserved unconditionally.
- `udg_temp_playergroup` is still created and destroyed on every sale (not just rejections) to keep the global's end-of-trigger state identical to baseline (one other trigger, autorevive at line ~20938, reads it before setting it — a pre-existing quirk left untouched).
- Deaths/repurchases: counting is still a fresh enumeration at purchase time, so dead or removed creeps naturally stop counting; no cached state to go stale.
- Redundant `set udg_creep_gold_cost=0` (immediately overwritten) dropped — no observable effect.

Intentional micro-divergences (documented, judged non-observable in gameplay):
1. For **unrestricted** unit types, `udg_temp_int` is no longer overwritten with the team-copy count. Audit of all `udg_temp_int` readers in the map shows set-before-use within each trigger, so no reader sees the difference.
2. Dead units are now excluded by the enumeration filter instead of being removed from the group afterwards. The resulting count is the same; this also sidesteps any remove-during-ForGroup iteration quirks.
3. The count group is a local, so the `udg_creep` global no longer holds the (cleared) group between purchases. No other code reads `udg_creep`.

## Validation result

```
JassParseCheck.exe src\war3map.j
OK   (8,836 top-level declarations)
```

Files touched: `src\war3map.j` (creep-limit block only), this document. No release built.

## Remaining risks — in-game tests recommended

1. **Cap enforcement**: buy `n006` (cap 4) five times on one team — 5th must be removed and refunded with the standard message; first 4 must survive.
2. **Cap = 1 type**: buy `uobs` twice — 2nd rejected.
3. **Team counting**: have an ally own 2× `n005`, then buyer purchases 1 — must be rejected (team total 3 > 2).
4. **Death/repurchase**: fill a cap, let one die, repurchase — must succeed.
5. **Refund amount**: verify refunded gold equals the shop price (lumber-bounty-field pathway intact), including in debug mode where the cost line prints.
6. **Unrestricted purchases**: buy several non-listed creeps rapidly — no messages, no removals, no lag spike (scan now skipped).
7. **Debug mode**: `-debug` on, buy any creep — "Creep Gold Cost" line still appears once per purchase.
8. **Regression watch on sell-driven systems**: page system (hero pages sold from shops) still works — it shares the sell event but no shared state was repurposed.
