# Objective
Replace Demon Knight's Blood Tithe with a new C-slot spell, Soul Hook: a short-range, fast hook that pulls everything it catches only partway back. Deliver a new map version from the latest verified map, preserving v68 and v67.

# Current status
v70 test candidate built and statically verified. Delivered locally at C:\Users\Ryan1\Transfer\DemonKnight_SoulHook_v70. Engine playtest NOT performed.

# Changes and important files
- Baseline: C:\Users\Ryan1\Transfer\Veigar_Classic_v68\FF799X_Rx_Veigar_Classic_v68.w3x (preserved); SHA256 ca55bf08034a5a8cfe4b37c374dd87f68f4fd358d73a57e0c95266188b467b35.
- Also preserved: C:\Users\Ryan1\Transfer\FF799X_Rx_Pub_XP_v67.w3x; SHA256 f51fd7d74d2977d8f20c005c79a7ae14678c717167f63c8983e1503cba91150f.
- Map: FF799X_Rx_DemonKnight_SoulHook_v70.w3x; SHA256 f311fd6821d1746504a6cbfb93fdc0a23937758c3b6ff4843bff7b05f076fd9b; 32,881,094 bytes.
- Build/checks: C:\Users\Ryan1\Documents\Footmen Frenzy Development\outputs\demonknight-soulhook-v70 (build.py, soulhook.j, baseline/, verification.json).
- README.md lists every rank value, the drag geometry, unchanged Reaping Axe / Pulverize / Demon Ascension values and the playtest checklist.
- SoulHook_Source.zip contains build.py, soulhook.j and the spot-check script used to validate the packed object data.

# Verification performed
JassCheck parse, pjass compile of both the packed script and the regenerated editor source, object-data round-trip plus unrelated-field comparison, member-by-member packed readback, 1373-member count matching v68, editor source/runtime/packed script consistency (no missing, changed or unexpected functions or globals), unchanged global declaration block. Changed functions are limited to DK_Free, DK_Tick, DK_OnCast, DK_Init; four new functions are DK_HookCast, DK_HookCatch, DK_HookChain, DK_HookStun. Object data spot-checked from the packed archive: ADk5/ADk6 fields, HDk1 abilities = ADk1,ADk2,ADk5,ADk4, and no Blood Tithe wording left on Reaping Axe, Pulverize or the hero tooltip. Engine, editor-save and multiplayer testing NOT performed; no balance claim is made.

# Decisions and constraints
- Slot: C replaces Blood Tithe; Z Reaping Axe, W Pulverize, V Demon Ascension unchanged. Blood Tithe's mark passive is gone with the ability; the unused ADk3 object entry and dead code remain but are unreachable.
- Soul Hook: 450 range, ~0.25 s outbound travel, 150 catch radius, 120-320 magic damage, 0.5-1.0 s stun, 60-110 mana, 12 down to 10 s cooldown, learns at 1/4/7/10/13/16.
- Drag: 45% of the victim's distance to the caster, clamped to 150-400 and never closer than 100; 1280 units/s; direction recomputed each tick; blocked by terrain/cliffs/buildings.
- Implementation reuses the v68 Demon Knight state machine (kind 11 head, kind 12 dragged victim) and adds zero globals. ADk5 is a Channel clone with base order carrionswarm so it does not share Reaping Axe's cooldown; ADk6 is a zero-damage Storm Bolt clone for the stun dummy.
- Only ground, non-structure, non-flying, non-magic-immune, non-invulnerable enemies are caught, matching the map's existing FS_Enemy filter.
- Transfer folder only; nothing installed into the Warcraft Maps folder. v69 Veigar refinement is paused and untouched.

# Remaining work or blockers
Playtest the map in Warcraft: load, learn panel and icon, C-slot cast and range, catch radius in clumps, stun duration, drag distances and wall/cliff behaviour, magic-immune/flying/building exclusions, cooldown and mana per rank, absence of Blood Tithe UI, death mid-flight cleanup, and multiplayer sync. Static checks do not establish balance or correctness in the engine. Version any further fixes as v71 and keep v68/v70 intact.

# Fresh-chat prompt
Read C:\Users\Ryan1\Transfer\DemonKnight_SoulHook_v70\HANDOFF.md and README.md, then playtest C:\Users\Ryan1\Transfer\DemonKnight_SoulHook_v70\FF799X_Rx_DemonKnight_SoulHook_v70.w3x. Preserve v67 and v68, keep Soul Hook on Demon Knight's C slot with the documented numbers, and version any fixes as v71. Do not claim engine testing unless it was actually run.
