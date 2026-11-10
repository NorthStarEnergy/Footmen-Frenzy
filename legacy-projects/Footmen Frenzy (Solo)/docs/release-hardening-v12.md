# SF_Test1.7_v12 release hardening

## Changes

### Startup consistency

- Normal/public mode now sets `udg_mode_koth` to `true` instead of briefly setting it to `false` before the real game-start path corrected it.
- The global default, public-mode setup, and game-start safety assignment now all agree that KOTH is a base Solo Foots system.
- Colossals remain enabled with the existing 10-wave maximum and still start from the real game-start path.

### Event-driven fake-shop visibility

- Added `SF_MH_UpdateFakeShopVisibility` as the single visibility decision point.
- Fake shops hide while the rat concealment timer is active.
- With anti-maphack enabled, fake shops also hide while at least one tracked truesight unit exists.
- Visibility updates now occur when rat concealment starts or expires, a tracked truesight unit enters or dies, or anti-maphack is toggled.
- Removed the 0.01-second hide poll and the 1.00-second unhide poll.
- Removed the unrelated `RemoveLocation(udg_temp_point)` call from rat-timer expiry; that action did not create or own the location.

### Self-contained verified build

- Copied the JASS parser, MPQ script packer, and MPQ extractor into `tools/bin`.
- Added `tools/Build-VerifiedMap.ps1`.
- The script refuses to overwrite numbered artifacts, parses the source, builds the map, extracts `war3map.j`, verifies its SHA256 against the source, and optionally delivers the map into the matching Warcraft III folder.

## Verification

- JASS parser: OK, 8,811 top-level declarations.
- Packed script bytes: 2,186,028.
- Source/round-trip script SHA256: `A99B676FC59C52A29CAFB3C8777A19AA2AA3E721E2F4945218059DF67A34933A` (exact match).
- Map SHA256: `F8F2FEDFA9E85A5DB750493660C4AB5CE3085B2F7568302BCE628F8C7E3A2C4B`.
- Extraction: 1,204 files extracted. The extractor returned its known nonzero result for the malformed `(listfile)`, but `war3map.j` was extracted and matched exactly.
- Delivery folder contains exactly one map file.

## Required in-game tests

1. Start a normal solo game and confirm KOTH appears immediately when the real game begins.
2. Confirm the first Colossal timer starts and its wave still spawns.
3. Cast a rat concealment ability and confirm fake shops stay hidden for the full 16 seconds.
4. While anti-maphack is enabled, create a tracked truesight unit and confirm shops hide immediately.
5. Kill the last tracked truesight unit after the rat timer has expired and confirm shops reappear immediately.
6. Kill the last tracked truesight unit while the rat timer is active and confirm shops remain hidden until expiry.
7. Use the authorized `-mhon` and `-mhoff` commands and confirm visibility refreshes immediately.
