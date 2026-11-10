# Trigger Notes

Readable trigger/script references:

- `../extracted/799W-tester/files/war3map.j`
- `../extracted/799W-tester/files/war3map.wtg`
- `../extracted/799W-tester/files/war3map.wct`

## Verified Snippet: Death Knight Hero Setup

In the generated script, the Death Knight setup appears near line `14766`:

```jass
//Death Knight
set udg_hero_category[9]=1
set udg_hero_STR_base[9]=20
set udg_hero_STR_inc[9]=2.7
set udg_hero_AGI_base[9]=16
set udg_hero_AGI_inc[9]=1.5
set udg_hero_INT_base[9]=17
set udg_hero_INT_inc[9]=1.8
set udg_hero_move_base[9]=320
set udg_hero_turnrate[9]=0.6
```

## Migration Notes

- Do not rewrite every trigger at once.
- Start by documenting existing behavior from `war3map.j`.
- Move high-complexity systems into Lua only after their current behavior is understood.
- Keep GUI/editor-linked one-off events in the editor until there is a clear reason to migrate them.

## Pass 11 Startup Repair

- Source: `../src/systems/startup_repairs_pass_11.jass`
- Converter: `../../../work/RecodeStartupPass11`
- Repaired the shared start action and SD/AP/AR initialization while leaving uncertain structure/tech behavior unchanged.
- SD temporary groups now have one clear owner and the three count-only debug messages are gone.
- AP labels all nine taverns and cannot read beyond the validated 91-hero catalog.
- AR draws one source hero per active player without replacement and stores that exact rawcode for repick.
- All 499 `InitTrig_` entry points remain available.

## Pass 12 Mode and Spawn Pruning

- Source: `../src/systems/mode_pruning_pass_12.jass`
- Converter: `../../../work/RecodeModePruningPass12`
- Pub setup is Red-only and exposes only Pub Default or Pub Custom.
- Pub Custom contains exactly 2K, No Transmute, and No Pool before SD/AP/AR selection.
- No Transmute filters hero indices 18, 21, 52, 55, 78, and 88 in all three hero modes.
- No Pool locks normal resource trading and disables the autopool command, execution, and periodic transfer triggers.
- Thirty-seven unsupported mode and grouped-spawn trigger bodies are now disabled compatibility stubs.
- The individual spawn scheduler and `eight_mass_bonus` remain active and unchanged.

## Pass 13 Runtime Location Cleanup

- Source: `../src/systems/runtime_location_cleanup_pass_13.jass`
- Converter: `../../../work/RecodeRuntimeCleanupPass13`
- Base, shop-block, shop-kill, and Phoenix boundary movement now uses coordinates without temporary locations.
- All original offsets, shop warning strings, Ankh removal, and kill order are preserved.
- Mass autosend orders use the playable-map center coordinates without allocating one location per footman.
- Both Mass Start branches now store, enumerate, and destroy each player's temporary footman group immediately.
- Static leak candidates fell from 46 to 34; all 499 `InitTrig_` entry points remain.

## Pass 14 Startup Dead Code

- Source: `../src/systems/startup_dead_code_pass_14.jass`
- Converter: `../../../work/RecodeStartupDeadCodePass14`
- The Start Game player callback now contains only its live behavior: assigning starting gold.
- Removed the impossible structure check based on `GetTriggerUnit()` from an eventless force callback.
- Removed ten unreachable base-availability calls; `R00D` and `R00E` remain the real object-data tier requirements.
- Identified `R00N` as Reinforced Defenses and removed its only script write, a level-zero reset targeting player 13.
- Removed the unobserved 280-second upgrade-delay timer global, initialization, and start.
- Real T1/T2/T3 timer triggers and all 499 `InitTrig_` entry points remain.

## Pass 15 Local Handle Cleanup

- Source: `../src/systems/local_handle_cleanup_pass_15.jass`
- Converter: `../../../work/RecodeLocalHandleCleanupPass15`
- River Staff impact and Alchemist bounty now release their one-shot temporary points.
- Thor Powerhit releases each point before replacing it during the movement loop.
- Jaina's ultimate owns its frost, fire, and lightning orbs per cast instead of sharing them across timed waits.
- Jaina's spawn/order points and temporary lightning target group are released immediately after use.
- Debug mode, debug commands, and debug control now release their temporary points and selected-unit groups.
- Static leak candidates fell from 34 to 27; all 499 `InitTrig_` entry points remain.

## Pass 16 Spell Lifecycle Cleanup

- Source: `../src/systems/spell_lifecycle_cleanup_pass_16.jass`
- Converter: `../../../work/RecodeSpellLifecyclePass16`
- River Staff now reuses its existing caster point when projecting the missile start.
- Akama Blink releases and clears its stored return point when the five-second return window expires unused.
- Akama's normal return action still owns the point when the player returns before timeout.
- Tracing confirmed The Nook removes its stored Hellseek point on both completion paths.
- Tracing confirmed `MissileCreate` removes submitted `udg_MissileStart` and `udg_MissileFinish` locations; their caller audit entries are ownership handoffs, not leaks.
- Static leak candidates fell from 27 to 26; all 499 `InitTrig_` entry points remain.

