# SF_Test1.7_v15

## Gameplay changes

- KOTH first hill now appears at 100 seconds of game time.
- Normal KOTH income tiers are 12g, 15g, and 20g per interval. The fourth hill remains at the 20g cap.
- Overdrive KOTH income remains doubled at 24g, 30g, and 40g.
- Hill ownership resets after a team earns 400g instead of 300g.

## UI changes

- The leaderboard clock is yellow while the `Leaderboard -` label remains white.
- All 258 screen-message call sites use a shared feed at screen position x=0.01, y=0.18.
- Messages use a 0.50-second timed display so they begin fading quickly.
- F2, `-clear`, and `-c` clear messages for the player who uses them.

## Verification

- JASS parser: OK, 8,860 top-level declarations.
- Source and packed-script SHA256 match: `756745862B80EA22B1F5C663E81990AE94E9AE6D393E6B8A8C6C091A23CAA4FA`.
- Release and delivered-map SHA256 match: `FB3BA64182193A605491A3D1035B5B608DC464295140B5DA1B06E6B08DDD32A0`.
- All 1,203 non-script files are byte-identical to v14.
- The extractor's only failure is the pre-existing broken `(listfile)` entry.
- In-game Warcraft III testing is still required.
