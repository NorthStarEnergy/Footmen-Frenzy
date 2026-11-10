# Working instructions

Complete requests without routine confirmation. Make reasonable assumptions and continue. Ask only when essential information is missing or explicit authorization is required.

## Warcraft III map installation

User-approved layout (November 5, 2026):

- Local root: `C:\Users\User\Documents\Warcraft III\Maps`. Do not install into OneDrive or the former map locations.
- `Downloads` contains downloaded maps.
- Main family folders exist directly under Maps: `799X`, `Solo Foots`, `Mini Foots`, and `FFA Foots`. Each MUST contain the newest available version (including test builds). Archive the previous main-folder version under `Maps\Archive\[map type]`. Preserve the separate deployed and test copies. Presence in a main folder does not promote a test to live deployment.
- `Foots\799X`, `Foots\Solo Foots`, `Foots\Mini Foots`, `Foots\FFA Foots` are deployed maps for real games.
- `Tests\799X`, `Tests\Solo Foots`, `Tests\Mini Foots`, `Tests\FFA Foots` contain the newest respective test build. Create another map-type folder when needed.
- Each test folder contains its own `Test Archives` subfolder. Every new test installation MUST move the previous current test map into that folder. Preserve older files; do not overwrite or delete them.
- Each map-type folder directly under `Maps\Tests` must contain exactly one active map file: its latest test build. Older map files belong below `Test Archives`, never alongside the current test. Reinstalling the same current build must still archive any stray active files. Keep the versioned filename; `foottest.w3x` in the user's example denotes the active map, not a mandatory filename.
- Superseded deployed maps go into `Maps\Archive\Foots\[map type]`.
- Existing legacy archives and the game-managed W3Champions directory are preserved.
- Do not promote a test to real-game deployment merely because it has a newer version number.

Use the checked `Install-Wc3Map.ps1` in this workspace to install builds. Example:

```powershell
& '.\Install-Wc3Map.ps1' -Source 'absolute path to built map.w3x' -Channel Tests -MapType 'FFA Foots'
```

Use `-Channel Foots` for authorized live deployments, or `-Channel Main` to populate a main family folder. Tests installs always synchronize the selected new test into the matching main folder, even if the build tool preserved an older file timestamp. Foots installs update the main folder only when at least as recent as its current map; older deployments do not replace a newer main-folder test. The installer stages and checksums the new map before archiving prior active maps, verifies the installed hash, and archives stray active files even on identical repeated installs. Filesystem escalation may be required outside the workspace. Do not bypass this rollover by directly copying releases into Maps.

The user's intended current test locations are plural `Tests`, not the earlier singular `Test`. Every new test map built in this workspace MUST be installed automatically as the final build step with `Install-Wc3Map.ps1 -Channel Tests -MapType '[correct family]'`, without routine confirmation. This is part of completing the build, not an optional follow-up. Use the build's actual family (799X, Solo Foots, Mini Foots, FFA Foots, or an appropriate new family); do not classify an 8-player FFA build as Solo merely because its filename contains Solo. Before reporting completion, verify exactly one active map in its Tests folder, the same filename and SHA256 in the matching main folder, and preservation of the previous test in Test Archives. If installation fails, report the build as not installed and resolve the failure rather than silently leaving it only in the build directory.

## Canonical GitHub workspace (November 5, 2026)

All four current map projects now live in `C:\Users\User\Documents\GitHub\Footmen Frenzy` (NorthStarEnergy/Footmen-Frenzy). Read its AGENTS.md and README.md before new development. Use its projects/799x, projects/solo, projects/mini, and projects/ffa sources and its Build-Map.ps1 entry point. These older ChatGPT working folders are retained as migration backups and historical dependencies. The old Install-Wc3Map.ps1 entry point forwards to the repository's shared installer so all projects retain the same Tests/Test Archives/main synchronization behavior.
