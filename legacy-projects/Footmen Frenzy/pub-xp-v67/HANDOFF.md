# v67 Pub XP test

Based on the verified v66 Team Taverns release. Separate test artifact; not deployed to the bot or installed over a map.

## Progression rules

Normal Pub with mass and colossals enabled only. Pro, 4K, private, inhouse, debug, overdrive, FFCH, no-mass and no-colo retain their existing XP paths.

| Hero level / phase | Native kill XP and scripted kill-supplement rate |
| --- | --- |
| Below 4, before anyone reaches 4 | 100% |
| Below 4, once a registered active hero reaches 4 | 200% |
| Level 4–5, after anyone reaches 6 or mass ends | 150% |
| Level 6, before the first colo spawns | 100% |
| Below 7, from the first colo spawn onward | 200% |
| Level 7–18, at any phase | 70% |

The first-colo rule supersedes earlier catch-up rates. It turns on before wave spawning and persists individually for heroes still below 7. Rates are not multiplied together. No timer, wave event, or milestone grants XP or levels. Killing is still necessary: this targets level 7 around first-colo completion, but cannot guarantee it for a hero earning no XP.

The below-4 boost expires individually. Another hero reaching 5 no longer cancels a slower hero's catch-up. The existing six-XP footman supplement extends from below 6 to below 7 once the first colo spawns; the normal-Pub supplement no longer ends at 480 seconds from map initialization. Sharing and scaling preserve fractional XP. Three other unit-supplement paths and the scripted Blademaster-illusion kill award also use the same rate. Existing non-Pub arithmetic remains in its original branches. Existing non-kill grants/items are not modified, and no new free grants are added.

Only registered active primary heroes drive milestones; showcase heroes, illusions and non-player slots cannot unlock them. A one-second rate refresh covers hiring, repicks, revives and substitutions; level events and phase transitions refresh immediately. The existing 25% anti-cheat XP penalty takes precedence.

## Validation

- 41 rate-boundary cases and 11 mode gates passed.
- Actual helper bodies executed in a small translation harness with mocked Warcraft natives: phase transitions, individual expiry, slot order, fractional rewards, replaced/inactive/illusion heroes, anti-cheat precedence, idempotent initialization and absence of automatic grants.
- Runtime JASS passed pjass.
- Synchronized WCT source regenerated, compiled with JassHelper, and passed pjass.
- Packed source re-extracts exactly; all unrelated archive payloads are checked for preservation.
- Warcraft native XP event ordering, multiplayer behavior, and balance remain untested.

## First playtest

Record hero levels and XP at mass end, first-colo spawn, local first-wave clearance, and two minutes after clearance. Compare time to levels 7, 8 and 10 against v66. Include a poor-opening team, split hero XP sharing, repeated hero deaths, a fast level-7 farmer, and a hero gaining several levels from one large kill.

Check that below-7 native kill rewards accelerate, level-7 rewards slow, and scripted unit supplements follow the same curve. Verify the switching kill: native XP is awarded in engine-sized chunks, so the model is not a hard cap and a large award may cross more than one level. Confirm exactly when native XP and custom death-trigger supplements are applied in Warcraft.

Tune constants in globals.j: 200% catch-up, 150% approach-to-6, 70% post-7 are initial playtest values. Do not interpret the static tests as proof everyone will reach 7 on schedule.

## Rebuild

Run prepare.py, verify.py, compile.py, then pack.py with the bundled Python runtime. compile.py invokes the existing local pjass/JassHelper toolchain; on this machine the 32-bit compilers need execution outside the restricted environment. All generated outputs stay in this folder. Changes go into both war3map.j and authoritative war3map.wct.