## Pass 17 External Review Fixes

- Source: `../src/systems/claude_review_fixes_pass_17.jass`
- Converter: `../../../work/RecodeClaudeReviewPass17`
- Shop-kill movement now uses `udg_centermap`; the prior `gg_rct_ENTIRE_MAP` target was inherited from the original map and pointed into the bottom-left corner.
- Scroll of Beast now searches `GetPlayableMapRect()` and can apply its cooldown to allied heroes across the map.
- Both Mass footman callbacks use the same map-center coordinates as hero autosend.
- River Staff impact uses `udg_MissileSource` and the active missile trajectory rather than shared cast globals.
- Akama Blink Return clears its released point slot.
- Both unlabeled vote stubs now carry retired labels, bringing the documented total to 39.
- The AFK setup comment now matches the implemented ten-second timeout.

## Pass 18 Guardian Force Field Rewrite

- Source: `../src/systems/guardian_force_field_pass_18.jass`
- Converter: `../../../work/RecodeGuardianForceFieldPass18`
- `AFOR` and its `AFFS` stun ability both have six levels in the packed ability object data.
- Wall count is now 1/1/3/3/5/5 for ability levels 1-6.
- Side-wall locations are projected from the stored field center and cast angle when needed, then released by the same action.
- Cast, natural expiry, and Detonate all use the current field instance for level, caster, geometry, pathing, stun, effects, and duration.
- Removing an older field safely moves the final active field into its slot and transfers each effect handle exactly once.
- The audit still flags `GuardianFF_CreateSidePoint` because it returns a location; every caller owns and removes that returned location.
- Eleven impossible or obsolete generated branch helpers were removed; all 499 `InitTrig_` entry points remain.

## Pass 19 Enumeration Ownership

- Source: `../src/systems/enumeration_ownership_pass_19.jass`
- Converter: `../../../work/RecodeEnumerationOwnershipPass19`
- Warcraft's matching-group BJ wrappers destroy their boolexpr arguments; their inline `Condition(function ...)` calls were retained.
- The Unit Indexer's direct initial enumeration now reuses one filter for all sixteen players and destroys it afterward.
- Eighteen previously anonymous `ForGroupBJ(GetUnits...)` groups now set `bj_wantDestroyGroup` immediately before enumeration.
- Cripple Wave releases its own copied points instead of Searing Bullet's shared point slots.
- Mirror Image leaves submitted missile locations to `MissileCreate` and only clears its stale references.
- Purge the Dead now filters with `GetFilterUnit`, reuses one target point, and destroys corpse effects.
- Scroll of Invisibility and Scroll of Inner Fire no longer destroy unrelated `udg_temp_unitgroup2` state.
- Allied upgrade groups, the allied player force, Frostbolt tower list, upgrade ping, and base-survival checks now have explicit owners.
- One obsolete upgrade group-copy helper was removed; all 499 `InitTrig_` entry points remain.

## Pass 20 Player Lifecycle

- Source: `../src/systems/player_lifecycle_pass_20.jass`
- Converter: `../../../work/RecodePlayerLifecyclePass20`
- Connection state, base survival, and team defeat are now evaluated separately.
- A connected base-less player keeps the team alive while any allied base remains alive, including a departed ally's base.
- Base death changes only the owner state, preserves usable abandoned-base controls, and reevaluates the full team.
- Departure and admin-kick handling share one idempotent path, preventing duplicate controls and stale autopool targets.
- Abandoned-base gold collection and destruction share one validated source mapping and one recipient calculation.
- AR, swap, votekick, and autopool no longer treat departed players as valid participants.
- Inactive cleanup and defeated-team visibility run once per transition.
- The endgame requires exactly one surviving team and is guarded against duplicate execution.
- Retired KOTH departure logic and the unwritten 6v6 result branch were removed from the lifecycle.
- One hundred fourteen generated helpers were removed, 28 named lifecycle helpers were added, and all 499 `InitTrig_` entry points remain.

## Pass 21 Recovered Review Fixes

- Source: `../src/systems/player_lifecycle_review_pass_21.jass`
- Converter: `../../../work/RecodePlayerLifecycleReviewPass21`
- Inactive cleanup now validates every `h02Q` against its source base and team instead of using one global remove-controls switch.
- Defeating one team no longer removes a surviving team's valid abandoned-base controls.
- Connected defeated players retain their `n02G` center vision across later cleanup; departure removes their temporary controls and vision.
- Votekick and autopool dialog clicks revalidate current participation instead of trusting stale menu state.
- Autopool threshold selection no longer allocates an anonymous force or destroys unrelated shared force state.
- The uncalled Visibility action is gone, while its disabled initializer preserves the 499-entry trigger contract.
- Strict parsers, modeled scenarios, the whole-script audit, deterministic rebuild, and packed-map round trip all pass.
