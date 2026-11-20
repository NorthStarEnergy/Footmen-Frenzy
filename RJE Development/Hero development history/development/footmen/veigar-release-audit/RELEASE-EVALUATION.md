# Veigar v81 release evaluation — 2026-11-03

**Verdict: suitable for a controlled test session; not yet approved for public release.**

Evaluated the delivered `Transfer/Veigar_Visuals_v81/FF799X_Rx_Veigar_Visuals_v81_TEST.w3x`, SHA-256 `3bbd2cb4a64799453f919da292636b79e2b6dcbaecf696b744a79324ce8bc1e4`. This review did not modify the map or run Warcraft.

## Evidence that supports testing

- The delivered map hash matches the verified v81 artifact. The existing v81 runtime and World Editor source compilation checks passed, as did four-model parse/round-trip validation and preservation of 1,399 unrelated archive entries.
- Re-extracted the delivered script and object data and ran 52 current-artifact checks: cage geometry, one hit per cage, rejected stun-order retry, exclusion rules, stun feedback cleanup, all 21 cast ranges, stun projectile speed and all stun durations.
- Ran 32 additional mocked behavior checks covering Q last-hit INT, hero-kill INT at every rank, excluded victims/casters, unlearned Q and Equilibrium at empty/half/full mana. One additional reproduction establishes the teleport concern below. These 85 successful assertions are not 85 engine tests.
- Object records give Q/W/E/R ranges 900/1100/1100/850; E stun durations are 1.5–2.75 seconds. Hero stats are 15/16/20 with growth 1.5/1.5/3, movement 270, attack range 600. All four skills and the innate passive are assigned. The unfinished Z/X/C/V reordering was not imported: the actual bindings remain Q/W/E/R.
- v81's new Q/R visual helper only creates a short target-attached effect and schedules existing cleanup. Damage still happens immediately. The draft projectile gameplay is absent.

## Findings and release gates

### Cage scanning needs a large-army performance test

`VG_CageScan` enumerates the entire playable area on every cage tick; `VG_Tick` runs every 0.03125 seconds. Every eligible enemy not already caught receives polygon crossing checks and previous-position writes. At 1,000 enumerated units, one active cage causes roughly 32,000 unit visits per second, plus geometry work; concurrent cages multiply this workload. This is an operation-count risk, not measured engine lag. Equilibrium also scans the whole map once per second.

Before release, run several concurrent cages with late-game army counts on multiple clients and compare responsiveness/frame timing to a no-cage baseline. Optimize if the difference is material; any localized scanner must preserve fast ordinary movement detection.

### Teleports are treated as walking through the wall

The scanner connects each unit's old and new positions with a straight segment. A reproduced jump from (-500, 0) to (500, 0), both outside a cage centered at (0, 0), receives a stun order because that imagined segment crosses the cage. There is no teleport distinction. Confirm the intended interaction with Blink, Gate and other map teleports; if teleporting over the cage should avoid the wall, this needs a fix. The reproduction uses native mocks, not an engine teleport.

### The new visuals and native spell behavior are not signed off

No Warcraft visual or multiplayer test is recorded for v81. Confirm Q/R flashes on moving, dying and flying targets, Dark Matter animation/impact alignment, effect cleanup, actual cage stun application and interruption at every rank, overlapping cages, immunity, maximum cast range, and death/revive. Confirm actual Q damage/death event ordering awards INT exactly once; the harness does not emulate the Warcraft damage engine.

Model parsing validates format, not rendering. I could not rerun the five historical installed-game metadata checks or resolve the models' ten stock texture references because the historical CascLib DLL path is missing. These checks are explicitly excluded from the fresh passed count; the audit makes no claim that the textures are missing from the game.

### Balance remains a playtest question

At level 18 with 71 INT and no extra stacks, max Q+W deals 1,253.6 raw damage. Adding R against a 50-INT hero produces 2,528.8 raw damage before defenses. Fifty additional INT adds 140 damage across that combo. The cage's long cast range and immediate rim activation make reliable setup the key balance concern, while low starting Strength and 270 movement provide vulnerability. These values do not establish that a nerf is needed. Run equal-investment matchups and farm-heavy games before changing numbers; verify permanent stacking does not snowball beyond the intended roster power level.

### Whole-map release remains separate

v81 inherits the v80 custom kill XP/gold payout system and its unresolved engine-comparison checklist. Even if Veigar passes, that does not certify the entire map for public release. See `fed-rewards-v80/HANDOFF.md`.

## Recommendation

Keep v81 labeled TEST. First resolve the intended teleport interaction, then run a focused multiplayer session covering large-army cage performance, native stacking/stuns, new visual readability and equal-investment matchups. Release only after those results are recorded and the inherited whole-map gates are satisfied. No additional visual imports or balance edits are justified by this review alone.

Reproduce the static/mocked review with the bundled Python and `veigar-release-audit/audit.py`. Evidence: `checks.json`, `additional-checks.json`, `objects.json`, `textures.json` and the extracted `src` files.
