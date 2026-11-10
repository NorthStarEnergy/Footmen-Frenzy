# 799X Orianna, UI and Gragus backport

Release: `release/FF799X_Rx_Orianna_v16.w3x`. In-game map title: **FF799X - Orianna v16**.
Installed in both Warcraft `Maps\Test` folders; previous v12 copies were archived.

Based on the latest locally identified 799X development build, FF799X_Rx_HeroTavern_v1, with changes from the current Mini Foots source.

- Compact Stats button above the minimap, consistent text and portrait anchors, early initialization independent of multiboard visibility. Expanded to all 12 players with four groups of three and an upper-right close button.
- Vertical zoom slider with explicit track/thumb artwork, lock button, distance label and delayed creation.
- Gragus Drunken Fortitude directly adds and removes its armor bonus. Green Fortitude and blue Body Slam icons imported. All other FS spell functions already match Mini Foots and are retained.

Original player slots, terrain, units, balance, tech, timings, pooling, and mass behavior are preserved. Original maps and Mini Foots are not overwritten.

## Previous build: v12 (steady overhead orb and Gragus repair)

The orb returns to directly above its carrier at fly height + 260 units, without facing offsets or idle bobbing. A 112-unit-diameter opaque jade sphere with baked shading replaces the particle missile, with no lights, emitters, additive layers or animated opacity. It remains full size during flight and return; Protect tints it blue. The deliberate Attack pulse gesture remains. Soft ground effects, Lich stats, Necromancer projectile and Sorceress voice remain unchanged.

Gragus's X (Drunken Fortitude) had changed base armor directly without adding the configured AGf1 native modifier, leaving no visible buff or green armor bonus. It now adds AGf1 at the spell rank and hides the passive command button; the native self-only Devotion-derived modifier provides +5/7/9/11/13/15 armor and its existing BGf1â€“BGf6 buff icons/tooltips. Base armor is no longer rewritten. Refresh removes the previous modifier before reapplying; expiry and death remove the modifier, buff and effect. Existing healing and magic reduction remain. A 100-unit self-only scan and 0.2-second aura duration replace the zero-radius, 0.01-second settings. The cast uses the distinct no-target roar order, and native Inner Fire art provides visible feedback.

All four Gragus active/research icons and their disabled variants are re-encoded with opaque BLP1 alpha and complete mipmaps, retaining their artwork and file paths. This replaces the mixed BLP1/BLP2 payloads. `prepare_gragus_icons.py` reproduces the assets. Validation includes 127 Orianna checks, 35 Gragus lifecycle/object/icon checks, 18 debug recruitment checks, pjass and archive verification. Engine visual validation remains with the user.

## Previous build: Orianna v11 (solid front orb, soft magic and Lich stats)

The Enchantress orb now contains an original opaque shaded core and uses full effect opacity, while retaining its subdued outer glow. At home it is held 70 units in front of Orianna, 145 units above terrain plus her fly height, at 1.05 scale. The control ball and visual follow her facing together. It grows to 2.0 scale over 0.22 seconds on departure; redirecting an already enlarged orb does not shrink it. Protect on allies floats higher at 260 units plus their fly height. The caster still uses Sorceress voice and Enchantress animations.

Protect's hidden AOz7 ability inherited Endurance Aura Targetart independently of the already-cleared BOr4 buff art. V11 explicitly clears that ability art. The managed native speed-scroll effect remains for the haste duration and is removed on expiry/death; haste amounts and healing are unchanged.

Ground line glyphs are replaced with soft 512px blue-green energy textures: directional wisps, expanding pulse, protective mist, and collapsing vortex. The existing radius rings and damage radii are unchanged. Shockwave adds an expanding energy burst, native Frost Nova and a cyan Monsoon strike at impact. New effects expire independently; the windup vortex still cancels on death/removal. Texture previews are in `audit/magic-ground-preview.png` and are not engine screenshots.

