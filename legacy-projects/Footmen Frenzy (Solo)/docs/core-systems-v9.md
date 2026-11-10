# SF Test 1.7 v9 - Core-System Hardening

## Startup

- Removed the duplicate `Start_game` execution from the AFK-host fallback.
- Normal selection and AFK fallback now converge on the same single startup path.

## King of the Hill

- Moved KOTH creation out of map initialization and into the actual game-start function.
- Removed the temporary GPT diagnostic banner and ping.
- Added a null guard so the initial hill cannot be created twice.
- Connected the previously unstarted fourth-hill timer at 1,340 seconds.

KOTH progression is now scheduled at 460, 900, and 1,340 seconds after game start.

## Colossals

- Explicitly displays the first-wave timer dialog.
- Corrected each base-wave minimap ping to use that base's Colossal spawn point instead of an already-removed temporary center location.
- Preserved the restored 150-second initial wave and 300-second recurring-wave schedule.
