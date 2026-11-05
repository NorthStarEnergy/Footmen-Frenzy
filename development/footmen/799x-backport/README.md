# 799X Orianna, UI and Gragus backport

Latest prototype: `release/FF799X_Rx_Veigar_v33.w3x`, based on Mundo v32. Type `-veigar` to summon a temporary hero with Event Horizon (E) and Dark Matter (W). Build, behavior checks and notes: `../veigar-prototype`. JASS compilation and archive preservation pass; live testing is pending.

## Historical v31 notes

Current release: `release/FF799X_Rx_HeroTooltips_v31.w3x`, installed in both Warcraft `Maps/Test` folders. Guardian, Orianna and Gragus now have concise, colored and rank-specific command and research descriptions; their hero selection descriptions and Gragas's barrel recast text are also refreshed. Shared Dark Passage text identifies Guardian-only effects explicitly. The late tooltip initializer runs after existing overrides; underlying ability mechanics and object fields are preserved. Source and verification: `../hero-tooltips`. All 63 skill ranks, native costs/cooldowns, hero level requirements, runtime damage/healing values, JASS compilation and archive preservation were checked. Live in-game layout verification remains pending.

## Historical v30 notes

Current release: `release/FF799X_Rx_GuardianLantern_v30.w3x`, installed in both Warcraft `Maps/Test` folders. Guardian's grounded lantern stuns enemies for 0.5s on entering its 130-unit area; they may be stunned again after leaving and re-entering. Other allied units within 65 of the grounded chain receive 10 HP on entry and 20 HP/sec while present, plus a 20% slow for 1 second on entry. Guardian is excluded because he anchors the chain rather than crossing it. A passenger stuns each eligible enemy hero intersected during the pull for 0.5s; swept-segment checks avoid missing fast crossings. Effects apply only to Guardian's use of the shared lantern ability. Source, build and collision/lifecycle checks: `../guardian-lantern`. JASS compilation and archive preservation pass; live testing is pending.

## Historical v29 notes

Current release: `release/FF799X_Rx_GuardianChannel_v29.w3x`, installed in both Warcraft `Maps/Test` folders. Guardian Shield is an immediate on/off toggle: drain starts at 30 mana/sec and grows by 5 mana/sec per second, capped at 130; healing, mana restoration, mana burn and damage scale by 5% per second to double after 20 seconds. At 5 mana or below it stops; the cooldown is five seconds after shutdown. The Guardian receives normal mana restoration from the dome. Edge-projecting beams and orbiting wisps were removed, and dome alpha is cleared before destruction. Time Warp now marks and damages each eligible enemy once, then stuns surviving marked enemies on arrival for 0.25 + 0.25 seconds per rank. Independent per-orb hit groups and effects clean up on impact or caster removal. Source, build and behavioral checks: `../guardian-channel`. JASS compilation and archive preservation pass; live testing is pending.

## Historical v28 notes

Current release: `release/FF799X_Rx_Guardian_v28.w3x`, installed in both Warcraft `Maps/Test` folders. Guardian's Force Field no longer grants or displays Detonate; fields expire on their existing timer. The affected tooltips were updated, and burst behavior, JASS compilation, object scope and archive preservation were verified. The current incremental source/build/verification scripts are in `../guardian-no-detonate`. Live testing is pending.

## Historical v27 notes

Current release: `release/FF799X_Rx_OriannaAudio_v27.w3x`. Installed in both Warcraft `Maps/Test` folders. Orianna's Attack pulse plays the native `StasisTotemDeath` sound at the ball; Move uses `FaerieDragonLaunch`. Both Move and Protect travel at 1,320 units/sec (+10%). Move's cooldown is 6 seconds at every rank (was 8), including active and research tooltips. Source and build/verification scripts are in `../orianna-audio-v27`; 134 mocked lifecycle checks, JASS compilation, object-scope checks and unchanged-archive verification pass. Live sound/visual testing is pending.

## Historical v26 notes

Current release: `release/FF799X_Rx_HeroPolish_v26.w3x`, installed in both Warcraft `Maps/Test` folders. The current incremental source/build pipeline is `../hero-polish/build.py`, `../hero-polish/pack.py`, and `../hero-polish/Install.ps1`; generated source is `../hero-polish/799x/src`. Earlier instructions below reproduce historical builds.

v26: Guardian fields use deeper blue, scale 0.70875 (+5%), and matching 75.6 pathing radius. Gragus turn rate is 1.0, with zero orientation interpolation and a deferred, interruptible Spell Drink animation after X completes. Orianna X/V radii and V pull speed are multiplied by 1.25. Fixed ground rings are removed in favor of feathered expanding energy fields for pulse, Protect, and Shockwave, with softer travel marks. Buff/damage values and pull collision guards are unchanged. Runtime/editor compilation, lifecycle harnesses, exact modified-file readback, and unrelated archive preservation pass; live Warcraft visual testing is pending. See `../hero-polish/799x/verification.json` and `../hero-polish/delivery.json`.