Orianna's projectile art is the native Necromancer missile. Core stats and combat values match this map's Lich (`U003`, roster 10), including scripted stat overrides: 17 STR (+1.7), 17 AGI (+1.6), 22 INT (+2.5), movement 310, turn rate 0.6, attack range 650, attack cooldown 1.8, damage dice 2d6 before intelligence, base HP 100 before strength, base armor 0 before agility, and matching regeneration/mana/sight. Presentation and spell cast timing remain Enchantress-specific. `lich-stats.json` captures effective reference values; `capture_lich_stats.py` records them from native data plus map overrides. Both object data and roster initialization use the same values, including debug recruitment at level 18.

Validation: 127 mocked lifecycle checks, 18 debug recruitment checks, model/texture round-trips, pjass, archive/object scope checks, and all-rank stat comparisons. In-game appearance/audio remain for the user's test. `orianna_v11.py`, `prepare_enchantress.cjs`, `make_magic_textures.py`, and `make_soft_ground.cjs` own this revision.

## Previous build: Orianna v10 (overhead orb and command ground effects)

The user found v9's orb too small and wanted it above Orianna. V10 removes the hand attachment and uses the existing control-ball position above its carrier: terrain plus carrier fly height plus 220 units, with the existing gentle hover. The effect scale increases from 0.65 to 2.0, just over three times the diameter, independently of hero-model scale. The same size applies during flight, while parked, and during Protect; its opacity and subdued particles remain unchanged. Travel trails scale proportionally. Cast animations, Sorceress voice and gameplay remain intact.

The existing radius rings are unchanged. Four original flat ground glyphs provide distinct command identities: green directional chevrons left behind Move; orange lightning spokes expanding with Attack's 0.25-second damage wave; a cyan protective crest at Protect arrival; and a purple inward spiral contracting and rotating during Shockwave's half-second windup. The marks fade, use no particle emitters, and are contained inside the relevant radius ring. Shockwave cancellation clears its spiral immediately. Travel marks are emitted at most once per 0.09 seconds.

`orianna_v10.py`, `command_ground.py` / `.j`, and `make_command_ground.cjs` own these changes. Ground models and color textures are self-contained and round-trip validated. `audit/command-ground-preview.png` is a geometry preview, not a Warcraft screenshot. Validation includes 120 mocked lifecycle checks, 18 debug recruitment checks, pjass, and archive verification. In-game appearance is left for the user's test.

## Previous build: Orianna v9 (Enchantress and Sorceress voice)

Orianna uses johnwar's Black Legion Enchantress V2 and its matching missile orb from https://www.hiveworkshop.com/threads/black-legion-mages-pack.337553/ . The hero model is preserved byte-for-byte, with its native portrait camera and textures. Voice is Warcraft's native Sorceress set. Credits are packaged alongside the model.

The persistent orb follows the model's right-hand attachment while home, so her movement and cast animations carry it. Move and Protect release it into world space at the 0.5-second cast point. An explicit spell-channel event selects Spell Attack for normal commands; Shockwave starts with Stand Channel then plays Spell Attack during its existing 0.5-second windup. Casting backswing matches the 1.533-second Spell Attack sequence. Attachment transitions destroy the previous effect and keep the same logical ball.

The matching green orb has reduced opacity and particle emission, without missile sound events or explosive death particles. Protect uses the same mesh with blue textures/tint, including when attached to an ally. Stationary trail copies fade over 0.25 seconds. Attack expands the orb by 18%; a detached orb also rises 20 units before settling. Native speed-scroll and priest-heal effects remain.

The v8 all-rank radius increase and v7 unlimited level-18 debug recruitment remain. `orianna_v9.py` and `prepare_enchantress.cjs` own the new presentation changes. Validation includes model round-trips, 110 mocked runtime checks, 18 debug checks, pjass, and archive/object scope verification. Warcraft visual/audio testing remains with the user; do not restart their game.

## Previous build: Orianna v8 (soft orb and attack gesture; superseded before installation)

The ball is now a custom 28-unit-radius matte sphere with a neutral silver-blue texture, ordinary alpha blending and looping Stand. It has no additive layers, particle emitters, lightning or lights. Protect tints the same effect blue. Flight afterimages use the same sphere at 0.32 scale and alpha 75, fading over 0.25 seconds. `make_soft_orb.cjs` generates the MDX and self-contained BLP1 texture, round-trips the model, and checks outward mesh faces and non-flashing material/animation settings.

