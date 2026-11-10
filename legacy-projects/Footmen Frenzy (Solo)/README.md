# Solo Foots Development

## Current four-player solo build

The newest four-player update is [Solo Foots v1.8 4P — 799X Update 08](solo-v1.8-799x/README.md), built from PRELOAD TEST07 with Gragus and Gul'dan/Orianna from 799X v80 plus compatible Architect and attack-range fixes. The playable map is under `solo-v1.8-799x/release/`. Compilation and archive verification passed; in-game testing is pending. The v1.7 notes below describe the older development line.

This workspace contains only the SoloFoots v1.7 map project material consolidated from the disassembly workspace.

## Source of truth

**Do not open the map in World Editor.** The trigger source (`war3map.wtg` / `war3map.wct`)
no longer describes the script the map runs, and saving from WE destroys every custom
system. See [BUILD.md](BUILD.md) for the build pipeline and the verification gate.

- `src/war3map.j` â€” current development gameplay script (newer than the v30 release).
- `src/war3map.w3u` â€” matching unit object data.
- `Disassembled Map/` â€” full current MPQ extraction, including imported assets and map data.
- `releases/SF_Test1.7_v30.w3x` â€” current verified local build; map binaries are published through GitHub Releases rather than normal Git history.
- `releases/SF_Test1.7_v29.w3x` â€” previous verified baseline.
- `docs/claude-item-limits-refactor.md` â€” rule catalog, equivalence audit, and in-game test matrix for the current build.
- `docs/jass-audit.md` and `docs/jass-audit.json` â€” performance audit reference.

## Verified hashes

- v30 map SHA256: `AC10A9F6BDE9A5ED9423774A34FD857A25DC2F031812062B8502D5AE32D5FECF`
- Current development script SHA256: `DC532AE2FE309C804ECE344A80831F369CC09FEE6E2EFFE9A0A3D6B8B8C3593D`
- Unit object data SHA256: `B0F8043E9D18088AD264B64F4AAAA0FFCD813EAB6288CE915A1FCCB2CA1C332E`

The v30 build passed the JASS parser and an exact script round-trip extraction check. The current source additionally contains post-v30 item-pipeline work documented under `docs/` and should become v31 after verification. Gameplay execution still needs an in-game Warcraft III test.

## Verified build command

The parser, map packer, and extractor are stored under `tools/bin`, so building no longer depends on the old external Codex work directory. From the project root, use:

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\Build-VerifiedMap.ps1 -Version SF_Test1.7_v31 -BaseMap <path-to-v30.w3x> -Deliver`

The command refuses to overwrite an existing release, round-trip folder, or delivery folder. It parses the JASS, packs the map, extracts the packed script, verifies an exact SHA256 match, and then creates the numbered Warcraft III delivery folder.

## Current KOTH test

Normal solo startup now enables King of the Hill automatically and creates the neutral hill immediately when the game mode starts. All KOTH action, death-event, income, progression, and temporary-invulnerability trigger wiring has been restored from the original SoloFoots v1.7 script.

- Test-map SHA256: `201E27C17F857C1FECF8647022EC988965FE0DC1620B6D2A98FE71AB296761F2`
- Script SHA256: `EEF66B700C467785AB7CB3A6EF4F2D366A355339A8D189381D45388269ABBB9E`
- Round-trip script SHA256: exact match

## Test-map delivery convention

Every new test map must also be copied to a sequentially numbered folder:

`C:\Users\Ryan1\Documents\Warcraft III\Maps\Solo Foots\GPT\SF_Test1.7_v<version>\`

The map inside must use the matching name: `SF_Test1.7_v<version>.w3x`. The current build is v30, so the next test build is v31.

## Repository policy

Generated `.w3x` releases, round-trip extractions, and temporary work folders are intentionally excluded from Git. Publish playable maps as GitHub Release attachments. Review licensing and attribution for imported Warcraft III assets before making the repository public.

## Deliberately excluded

Duplicate historical extractions, Performance Tests 2â€“5, smooth-spawn experiments, script-only temporary maps, and repeated round-trip folders were not copied. They remain untouched in the original workspace.
