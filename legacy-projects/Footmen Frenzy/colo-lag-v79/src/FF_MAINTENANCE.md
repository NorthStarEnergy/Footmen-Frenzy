R5: Arcane Vault Mira brew purchase hotkey C. Restore native hotkeys and command-card positions for all 13 affected abilities, including every purchased spell. Remove spell-item purchasing, learning and debug-spawn paths. Preserve R4 modes and balance.

R6 portrait audit: Gron uses its imported DragonboneGolem_Portrait; Demolisher uses the portrait camera embedded in its actual Catapult_V1 model. Death Knight SD inherited art and dependencies resolve; reported black portrait requires in-game reproduction. R5 gameplay, hotkeys and source unchanged.

R7: newly spawned hfoo/h060 during actual mass receive 30% movement speed for six seconds; original speed restored by per-unit timer. No boost before/after mass or in no-mass mode; no retroactive boost at mass start. Orders and all other balance preserved.

R8: All living existing Footmen receive the same six-second +30% boost at mass start, including autosend-off players. R7 spawn boost retained. Previous behavior superseded: R7: newly spawned hfoo/h060 during actual mass receive 30% movement speed for six seconds; original speed restored by per-unit timer. No boost before/after mass or in no-mass mode; existing Footmen now boosted at mass start. Orders and all other balance preserved.

R9: Alchemist Chemical Rage uses the current hero-level bounty table with zero random dice. Refresh on cast and before damage to prevent alternate-form bounty overrides determining a lethal hit payout. Native gold payment and team bonus remain unchanged. No fixes to other reported hero/spawn credit issues. Engine verification pending.

R10: Custom kill credit accepts dead valid enemy player-owned sources while retaining null, removed-source and slot guards. Enemy Objection dummy lives for the maximum actual ANso normal/hero duration plus two seconds; allied branch unchanged. Native XP and bounty untouched; R9 Alchemist correction preserved. Engine reproduction remains pending.

R11: Hill unit always remains Neutral Passive after capture/reset. Logical controller, income, level, protection timer and controller glow remain unchanged. Based on user-confirmed R10. Engine targeting/playtest pending.

R13: Debug mode starts the hill setup timer at 10 seconds after gameplay starts. Normal timing and disabled KOTH unchanged. Based on R11 with the original small hill target; no R12 model changes. Neutral ownership and shopping geometry preserved.

R14: Debug Mode is available to the host in the initial game-type dialog. Uses existing debug setup and AP vote completion to start gameplay once, with R13 debug hill timing. No hill/shop geometry changes.

R14 Debug30G: Hill control resets after 30 team gold earned in debug mode; normal reset threshold remains 300. Existing neutral reset logic, debug menu, 10-second spawn and original small hill target preserved.

R14 RacialShared: Completing Human, Orc, Night Elf or Undead racial research synchronizes all four to the highest completed allied tier, including the researcher. Existing race-specific unit bonuses and all unrelated systems preserved.

R14 RandomHero: Restores free clickable Random Hero in hero taverns after every game-mode startup including AFK Pub fallback and AP. Uses existing mode-aware random pool and hero entry initialization; prevents additional heroes. Shared racial upgrades retained.
R14 RandomRestored: carry tavern Random Hero H0R0, global initial-seed exclusion, team category 5/11/12 locks and bonus Boots of Speed. Edit WCT and generated JASS together.


R14 RandomRestored Heroes: Orianna and Gragas in roster 92/93. Gragas W drinks for 5 seconds of armor, magic resistance, and healing; E passes allies and stops on enemies or buildings. Orianna Command: Move radius reduced 10%, Command: Attack radius reduced 10%, and Shockwave radius reduced 45% at all ranks. Guardian has innate D Guardian Dome. Rx level cap remains 18.

Global Silence: one-use scroll IGs1, 1000 gold, Personal Shops n007, stock 1/restock 120s. Global persistent Cloud silence plus Tornado aura and spell-channel guard; source survives caster death, covers new spawns, duration 120s; same owner refreshes and different owners overlap independently. Engine tests pending.

Rx hero progression v1: level cap 18 retained; Orianna INT/Archmage stats and Gragas STR/Tauren stats synchronized with central assignment; basics 6 ranks at 1/4/7/10/13/16, ultimates 3 at 6/11/16; QWER learn / ZXCV cast; positive rank-based mana costs; Gragas damage extended to rank 6 with 500 damage capstone comparable to Thunder Clap. Existing Orianna rank damage, mark payoff and reduced radii preserved. Drunken Fortitude uses native self-only bonus-armor aura, six descriptive buff ranks, model animation 9, persistent imported effect and explicit expiration/death/refresh cleanup. Engine test pending.

