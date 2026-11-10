# Shared fixes: 799X v85 and Solo UPDATE09

Built November 4, 2026 from hash-verified 799X v84 and four-player Solo UPDATE08. This is a bidirectional compatibility port, not a conversion of either map's format.

## Solo improvements that were missing from 799X v84 and are now included

| Area | Ported improvement |
|---|---|
| Throw Glaive | Coordinate-based travel and distance checks eliminate repeated location allocations while retaining 799X's movement and targeting values. |
| Cripple Wave | Release its own point array instead of Searing Bullet's points. |
| Staff of the River | Release temporary launch and hit-enumeration origin locations; retain 799X healing and missile speed. |
| Mirror Image | Give the consuming missile system a copy of its endpoint; retain the persistent stored endpoint. |
| Thor Powerhit | Release each superseded movement-step location, retain the pathing helper's borrowed reference, and clear it afterward. |
| Prison | Release replaced wall points on recast, temporary blocker points after creation, and expiry handles once. Use coordinates for exile relocation. Stop idle countdown polling. |
| Myrmidon Sinkhole | Track and clean per-cast dummies and center points, reuse enumeration groups, support recasts and simultaneous casters, and stop polling after the last sinkhole. The helper's 12-slot loop supports standard 799X. |
| Architect, Bloodrush and item walls | Release placement locations, avoid repeated destruction of expired text tags, and stop idle timer scans. Existing casts re-enable the triggers. |
| Hook/Pandero | Clear released handles; choose a random target without allocating a temporary subgroup. Retain 799X hook distances and speed. |
| Shop boundaries and page selection | Coordinate-based displacement and punishment, scoped enumeration/group cleanup, and table-driven selector lookup. Keep all 799X team conditions/regions and the special u01C Personal Shop behavior. |
| Creep caps | Skip full-map scans for unrestricted types; destroy owned count groups/filters; preserve all cap/refund decisions and 799X observer-substitution ownership handling. |
| Item caps/combinations | One inventory scan plus lookups; avoid leaking message forces. Preserve 799X-specific Necklace/I03C caps, hero exclusions and overflow behavior. |
| Item spells | Reuse Purge the Dead's existing target point, release Forked Fury's proc point, and share equivalent scroll filters/callbacks. Preserve the recipient's ability IDs and cooldowns. |

This changes 46 existing 799X functions, adds 22 helpers and four globals, and preserves the remaining 3,762 v84 function bodies. All v84 custom heroes, Veigar Z/V stacks, Guardian visuals, spawn balance, progression/rewards and observer-substitution systems remain.

## 799X fixes now added to Solo

- **Jaina ultimate:** each overlapping cast owns its caster, rank, three orbs and temporary handles. A second cast no longer redirects the first cast's orders/removals to its own orbs.
- **Alchemist Chemical Rage bounty:** use the actual caster and its hero level instead of a possibly stale primary-hero slot. The guard and direct-caster implementation come from 799X. Solo's existing 8 dice × 3 sides are retained, along with its own base-bounty table; the 799X deterministic bounty policy is not imported.
- **Shockwave item overflow (I009):** retain the two-copy limit but eject one held copy rather than destroy up to three copies without feedback.
- **Two-copy warning:** report “Only 2x” for two-copy items, instead of the old incorrect “Only 1x”.

Solo changes three gameplay functions, adds one helper, and changes only the display name in `config`. The remaining 2,956 functions, all objects and its four-player configuration are preserved.

## Already shared or deliberately kept distinct

Solo UPDATE08 already contains current Gragus/Gul'dan implementations, Architect caster-ownership recruitment, effective attack-range updates and most shared event-data snapshots. These were verified/preserved instead of replaced with older generated code.

The comparison also exposed actual format/balance differences, not missing fixes: Solo's four-player slot/team arithmetic, selection roster, camera/message filtering, spawn/preload scheduler, economy, item/hero balance, and KOTH setup stay Solo-specific. 799X keeps its twelve-player structure, roster, team shops, observer substitutions and v67–v80 Pub/Colossal/reward rules. The variants use different Forked Fury and Death Ward ability IDs in their actual object data; each retains the matching IDs. No new hero roster, game mode or mode default is imported into Solo. Cosmetic-only differences in generated-library formatting are not changes.

This review identified shared behavior by comparing actual functions and objects, not by treating every differing function name as a missing fix. Broader redesigns, historical prototypes and format conversions remain outside this port.

## Verification

Both packed runtime scripts compile with pjass. The updated 799X authoritative World Editor source also compiles through JassHelper and pjass. Solo's inherited GUI source is not authoritative; its runtime remains the source of truth, as in UPDATE08. Do not resave Solo in World Editor without first migrating that source workflow.

- Exact packed-payload readback and preservation of all 1,405 unrelated 799X archive entries and all 1,259 unrelated Solo entries.
- Unit, ability, buff, item, upgrade, map-info/player, terrain and placement payloads remain byte-for-byte identical to each map's own baseline.
- 42,548 item-rule, mixed-inventory, creep-cap and rank/terrain test cases execute translated final JASS with mocked natives. 799X's original outcomes match; Solo differs only in the documented overflow/warning corrections.
- Interleaved Jaina casts, caster-based Alchemist bounty/dice checks, Thor handle cleanup, simultaneous/recast/slot-12 sinkholes, repeat-safe timer cleanup and mode/roster preservation checks pass.
- Specialized 799X hero/reward functions and Solo Gragus/Gul'dan, camera, preload/spawn and mode functions are preserved.

These are compiler/static/mocked-native checks, **not Warcraft engine or multiplayer playtests**. In-game testing remains required for native event ordering, animation, long-session behavior and multiplayer synchronization.

## Deliverables and rebuild

- `release/FF799X_Rx_Shared_Fixes_v85_TEST.w3x`
- `release/Solo_Foots_v1.8_4P_SHARED_FIXES_UPDATE09.w3x`

`migration.json` and each variant's `verification.json` identify the exact bases, output hashes and function changes. `behavior-checks.json` and `lifecycle-checks.json` record verification. `installation.json` records installed-file hashes once copied. Older maps are preserved.

Run `build.py` using the bundled Python, then `check.py` and `lifecycle-check.py`. Legacy JASS compiler execution requires running outside the sandbox on this machine. The `inspect`, `adjust` and other investigation scripts are historical working notes, not rebuild steps.
