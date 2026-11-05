# Soul Hook and Mundo combined test

Test map: `release/FF799X_Rx_SoulHook_Mundo_v72_TEST.w3x`.

This combines the corrected Demon Knight Soul Hook from the reviewed v70 with the newer UI/Mundo/Stalker test map. It includes the repaired UI, Lux, Veigar, Stalker movement fixes, Mundo health kit and cleaver, and the 10-second Disease Cloud ramp. It is a test candidate, not a production release.

Soul Hook remains Demon Knight's C skill: six ranks, 450 head travel, 150 catch radius, and 120/160/200/240/280/320 magic damage. The head catches on the outgoing trip only, with continuous collision across each movement segment. Every hook applies its own hit and stun, even if another hook is already dragging its victim. When Soul Hook and Reaping Axe both try to drag one victim, the most recently applied Demon Knight pull replaces the earlier pull. Damage and stuns from both casts still apply. The existing partway drag rule, terrain checks and caster-death cleanup remain.

Mundo's Disease Cloud retains the newer ramp: light green, darker green, purple/dark green and near-black as damage and health drain increase smoothly to double over 10 seconds. Clouds are emitted every half second, with each cloud holding its own emitted color and damage. The combined map's 21 imported particle models were decoded and checked: their alpha blending, fade, native texture reference and gradual adjacent colors match the authored models. Their in-game appearance has not been observed.

Both packed runtime JASS and reconstructed editor source compile. Nineteen mocked-JASS Soul Hook checks, 65 gas checks and 10 resource checks passed; all 21 models were parsed and compared; 1,379 known inherited archive files were read and 1,398 unrelated archive entries preserved. The embedded source snapshots and source manifest were refreshed from the synchronized editor data. See `verification.json`, `checks.json`, `mundo-checks.json`, and `model-checks.json` for evidence.

**No Warcraft engine or multiplayer playtest was performed.** Test two simultaneous hooks, hook plus returning axe, targets at the edge of the corridor, walls/cliffs and death during a cast. For Mundo, watch the entire color ramp while standing and moving, including after toggling off/on, and verify damage, health drain and the dark gas against actual terrain. Engine rendering, spell-block interactions, native stun behavior and balance remain unverified.

SHA-256: `b9efcb334419d88f6ad96da70f868cf22c0d121297cc4f2d37facb5c11aff780`. The reviewed v70 and combined input map are preserved. This build is not installed or deployed.