Command: Attack makes the ball rise 20 units and expand by up to 18%, then settle within the pulse's 0.25 seconds; the control position and damage center do not change. Attack radii are now 207.9 / 225.225 / 242.55 / 277.2 / 311.85 / 346.5. Shockwave radii are 211.75 / 254.1 / 296.45. Each is 10% above v7 at the same rank, including object data, research/spell tooltips and visible boundaries.

`orianna_v8.py` owns these changes. The 98 Orianna runtime checks include the new gesture and updated all-rank damage boundaries; 18 debug recruitment checks remain enforced. V8 was packaged but superseded by the user's Enchantress request before installation.

## Previous build: Orianna v7 (Lich appearance and debug hiring)

V7 includes the v6 Lich appearance below and removes remaining debug recruitment limits. Debug activation opens aggregate/per-type hero quotas; purchased heroes stop consuming food and their tavern stock is immediately replenished after the sale completes. First, additional and random recruits reach level 18 after their base stats and growth values have been initialized. Repeated events do not duplicate levels or starter items, and the original primary-hero reference remains intact. Normal mode retains its previous limits and starting levels.

`debug_heroes.py` owns this patch; `check_debug_heroes.py` executes its handlers with mocked engine state. The 18 debug checks cover normal-mode isolation, quotas, food, level/stat initialization order, repeated recruitment, stock replenishment, primary-hero tracking, and cleanup. `Pack-Map.ps1` enforces these alongside the 94 Orianna checks, pjass and archive verification. Use `Install-V7.ps1` for the current build; it archives older Test maps. In-game testing remains with the user.

V7 is installed with matching SHA256 `6726931945cede27874b48cce6d33c867e5d8c87011a14ec0e9f60c2a9e1871d` in both Test folders. Local Documents/Test contains only v7. The active OneDrive/Documents/Test v5 file was locked by another process during installation and could not be moved; v5 remains beside v7 there pending release of the lock. Do not terminate the user's running Warcraft match to archive it. See `audit/installation-v7.json` for exact paths and pending cleanup.

## Previous build: Orianna v6 (Lich appearance)

Orianna now uses the downloaded `Lich.zip` model and matching icon by **HappyTauren**, with Warcraft's native `HeroLich` voice set. Model credit: https://www.hiveworkshop.com/threads/lich.88135/ ; icon credit: https://www.hiveworkshop.com/threads/btnlich.88137/ . The model includes a portrait camera and its required animations; all five texture dependencies resolve in the installed game. The original model bytes are preserved. Download provenance and model inspection are recorded in `audit/lich-source.json` and `audit/lich-model.json`.

Only Orianna's hero model, voice and matching icon fields changed from v5. All v5 ball/spell changes below remain in place. Use `Install-V6.ps1` to install v6 and archive older maps. Engine appearance/audio are left for the user's test; do not restart their match.

## Previous build: Orianna v5

- Command: Move and Protect leave stationary electric afterimages that shrink and fade over 0.25 seconds.
- Command: Attack releases a red ring expanding from the cast position over 0.25 seconds. Damage and slow follow its growing radius, hit each enemy once, and stop when expansion completes. Each cast owns its timer, hit list and center. The ring fades out by 0.375 seconds.
- Protect retains the same Farseer orb handle and model, tinted blue (65,145,255); it no longer selects the Priest missile/bird model. Casting Attack while protecting retains the blue orb.
- Allied haste immediately attaches the native Scroll of Speed `SpeedTarget.mdl`, persists through refreshes, and cleans up on expiration/death. The automatic buff art is empty to avoid duplicate effects. Healing uses the native Priest `HealTarget.mdl`; healing amounts and arrival timing are unchanged.
- Command: Attack radii: 189 / 204.75 / 220.5 / 252 / 283.5 / 315. Shockwave radii: 192.5 / 231 / 269.5. These are 30% smaller radii at every level; object data, spell descriptions, research tooltips, visuals and damage use the reduced values.