Global Silence direct-use fix ported onto Rx Hero Progression v1. Existing IGs1 item and silence abilities/object data retained. EVENT_PLAYER_UNIT_USE_ITEM checks GetManipulatedItem type and starts the existing 120-second global field. Rx hero progression and all other map changes preserved.

Rx Carry Heroes v1: Orianna (HOr1, slot 92) and Gragas (HGr1, slot 93) moved from category 3 to middle Carry category 15 (fourth of categories 12-18). Existing SD Carry tavern routing, Carry locks and AP tavern 9 stock retained. Hire tooltips label Carry Tier. HeroIcons v1 baseline preserved.

LoadTrace v1 DIAGNOSTIC ONLY: preserves gameplay, writes last startup checkpoint to CustomMapData/ff_rx_startup_trace.txt. Not a verified fix. Original CarryHeroes v1 remains unchanged.

Rx RC6Bot v1: RC6 format-2 bot reporting, host auto-Pub and observer vision ported onto LoadTrace v1; Rx gameplay, objects, source and diagnostics retained. TEST: engine/bot validation pending.

Rx Hero Balance v2: user-requested Gragas and Orianna damage, cooldown, healing and magic-reduction changes; Orianna mark runtime, globals, ability and buffs removed. Ball movement, haste, slow, pull, stun, knockback, mana costs, hero stats and RC6 bot systems preserved. Static verification only; inherited startup investigation remains unresolved.

Orianna Red Attack v1: AOz2 red icon; crimson/black ground nova at ball coordinates, scaled to rank radius, destroyed after 1.5 seconds. Visual only: damage, slow, cooldowns, mana and every other spell preserved. Dark Lightning Nova derivative credit: JetFangInferno, https://www.hiveworkshop.com/threads/dark-lightning-nova.65965/. Engine playtest pending.

Hero Balance v3: Orianna Move damage 60/90/120/160/200/225, cooldown 8s all ranks; Protect travel damage 30/50/75/100/125/150; Gragas Barrel Roll rank 6 damage 550. Tooltips synchronized. Red Attack icon/ground effect and all other gameplay retained. Engine test pending.

Hero Tooltips v1: clean current-rank cast tooltips and initialized rank-specific learn tooltips for all 42 Orianna/Gragas ranks; clarified Detonate Barrel. Final HeroBalance_v3 gameplay and red Attack assets preserved. Engine UI testing pending.

Demon Knight v1: HDk1 roster 94, category 8 matching Monkey King. Strength bruiser: returning axe, cooldown-gated Pulverize, caster-specific Blood Tithe marks, interruptible global enemy-hero Dread Requiem. Six basic ranks and three ultimate ranks; QWER learn / ZXCV cast. Tarrasque Demon Knight model and portrait imported. Inherited startup issue unresolved. Static verification only; engine playtest pending.

Demon Knight v2 polish: swept axe collision, faster crimson return and collision-safe nonstacking pulls; Pulverize lethal-hit eligibility and native cooldown feedback; readable private mark counts, staged crimson impacts, atomic Tithe consumption with healing feedback and empty-cast refund; Requiem overhead countdown, atomic global impact and empty-cast refund. Damage/rank/stat balance preserved. Only DK runtime and four spell objects changed. Inherited startup issue unresolved; engine/visual/multiplayer proof pending.

Guardian Force Field AFOR: three placements in a two-second window, then twelve-second cooldown; mana per placement. Existing field behavior and shield ultimate preserved. Engine playtest pending.

Guardian Force Field: radius 32, visual scale 0.30, segments 2/2/3/3/4/4 at 64-unit spacing. Guardian Force Field AFOR: three placements in a two-second window, then twelve-second cooldown; mana per placement. Existing field behavior and shield ultimate preserved. Engine playtest pending.

Guardian Psionic Storm replaces Enchanted Aura in third hero slot. Four-second, 250-radius storm: damage, 30% slow, mana burn; six ranks. Force Field v2 and dome ultimate preserved. Engine playtest pending.

Guardian Time Warp: zero-damage fixed-direction disruption orb, distance 700/800/900/1000/1100/1200, proximity-based swirl and facing changes. Legacy damage/explosion disabled. Psionic Storm, Force Field v2 and shield retained. Engine playtest pending.

Detailed player stats v1: local Player stats toggle below original team multiboard, 12 rows with hero icon/name, unit kills, units fed to enemies, hero deaths, hero assists (enemy damage within 10s before allied hero kill), hero kills, actual hill captures, hostile building kills, landed Transmutes and current hero level. Refresh 1s. Frame geometry and multiplayer require engine playtest.

