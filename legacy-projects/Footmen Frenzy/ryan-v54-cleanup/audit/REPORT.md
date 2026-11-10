# Ryan v54 / cleaned v55 object and code audit

Read-only audit; map unchanged. All seven object tables parsed and byte-exact round-trip checked.

| Category | Custom | Modified standard | No-direct-reference candidates |
|---|---:|---:|---:|
| units | 609 | 139 | 89 |
| items | 230 | 85 | 33 |
| abilities | 1535 | 362 | 413 |
| buffs | 132 | 0 | 33 |
| upgrades | 28 | 8 | 5 |
| destructibles | 1 | 0 | 0 |
| doodads | 0 | 1 | 0 |

Script: 3705 functions; 297 have no discovered path from main/config (103,986 bytes of uncompressed function bodies). Direct callbacks and literal ExecuteFunc targets are included conservatively by identifier matching. This is a static candidate list, not proof every candidate can be deleted.

Examples of leftover code include the disconnected Guardian Force Field Detonate trigger, old Twisted Fate pickACard/destiny helper functions, old MODE_1v1/Overdrive/camera initializer functions, and unused generated GUI condition helpers. Do not remove whole libraries merely because some public helpers are unused.

The script also retains GST Example expiry triggers: their initializer calls remain present, so these are not classified as disconnected merely because they start disabled. Disabled triggers may be executed or enabled elsewhere.

Editor data: war3map.wct 2,696,312 bytes; war3map.wtg 519 bytes. Runtime and editor custom source must be changed together to prevent old code returning on editor save.

Review objects.csv for every object and its references; functions.csv for every function, callers and static reachability. Additional SLK/TXT data mentions are retained conservatively; a mention may be a definition rather than a use. Blank object names mean no name override exists in the binary object record, not an unnamed in-game object.

Limits: static scan does not resolve computed rawcodes, numeric encodings, all engine-inherited dependencies, arbitrary dynamic calls or unnamed archive files. Modified standard objects are not deletion candidates; reverting them requires comparing gameplay fields with Warcraft defaults. No live match or editor save test was performed.

Recommended next cleanup: remove individually proven disconnected code from both runtime and editor source, then resolve object candidates against inherited/default and SLK data before deleting them. Keep active hero scripts, shops, tech trees, summoned/dummy units, buff chains and core systems. Compressed map savings will be smaller than uncompressed code sizes.