Validation: pjass and 94 mocked runtime checks pass. These include all-level radius boundaries, pulse timing and single hits, concurrent casts with distinct casters/damage/centers, stationary trail fading, haste refresh/expiry/death, and existing ball lifecycle behavior. Native models were verified against installed Warcraft data. Full packaged validation is recorded in `audit/verification.json`; installed copies are recorded in `audit/installation-v5.json`. The user is testing in Warcraft; do not control or restart their game.

Rebuild with `build.py`, then `Pack-Map.ps1`. The v5 patch lives in `orianna_v5.py` and `orianna_v5.j`, applied after the v4 patch. `Install-V5.ps1` installs the verified release in both Warcraft Test folders and archives older maps.

## Previous follow-up: native orb rendering (v4)

The v3 ball remained invisible in the user's Warcraft test despite functioning spells. This was reproduced in the running game with Command: Move; the earlier WebGL preview did not validate Warcraft's unit-model rendering.

V4 separates the visible orb from its control unit. A persistent native Farseer missile effect (normal) or Priest missile effect (Protect) follows the control unit in world space, using terrain elevation plus its scripted flight height. The control unit has a blank model. Effects persist while idle, follow flight and carriers, switch on Protect, and clean up on death/removal. Existing spell mechanics and feedback remain intact.

V4 passes pjass, 43 mocked lifecycle checks and 1,375 archive checks. Both installed hashes match `bba6964619cc3955fe041d8ba1135cc35a1b1975523aa1f8c34fa28cf0da14e2`. V4 is the only map directly in both Test folders; v3 is archived. **V4 has not been playtested in Warcraft. The user elected to test it themselves; do not restart or control their game.**

The following v3 record describes the earlier unsuccessful unit-model approach, not proof of the v4 fix.

## Orianna presentation repair â€” October 28, 2026

- Register the ball on tavern purchase and hero ownership change, in addition to entering the map and casting. Registration remains idempotent, and neutral showroom heroes remain excluded.
- Repair both orb models with explicit opaque idle/portrait keys, full root scale during idle, and a nonzero model bounding radius. Preserve their existing animation, geometry and blue/gold appearance. Package all ten textures as Warcraft BLP1 files, removing the need for legacy texture-name resolution. Clear extreme unit pitch/roll values and explicitly restore scale and vertex alpha when locking the ball.
- Move: electrical travel/audio, per-enemy impact, arrival flash/audio, visible slow buff.
- Attack: existing red radius ring and impact audio, plus flashes on affected enemies and visible slow buff.
- Protect: distinct travel/audio, green arrival radius ring, heal sound, heal flashes on allies, and a persistent haste aura tied to the existing buff duration.
- Shockwave: subdued exact-radius telegraph and charging sound for the 0.5-second windup, then the existing bright cyan ring, impact sound and victim flashes. Windup effects are cleaned on impact, return, death, owner change and removal.
- Leash/invalid-carrier/timeout return: cosmetic recall flash and sound. No damage, healing or haste is added by returning.

The original feedback models and sounds were present in the MPQ but absent from its listfile. Initial directory-only extraction therefore incorrectly suggested missing assets. The revised build reads membership by filename hash and preserves unlisted files, including the map's skin object tables. The installed game also provides the old orb texture names as DDS replacements. Those observations do not prove an engine-side texture fault; packaging the textures makes the repaired models self-contained. Exact live root-cause reproduction remains pending.

Validation: pjass passes; 35 translated-JASS lifecycle tests pass; 1,375 archive/asset/scope checks pass, including 1,281 untouched archive entries preserved byte-for-byte. Both repaired ball variants and the Attack/Shockwave rings render with packaged textures in the WebGL preview (`audit/orb-preview.png`). This is not a Warcraft engine test. Live visuals, sound mix, buff behavior, and multiplayer testing remain pending.

For the next Warcraft test: select **FF799X - Orianna v4** in Test; buy Orianna and inspect the ball before learning/casting; test Q travel/arrival/slow, W ring and hits, E on a moving ally/heal/haste, and R windup/pull. Then test leash return, death/revival, and commands during flight. Listen with spell sound enabled. An already running match continues to use its loaded map.