Player-bound inventory items v1: first real hero pickup binds the individual item to its player. Same-player heroes and couriers may transfer items; other players drop rejected pickups before recipes/limits run. Dropping retains binding; pawning clears it. Instant-use powerups remain unchanged. Existing hero inventories bind at initialization. Item custom values are reserved for binding (previously unused). Original DetailedStats v1 systems retained. Engine and multiplayer playtest required.

Demon Knight v3 playtest corrections: Z range 700 for 800 travel, return pull up to 640 with a 100-unit caster gap and dynamic direction; no Strength scaling in any DK ability; C light-red Destroyer devour burst and Spell animation; V native three-second Starfall channel shell with zero native damage, finish-event global enemy hero impact, cancellation on interruption. All unrelated gameplay and item binding preserved. Exact original in-engine short-cast cause unconfirmed. Engine visual and multiplayer playtest pending.

Orianna Feedback v1: paused Locust ball with protection reapplied after skin/show, double ball object scale, scripted parked/overhead hover; Move and Protect trails and travel-hit flash; exact-radius red Attack ring and cyan dramatic Shockwave ring with ground impacts; original packaged 3D PCM command sounds. Preserves spell balance, DemonKnight v3 and unrelated systems. Engine visual/audio/multiplayer playtest pending.

Demon Knight v4: reliable long-range point axe, 1200 flight, fast outbound/slow return, linked smooth rank-scaled pull with 100 gap and no slow; blood impact; permanent local-visible mark counters; dramatic Tithe ground burst and draining beams; timer-owned three-second paused channel with verified model sequence 7, darkening overhead enemy spheres and sky lightning impacts. Native finish/end events cannot cause early damage. Orianna Feedback v1 and all unrelated gameplay preserved. Engine/multiplayer verification pending.

Classic Mundo v1: HMu1 roster 95, category 15. Innate 0.3% max HP regeneration; health-cost cleaver using Troll missile engine/art with first-hit slow; toggle burn plus user-selected native spell resistance; five-second missing-health attack boost; twelve-second health regeneration and movement ultimate. Six basic ranks / three ultimate ranks. SuPa- HeroAbomination model and texture, unmodified files with purple unit tint. Preserves Orianna Feedback v1 and Demon Knight v4. Engine and multiplayer playtest pending.

TestSilenceBall v1: test mode unlimited HERO cap and 300 food, extra tavern recruits retained without replacing primary hero, no test-mode showroom kill or death cap reset; Global Silence native Roar item activation and repeating native Silence every 0.25 seconds for existing 120-second field, with persistent global aura visual and channel guard; Orianna ball unpaused with explicit looping stand animation, Locust/zero movement/double size retained. Demon Knight v4, Mundo v1 and unrelated gameplay preserved. Engine playtest pending.

Main Heroes v1: reconciles tested Twisted Fate v1 and Mundo v1 into the TestSilenceBall v1 main lineage. Mundo remains hero 95/category15; Twisted Fate is hero96/category3. Both recruited in AP and shared SD/random registry. Exact TF kit/module and object values preserved, with unique TFP namespace and TFLN chain assets. Keeps latest multihero test mode, 120-second persistent global silence, visible Orianna ball, Demon Knight v4, Guardian/items/scoreboard and all unrelated gameplay. Engine playtest pending.

Hero Tavern v1: Twisted Fate uses the standard ranged Agility attribute profile, native base health/mana/armor, normal acquisition/collision/turning, six-rank basics at levels 1/4/7/10/13/16, and three-rank Destiny at 6/11/16. QWER learn and ZXCV cast keys; complete rank tooltips and sixth-rank Red/Gold dummy debuffs. Mundo retains health-cost kit and tank attributes, with native tavern base HP100 and base damage0. Fixed eight unique slots in final AP tavern, Mundo row2 column3 and TF row2 column4. Existing roster95/96 and category15/3 preserved; TF central stats synchronized. All unrelated gameplay, latest Orianna/Demon Knight, test-mode and silence fixes preserved. Engine playtest pending.

v54: Stats moved down; padded close button; gameplay leaderboard clock enabled; five-digit mine gold width; floor mode selectors removed and host hero-selection dialog used. Recovered authoritative editor runtime from v53 executable script. Warcraft visual, gameplay and editor-save tests pending.

v56: Veigar Event Horizon uses five translucent Guard stone-wall effects with pentagonal swept-contact stun detection; no pathing blockers. Existing stun ability, duration, targeting and Dark Matter unchanged. Engine playtest pending.

