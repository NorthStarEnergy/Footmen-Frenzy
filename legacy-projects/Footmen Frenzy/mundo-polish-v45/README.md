# Mundo and Twisted Fate v45

Base: Myrmidon Cleave v44. Retains its item changes and applies the confirmed v42a ability-record load fix.

Mundo: Cleaver Z with 1100 cast range and ground pickup circle, no lightning tether; aura X. Base and runtime stats mirror The Strongest Man Ever. Successful swallow gains a stomp effect. Flip travels 200/230/260/290/320/350 units by rank, 5% faster, with a higher arc and landing effects. Sweeps walkability, cliff level, collision footprint and playable bounds; obstructed throws shorten. Walkable areas behind bases remain usable.

Twisted Fate: three small card meshes, speed 1400, 18-degree fan offsets, 32-unit collision radius with swept collision. X cycles overhead, locks, then allows ten seconds to throw a homing card with a small attached coil effect. C is active Loaded Dice with a generated pair-of-dice icon. Native Gate retains its two-second cast and landing handling, with rotating custom LoL-inspired ground gateways at departure and intended destination plus a teleport channel effect.

Loaded Dice: requires at least 50 gold; 60-second cooldown; winning adds 50, losing subtracts 50. Win percentage = 50 + min(10, seconds alive / 90) + 2 * min(5, enemy hero kills this life). Survival is tracked at one-second intervals from spawning, including before learning the skill. Death immediately resets both bonuses. Illusions, allied kills and nonhero kills do not contribute. The former passive income is removed. All ability ranks use the requested odds and wager.

Validation: JASS compilation, 204 Mundo/regression checks, 82 TF checks using translated JASS and mocked natives, independent binary object parsing, model MDX roundtrip, built-in FX asset existence, archive readback and preservation of 1331 unrelated payloads. Native engine playtesting pending; mocked checks do not establish in-game appearance or load success.

Build: assets.py, models.cjs, tf_patch.py (runs build.py first), checks.py, tf_checks.py, native pjass compile to compiler.log, pack.py. Install.ps1 checks hashes and copies into both Warcraft Test folders and the workspace release archive. pack.py refuses to overwrite a release.

Assets: card/gateway geometry authored locally; model serialization uses MIT-licensed war3-model 4.0.1. Dice source generated with built-in imagegen; resized and framed using the project's standard button templates.

## v45a loss distribution
A lost roll distributes exactly 50 gold among opposing active players with at least one living, non-illusion hero. One share per player; integer shares differ by at most one gold, with a randomized starting slot for remainders. With no eligible enemies, the wager is still lost. Compilation and 296 automated checks pass; native playtest remains pending.
