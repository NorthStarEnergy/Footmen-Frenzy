# Footmen Frenzy

Four Warcraft III map projects, shared build/install tools, and development history.

| Project | Current baseline | Branch | WC3 test folder |
|---|---|---|---|
| 799X (12 players) | Shared Fixes v85 | Footmen-Frenzy-12p | Tests/799X |
| Solo (4 players) | UPDATE09 | Solo-Foots-4p | Tests/Solo Foots |
| Mini (8 players) | v10 | Mini-Foots-8p | Tests/Mini Foots |
| FFA + King (8 players) | v17 | FFA-Foots-8p | Tests/FFA Foots |

## Get the project

Install Git and Git LFS, clone this repository, then run `git lfs pull`. Binary maps and imported assets are stored with LFS; pointer files cannot be opened in Warcraft III.

- `projects/<project>/src`: editable files extracted from the exact current release.
- `projects/<project>/release`: complete verified baseline map, including unnamed/protected assets.
- `project.json` and `source-manifest.json`: baseline identity, checksum, and extracted-file inventory.
- `tools`: shared archive, build, and install code.
- `development`: imported historical build scripts, checks, reports, and UI definitions. These are reference history, not the current build entry point. Historical paths and dependencies may refer to the preserved original working folders.

All branches begin with the same complete four-project baseline. Use the named map branch for its changes. Common, Heroes, and Units are shared-development branches, not automatically synchronized modules. Merge reviewed shared changes into the affected map branches.

## Build and install a new test

Windows, Python 3.10+, and a 64-bit StormLib DLL are required. Copy `tools.local.example.json` to `tools.local.json` and set your local tool paths. Changed JASS additionally requires pjass plus Warcraft III common.j and Blizzard.j. Third-party tool binaries are not bundled.

```powershell
.\Build-Map.ps1 -Project 799x -Name FF799X_v86_TEST.w3x
.\Build-Map.ps1 -Project solo -Name Solo_Foots_UPDATE10.w3x
.\Build-Map.ps1 -Project mini -Name 'Mini Foots v11.w3x'
.\Build-Map.ps1 -Project ffa -Name Solo_Foots_8P_FFA_v18.w3x
```

Edit `src` first. The builder sets the in-client map title to the output filename without the .w3x extension and verifies it in the packed map. The builder copies the complete baseline, replaces changed payloads, compiles changed JASS, verifies roundtrip bytes and untouched named entries, and writes its verification report under ignored `build/`. Removing a source file does not delete an archive entry. Game and World Editor testing remain necessary for gameplay changes.

The PowerShell entry point then installs into local `Documents/Warcraft III/Maps/Tests/<map type>`, archives the previous test inside `Test Archives`, and synchronizes `Maps/<map type>`. Exactly one active test remains. Previous main copies go into `Maps/Archive/<map type>`. It never deploys into `Maps/Foots` unless separately requested and never writes maps into OneDrive or singular `Maps/Test`. Use `-Python` or `-MapsRoot` to override local executable/destination paths.

For a prebuilt validated map, use `tools/Install-Wc3Map.ps1 -Source <path> -Channel Tests -MapType <family>`.

## Verification

```powershell
python tools/check_repository.py
python tools/build_map.py 799x --verify-only
```

The first command checks release hashes, required sources, and Python tool syntax without Warcraft tools. The second compares extracted source bytes with a baseline using StormLib; it is intended for an unchanged snapshot. CI checks repository structure and release integrity on Windows with LFS enabled. It does not simulate Warcraft gameplay.

## Migration and retained files

Imported November 5, 2026 from the existing Footmen Frenzy and Solo working folders. All four release checksums match the installed current maps. Original working folders remain as recovery copies. Generated intermediate maps, downloaded runtimes, caches, old binary archives, unrelated NorthStar/SCADA files, and the unrelated source-folder Git history were not uploaded. Current imported assets are preserved in the baseline maps and extracted source; older binary versions remain in the original local archives. See `development/migration-manifest.json` for the transferred development files.

No new license is asserted over Warcraft III or inherited third-party models, textures, sounds, or scripts. Existing asset ownership and permissions continue to apply.