v57: Veigar cage visual polish: five violet translucent walls, luminous pentagon rims and corner pillars, gentle synchronized pulse and final fade. Collision, stun, duration and other spells unchanged. Engine visual playtest pending.

v58: Confirmed-stun overhead stars and STUNNED marker; Dark Matter now drops a dark smoky orb with accelerating descent and dark nova impact. Frost Nova removed. Existing delay, damage, radius, cage and stun duration preserved. Engine visual playtest pending.

v59: Orianna/Guldan visual amplification: attack pulse 1.6x, protect ground 1.5x and healing 2x, Shockwave windup 1.6x and burst 1.8x; ground alpha 225, travel trails/hits 1.6x and arrival flash 2x. Visual-only; combat values, timing and lifetimes unchanged. Engine playtest pending.

v60: Standardized colored rank-specific learned/research tooltips for Guldan, Gragas, Twisted Fate, Guardian and auxiliary buttons. Fixed stale TF Destiny/card timings and Guardian bolt values. Object text and runtime synchronized; no balance changes. UI playtest pending.

v61: Reviewed startup and new hero spell lifecycles. Fixed hero-selection vote borrowing an unrelated timer dialog: create its own countdown and destroy it on vote expiry. Engine playtest pending.

v62: Normal Pub pooling unlocks 30 minutes after game start; lifetime 5000 gold per sender/ally through -pool or F3. Native trading remains locked so cap applies; pool_out/in and given/recv reporting include actual scripted transfers. Tier-1 item-price request needs confirmed intended values. Engine/multiplayer tests pending.

v63: correct recipe and total gold descriptions for Ninja Stealth Cloak, Guardian Shield and Ring of Titans; prices, craft mechanics and all other data unchanged. Unused undefined shop rawcodes not repaired. Actual UI test pending.

v65: Restore neutral-tavern buyer units after dialog startup, for all active AP players and team-specific SD/Carry taverns. AR direct assignment unchanged. Preserve v64 Mundo cloud fix. Runtime and WCT synchronized. Engine playtest pending.


v66: Base SD taverns, Human Carry Altar, team-wide 3-use Random, public F9 draft archive, dynamic AP roster bound, compensated spawn attack range. Runtime and WCT synchronized. Engine playtest pending.


v67 Pub XP TEST: normal Pub with mass and colossals only. Existing below-4 200% catch-up now expires per hero; below-6 150% after first level 6 or mass end; from first colo spawn below-7 200%; level 7+ 70%. Native kill XP and scripted unit supplements use the rate. Footman supplement extends to below 7 after first colo and no longer expires at map-time 480s in normal Pub. All XP remains kill-earned; no free XP or level floors. Runtime/WCT synchronized. In-engine and balance playtests pending.


v68: Classic Veigar complete. User stats STR/AGI/INT 15/16/20, gains 1.5/1.5/3. Hero Killer roster 97; Lich model; Q last-hit INT, W scaled meteor, E ranked stun, R target-INT burst, Equilibrium. Custom bordered BLP icons. Static-validated candidate; engine playtest pending.

v70 Lux Final Spark test: ALxR; standalone LX_ module in FF_Runtime and synchronized WCT globals. HLx1 is an extra test caster, outside draft/taverns. Debug/solo -lux/-lux2/-lux3. Charge 1 sec, 3400 range, 200 width, 400/650/900 + INT magic damage, 100/150/200 mana, 70/60/50 sec cooldown. PauseUnitEx lock is released once. New procedural models/textures/sounds in Spells\Lux. Compiler and mocked-native checks required; engine playtest pending.


v71 Stalker test: nStk, AStB, AStS. Model Stalker by Fingolfin, https://www.hiveworkshop.com/threads/stalker.171022/ ; custom mesh/texture used with required author credit. Adaptation adds attachment points, repairs bounds, repaths texture and removes unfinished Spell sequence. ST_ module preserves selected-unit formation Blink with per-unit cooldown, pathability/visibility/collision checks, shields on mana bar, +5 vs heavy/fortified. Debug/solo -stalkers summons eight test units. Not added to production roster. WC3 movement/combat/armor scale is an adaptation. Original SC2 audio and icons are not included. Engine playtest pending.


Mundo health-kit test: AMu2 remains X click-to-toggle with 12/16/20/24/28/32 health per second. Disease clouds damage on first scan, use MU_Hash key 23 for cloud scheduling (20 belongs to cleaver). Hidden AMi0-AMi9 and AMj0-AMj9 cancel Intelligence bonuses; MU_ZeroResources recomputes on registration and each 0.25 sec, and sets max/current mana to zero. Hero object INT, INT growth, max mana, initial mana and mana regeneration are zero. Engine testing of negative stat bonus and zero max mana remains required.