Release: `release/FF799X_Rx_Gragus_v24.w3x`. In-game map title: **FF799X - Gragus v24**.
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


## v17: softer blue orb
Normal orb uses the previous Protect tint (65,145,255). Protect now uses a deeper blue (30,90,255). Size and gameplay unchanged. Compilation and regression checks pass; in-game color testing pending.


## v18: Fortitude rebuild
Replaces the self-only Devotion Aura with six fixed-rank item armor modifiers (+5/7/9/11/13/15). Correct-rank targeted cosmetic Inner Fire buff is cast after setting its level, with no additional armor/damage/regeneration. Recast, expiry, death and removal clear modifiers. Healing and magic reduction retain five-second duration. Compiler and mocked checks pass; actual engine armor/buff behavior still requires live testing.


## v19: Guardian kit and rapid forcefields
Guardian is available in the roster again. Z retains Time Warp. X uses a new Channel-based Force Field with a distinct forceofnature order (the old Carrion Swarm base conflicted with Dark Passage). Five individually aimed placements within four seconds, a 0.10-second recast interval, then a 30-second cooldown on exhaustion or window expiry. Cost: 25 mana per field. Guardian cast point/backswing: 0.05 seconds. One SC2 forcefield at each click, scale 0.90 versus the previous 0.30; pathing creation/removal both use radius 96. Field duration remains 3/3/3.5/4/5/5 seconds. Existing detonation/expiry behavior remains. Fixed a leaked caster location; initialize field storage on cast as well as learning.

C uses the existing six-rank Dark Passage lantern without changing Twisted Fate's spell. V is Guardian Shield, replacing Time Spiral: ultimate ranks at levels 6/11/16, cooldowns 60/45/30 seconds, 100 mana. Existing moving 600-radius dome lasts 15 seconds, heals allies for 100 HP and 10 mana per second, slows enemies 60%, and burns up to 20 mana per second with equal spell damage. No projectile blocking. Removed innate dome from gameplay and skin object tables.

Replaced C: Psionic Storm, 250-radius storm for four seconds, 120-320 total magic damage, up to 60-160 mana drained, 30% slow. Replaced ultimate: Time Spiral, a sun orb with magnetic pulling and an area explosion. Z Time Warp remains a non-damaging displacement orb, traveling 700-1200 units by rank and disrupting enemies within 280 range.

The reproducible patch is guardian.py. check_guardian.py executes translated JASS burst functions for exhaustion, timeout, concurrent casters and new bursts, plus spell-slot/order/targeting/footprint checks. The packer enforces these, existing hero regressions, pjass and archive verification. Warcraft visual/casting playtesting remains pending.


## v20: Guardian Shield visual feedback
Visual-only update: dome rotates gently and shimmers in opacity, with three blue energy wisps orbiting above ground. The existing dome model, scale and gameplay radius are retained. Allied units covered by restoration carry a blue Inner Fire marker and pulse when missing health or mana. Affected enemies carry a purple curse marker and pulse only when mana is actually burned. Pulse effects are throttled to once per 0.75 seconds per unit and polarity, rather than spawned every 0.05-second combat tick. No additional buffs modify stats.

Coverage aggregates across domes before removing stale markers. Friendly and hostile coverage can coexist without effect recreation each tick. Exit, death, removal and final dome expiry clear markers; dome stop clears its three wisps. Existing damage/heal/mana code is verified unchanged. Translated JASS lifecycle tests cover effect reuse, overlapping coverage, exit, death, expiry, pulse throttling and orb cleanup. Runtime tests and JASS compilation pass; archive validation is enforced by the packer. Warcraft visual testing remains pending.


## v21: Guardian projects the dome
Three soft blue DRAM energy tethers originate at Guardian's chest (terrain plus fly height plus 100) and terminate on the dome shell, alternating irregularly between sides and top. Each fades over a 1.2-second cycle with staggered phases and a maximum 26% alpha; endpoints change at the dim part of the cycle. Endpoint directions use deterministic variation without consuming gameplay RNG. The shell approximation uses the imported model bounds: radius 600, center 41 below the ground reference. Both ends follow Guardian every shield tick. Each caster owns three reusable lightning handles; all handles and endpoint state clear when the dome stops. Existing dome wisps and allied/enemy visual feedback remain, and combat calculations are unchanged.