Rebuild with bundled Python running `build.py`, then run `Pack-Map.ps1` (runtime tests, pjass and archive verification are enforced). `orianna.py` owns the script patch; `repair_orbs.cjs` uses the pinned `war3-model` dependency under `tools/model-tools`. Committed inputs are in `assets`; `prepare_orianna_assets.py` recaptures them from the original map and installed Warcraft data when needed. `verify.py` checks every MPQ entry, including unlisted entries and legacy compressed blocks. `audit/verification.json` records the release hash. Authoritative custom runtime is war3map.j; inherited World Editor trigger sources are not synchronized and saving through World Editor can replace runtime code.

## Proposed opening auto-spawn formation (not implemented)

Assumption: the requested auto-spawn is Mini Foots-style opening mass staging. Later automatic reinforcement waves are a separate choice.

The existing 12-player spawn function creates each player's units at their base. Mass start orders footmen toward the central battlefield and casts automatic roar at the player starts. A formation port must update both staging and mass release, including roar placement and mass movement speed.

Use one continuous front per team, following its two inward-facing edges. Use a shallow staggered band, roughly two footmen deep on the outer sections, tapering to a single row around the central bend to leave more room near shops. Keep each player in a separate contiguous section for ease of control: one on each outer section and the middle player around the corner. Preserve each player's actual footman count. If a teammate is absent, distribute the remaining units over the same usable front rather than leaving that player's section empty. Do not import Mini Foots' 1.5x count multiplier.

The latest diagram uses 65-unit spacing along each rank, a half-step stagger, 50 units between outer ranks, 75 illustrative footmen per team, and a 130-unit gap between opposing fronts. The central 11 footmen per team form a single row; remaining units occupy the outer sections. Check unit collision and terrain in game before adopting those dimensions. Connect each team's two edges at the corner and mirror every team's geometry. Distribute the actual footman count along the complete walkable front, preserving the single-row central section and allocating extra depth toward the outer sections. Validate all positions against terrain and buildings, shifting blocked points along the front instead of stacking units at a fallback point.

Stage units hidden, paused, invulnerable and without collision before mass, then restore ordinary state together. Apply roar across the formation with coverage of both edges. Use attack destinations distributed across the opposing front; sending every unit to the same center point would quickly recreate a clump. Restore existing player orders and reinforcement behavior after the opening deployment as appropriate.

Before adoption: compare all four teams with full and missing-player lobbies, odd counts, different mass modes, corner congestion, buff coverage, mirrored travel distance and the first several seconds of contact. Confirm deterministic multiplayer positioning and preserve no-mass mode behavior.


## Orianna v13 â€” Mini Foots UI sync
Carries the Mini Foots v5 minimap-anchored zoom and Stats UI, including removal of the panel title and footer and an X close button. The Stats panel retains all 12 players. The v12 Orianna and Gragus changes remain. Hero runtime checks, pjass and archive verification pass. Installed and hash-verified in both Test folders. Live UI and hero testing remain pending.



## Current v14 working base
Power Orb by Kitabatake: https://www.hiveworkshop.com/threads/power-orb.48602/ . Persistent Stand animation, finite Death cleanup, and no recreation on Protect tint changes. Test heroes disabled except Orianna and Gragus. Preserves the 799X layout, latest hero/UI/zoom code, and current working item data. JASS compilation, 127 spell lifecycle checks, 18 recruitment checks, 35 Gragus checks and full archive verification passed. Live game testing pending.


## v15: smaller Power Orb
The entire persistent orb effect is scaled to 60% of v14 size, including its surrounding particles and death effect. Gameplay radii remain unchanged. Compilation, lifecycle tests and archive verification pass; in-game appearance awaits testing.


## v16: Guardian sun orb
Orianna now uses the existing SuperLightningBall model from Guardian Time Spiral at 0.60 scale. Uses looping Stand and its finite 0.5-second Death animation. Guardian spell and gameplay radii are unchanged. Compilation, lifecycle and archive checks pass; live appearance pending.