Mundo Cleaver Wound: new MW_ module and MW_Hash. AMwR/BMwR implement private art-free native movement root with 0.2 sec native duration and explicit cleanup; no shared Beng buff. AMwS/BMwS apply 70% move slow for 2.2 sec including root, no attack slow. Per-target 0.025 sec timer removes Bspe (also on impact), ending on 2.2 sec expiry, real dispel, death, removal, owner change, immunity, or replacement. Rehits refresh, not stack. Native root can interrupt channeling; no PauseUnit. Positional CreateSoundFromLabel MetalMediumChopFlesh and small blood burst play on contact including lethal hits. Engine testing pending.


Mundo cloud ramp: MC_ helpers; continuous 10 sec 1x-to-2x damage/HP drain, off/death resets hero keys 24/25. Integrated elapsed-time drain, cap at 10 sec. Cloud key46 stores emitted DPS; poison keys50-53 preserve maximum overlapping dose for four half-second ticks without stacking. 21 alpha-blended custom particle models transition light green/dark green/purple+green/near-black, snapshots match emitted strength. Prior health-kit and cleaver preserved. Engine testing pending.

Mundo merged onto UI label repair; UI repair archive members preserved and validated.


Stalker movement/Blink patch on UI Repair + Mundo Combined: nStk collision 32 -> 16. ST_Cast processes selected ready units from leading edge to rear, allowing vacated squad slots. ST_Move uses validated SetUnitX/Y, avoids native Stop and removes the 2-unit placement rollback. ST_Space uses actual mover collision, tolerates 10-unit item probe deviation, and temporarily hides/restores loose items so loot does not block Blink. Ownership/selection/readiness, visibility, terrain, blockers, cooldown, shields and tether integration remain. Three existing ST_ functions changed; one item-enumeration helper added. No other runtime functions, abilities, string labels, art or Mundo behavior changed. Runtime/editor compilation and mocked-native regression checks required; engine playtest pending.


Soul Hook integrated and fixed: ADk5 C, ADk6 stun. Swept outbound collision, per-cast damage, most-recent Demon Knight displacement wins. Mundo ramp and authored cloud models retained. Runtime and WCT synchronized; engine testing pending.


Veigar casting test: correct ability object field types using Warcraft metadata; preserve 700/900/900/650 cast ranges. AVgs stun missile speed 10000 with the standard spell dummy. Stun feedback supports rank 6. Editor and runtime synchronized. Engine playtest pending.


Veigar cast-distance test: Q 900, W 1100, E 1100, R 850; all ranks and displayed tooltips updated. Damage, target rules and cooldowns unchanged. Engine and balance testing pending.


v75: restrict timed level override to footmen. All other spawned units retain udg_unit_level. Pub level-7+ XP remains 70%. Runtime and authoritative WCT synchronized; both compile. Engine playtest pending.


v77 normal Pub: center boss level 5+(wave-1)/2 using integer division. Base packs keep waves 1/2 unchanged; wave 3 target is wave 2 XP times 1.10, then times 1.05 per wave through 10. Per-slot native levels approximate each target within 0.4 percent. Gold, combat stats, composition and timing unchanged. Includes v75 spawn fix and v67 70-percent post-7 rate. Runtime, WCT and source_roundtrip synchronized. Engine playtest pending.


v78 normal Pub: keep 70-percent kill XP at levels 7+ until first active registered primary hero reaches 10. Permanently unlock individual level-7-to-9 catch-up: rate = 70 + 40 * (10 - fractional hero level), based on actual cumulative XP thresholds 2700/3500/4400/5400. Ends individually at 10; below-7 rules preserved. Leader allies follow the same individual curve. All rewards still require kills. Native handicap refreshed every second and immediately on levels; scripted supplements calculate from current XP. Anti-cheat 25-percent override remains authoritative. Runtime and WCT synchronized. Engine playtest pending.


v79 normal Pub: at milestones 10/13/16, a strict majority of OTHER surviving teams must each have a strict majority of active primary heroes at the threshold. A hero at least one fractional level behind for 90 continuous seconds unlocks colo-only extra XP, tapering with the gap until the threshold. Extra = min(100 percent, 40 percent per level behind) of unmodified kill XP divided among nearby live allied primary heroes; maximum half one level XP band per player per spawn wave, fixed when first processed. Milestone shortfall also caps each award. The center boss and all direct colo units are tagged with their actual spawn wave. Only nearby live heroes on the killing team qualify. Deferred reward checks current XP after normal awards. Existing 70-percent rate, level-10 catch-up, colo curve and gold preserved. Engine ordering/playtest pending.