Validated the native DRAM entry in installed Warcraft LightningData. Added translated-JASS tests for alpha bounds, shell endpoints, chest position with terrain/flying height, movement, handle reuse, endpoint variation, simultaneous casters and cleanup. Compilation and existing regressions pass; archive verification is enforced by the packer. In-game appearance remains pending.


## v22: Gragus animations, based on Guardian v21
Adds Spell Drink index 12 (1.6 seconds), restores Spell Slam index 9 (0.5 seconds), and explicitly uses Spell Throw index 11 for barrel spells. Keeps original geometry and textures. Drink is previewed as geometry; live Warcraft transition testing pending. Compiler and regression checks pass. Latest Guardian v21 changes preserved.


## v23: Barrel Roll targeting circle
Enables Channel targeting image on AGr1 and sets its radius to 260 at every rank, matching both automatic and manual explosion damage searches. Gameplay values unchanged. Archive validation passes; in-game cursor appearance pending.


## v22: cast ranges, random dome bolts and raised buttons
Corrected Guardian Channel real/unreal object-field types using installed Warcraft AbilityMetaData: range, area, cooldown and Channel timing fields require type 2 (unreal). Explicit all-rank cast ranges: Z Time Warp 1200, X Force Field 900, C Dark Passage 1000. V remains a self-cast dome with radius 600. Force Field model scale 0.90 -> 0.675 and pathing radius 96 -> 72, both 25% smaller. Projection strands now peak at 55% alpha, up from 26%.

While the dome is active, every 0.75 seconds it selects up to one random eligible ally and one enemy in its 600 radius using synchronized reservoir sampling. Allied hits restore 25/30/35 HP by ultimate rank and 10 mana, capped at maximum, and apply +10% movement speed for 1.5 seconds. Enemy hits deal 25/30/35 magic damage, burn up to 10 mana, and apply 15% movement slow for 1.5 seconds. Existing dome restoration, burn and 60% slow are preserved. Structures, dead, locust, invulnerable and magic-immune units are excluded from new bolts. Native Bloodlust/Slow dummy casts carry custom buff icons/tooltips; Bloodlust has zero attack speed and scale modification. No permanent movement-speed writes. Bolts last 0.35 seconds, follow target movement and clear on death/expiry/dome stop. Both positive and negative bolts use the Mana Drain visual, tinted teal/purple.

Four new Guardian active-button icons generated using built-in image_gen: Time Warp, Force Field, Lantern, Guardian Shield. Raised metallic frames applied to existing Orianna and Gragus artwork, preserving their subjects. All 12 main ability icons have opaque 64x64 BTN and dark DISBTN BLP1 exports with complete mipmaps and matching research icons. Sources and prompt summary: icon-sources/. Preview: audit/ability-buttons-v22.png. button_icons.py reproduces exports using the existing BLP encoder; no external download is needed.

check_guardian_bolts.py covers all ultimate ranks, resource caps, exclusions, empty selections, buff orders, lightning expiry/cleanup, typed all-rank ranges and 24 button assets. Existing hero and projection tests remain required. In-game cast-distance, speed-buff and visual confirmation remains pending.


## v24: Barrel presentation
Z barrel scale 1.15; ultimate barrel scale 1.45 with red tint and additional orange-red impact explosion. Native Pandaren Brewmaster Warcry1 plays as a positional sound on ultimate release and cleans up after playback. Damage, radius and timing unchanged. Compile, mocked presentation and regression checks pass. Live visual/audio testing pending.

Guardian v22 changes were integrated with concurrent Gragus updates into the verified combined release **FF799X - Gragus v24** (FF799X_Rx_Gragus_v24.w3x). SHA256: 64c6555509affde8ef6eb7539ec82e19150ca718faa472c9ac08700ea7bef76e. Installed and hash-checked in both Test folders; see audit/installation-guardian-update.json.


## v25: standard Warcraft III icon borders
Release: FF799X_Rx_WC3Icons_v25.w3x; title FF799X - WC3 Icons v25. Uses the exact standard bm_btn.tga and bm_disbtn.tga supplied in Shadow Daemon Button Manager v1.8.2 from Hive Workshop. Applied the documented equal-RGB multiplicative shading rule and default shading; no custom frame. Removed the generated Guardian frame with a 10% artwork crop on each edge before resizing. Orianna/Gragus use their saved original artwork. All 24 BTN/DISBTN exports retain opaque BLP1 and mipmaps. Incremental packaging modifies only these icons and the map title; gameplay is byte-identical to Gragus v24. Preview: audit/ability-buttons-wc3-default.png. Source: https://www.hiveworkshop.com/threads/button-manager-v1-8-2.116280/ .

