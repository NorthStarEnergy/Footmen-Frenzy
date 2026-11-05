# Veigar visuals v81

Built from the verified v80 Fed Rewards TEST candidate. This is a separate test map; it has not been installed into Warcraft or deployed.

## Imported visual work

- Baleful Strike: blue-black orb attached to the target's chest for 0.30 seconds.
- Primordial Burst: blue-purple orb with a bright core attached to the target's chest for 0.30 seconds.
- Dark Matter: blue meteor and blue impact models. Neutral effect tint allows the models' authored colors to show; the existing size, descent, impact timing and cleanup remain.

The four MDX assets are copied byte-for-byte from `Transfer/veigar-refine-v69-work/edited/Spells/Veigar69`. The orb models are used as short hit flashes so Q/R damage remains immediate. The unfinished travelling-projectile code was not imported. Icons, hotkeys, cage behavior, stats, balance, Twisted Fate, and all other v80 features are unchanged.

## Verification

Both runtime pjass and authoritative World Editor source JassHelper/pjass compilation passed. All four models parse and round-trip, with the required Stand/Birth animations and valid particle texture indices. Packed payload readback passed; all 1,399 unrelated archive entries and all object data are preserved. Reversing the specific model/color/hit-effect substitutions restores the original three edited functions exactly. The only added function creates a cosmetic effect and schedules the existing timer/effect cleanup.

Not engine-playtested. Check Q/R readability on moving, dying and flying targets; confirm orb flashes disappear after the short hold. Check the meteor and impact colors and visibility, repeated casts and multiple Veigars. Damage remains immediate for Q/R and delayed 1.25 seconds for Dark Matter. This build also inherits v80's documented pending gameplay checks.

## Rebuild

Run `node veigar-visuals-v81/check-models.cjs`, then run `veigar-visuals-v81/build.py` with the bundled Python. The existing legacy JASS compilers require execution outside the restricted sandbox on this machine. The build checks the v80 base hash, updates the authoritative embedded source and manifest, compiles both script paths, and verifies archive preservation.

Release: `release/FF799X_Rx_Veigar_Visuals_v81_TEST.w3x`. See `verification.json` and the adjacent SHA-256 file for identity and validation results.
