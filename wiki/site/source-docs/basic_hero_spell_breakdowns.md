# Basic Hero Spell Breakdowns

First extracted draft for the 16 basic heroes. Layout follows the requested breakdown style: hero name, spell name, short behavior summary, per-level stats, and notes.

Data sources: `war3map.w3u`, `war3map.w3a`, and `war3map.wts`. Trigger-only behavior still needs a manual pass before this should be treated as final player-facing copy.

## Paladin

Rawcode `H005`. Ability list: `AHhb`, `AHds`, `AHad`, `AHre`.

### Holy Light

Ability `AHhb` based on `AHhb`.

Heals an injured non-Undead ally, or deals half damage to an enemy Undead unit.

| Level | Heal | Cooldown |
|---:|---:|---:|
| 1 | 300 | 5 |
| 2 | 600 | 6 |
| 3 | 900 | 7 |
| 4 | 1200 | 7 |
| 5 | 1500 | 6 |
| 6 | 2000 | 6 |

Notes:
- war3map.w3a entry AHhb based on AHhb.
- Learn tooltip was used for the primary table shape.

### Divine Shield

Ability `AHds` based on `AHds`.

An impenetrable shield surrounds the Paladin, protecting him from all damage and spells for a set amount of time.

| Level | Duration 1 | Duration 2 |
|---:|---:|---:|
| 1 | 6 | 60 |
| 2 | 12 | 55 |
| 3 | 14 | 50 |
| 4 | 16 | 45 |
| 5 | 18 | 40 |
| 6 | 20 | 35 |

Notes:
- war3map.w3a entry AHds based on AHds.
- Learn tooltip was used for the primary table shape.

### Devotion Aura

Ability `AHad` based on `AHad`.

Gives additional armor to nearby friendly units.

| Level | Data A | AoE | Duration |
|---:|---:|---:|---:|
| 1 | 4.5 | 1000 | 4 |
| 2 | 6 | 1100 | 4 |
| 3 | 8 | 1200 | 4 |
| 4 | 10 | 1300 | 4 |
| 5 | 15 | 1400 | 4 |
| 6 | 18 | 1500 | 4 |

Notes:
- war3map.w3a entry AHad based on AHad.
- Learn tooltip was used for the primary table shape.

### Resurrection

Ability `AHre` based on `AHre`.

Brings back to life the corpses of friendly nearby units.

| Level | Number of Units Resurrected |
|---:|---:|
| 1 | 10 |
| 2 | 16 |
| 3 | 24 |

Notes:
- war3map.w3a entry AHre based on AHre.
- Learn tooltip was used for the primary table shape.

## Archmage

Rawcode `H008`. Ability list: `AHbz`, `AHab`, `AHwe`, `AHmt`.

### Blizzard

Ability `AHbz` based on `AHbz`.

Calls down waves of freezing ice shards that damage units in a target area.

| Level | AoE | DMG | Waves |
|---:|---:|---:|---:|
| 1 | — | 33 | 5 |
| 2 | 250 | 42 | 6 |
| 3 | 275 | 90 | 6 |
| 4 | 300 | 115 | 6 |
| 5 | 350 | 130 | 7 |
| 6 | 400 | 155 | 8 |

Notes:
- war3map.w3a entry AHbz based on AHbz.
- Learn tooltip was used for the primary table shape.

### Brilliance Aura

Ability `AHab` based on `AHab`.

Gives additional mana regeneration to nearby friendly units.

| Level | AoE |
|---:|---:|
| 1 | 1100 |
| 2 | 1350 |
| 3 | 1400 |
| 4 | 1500 |
| 5 | 1700 |
| 6 | 1800 |

Notes:
- war3map.w3a entry AHab based on AHab.
- Learn tooltip was used for the primary table shape.

### Summon Water Elemental

Ability `AHwe` based on `AHwe`.

Summons Water Elementals to attack the Archmage's enemies.
Lasts 35 seconds.

| Level | Lasts | Spawns |
|---:|---:|---:|
| 1 | 35 | — |
| 2 | 35 | 2 |
| 3 | 35 | 2 |
| 4 | 35 | 2 |
| 5 | 35 | 3 |
| 6 | 35 | 3 |

Notes:
- war3map.w3a entry AHwe based on AHwe.
- Learn tooltip was used for the primary table shape.

### Mass Teleport

Ability `AHmt` based on `AHmt`.

Teleports the player's nearby units, including the Archmage, to a friendly ground unit or structure.

| Level | Max Units | Cooldown | Cast Time |
|---:|---:|---:|---:|
| 1 | 16 | 60 | 2 |
| 2 | 30 | 60 | 1.5 |
| 3 | 40 | 60 | 0 |

Notes:
- war3map.w3a entry AHmt based on AHmt.
- Learn tooltip was used for the primary table shape.

## Mountain King

Rawcode `H00A`. Ability list: `A0G9`, `AHtb`, `A00D`, `AHav`.

### Thunder Clap

Ability `A0G9` based on `AHtc`.

Slams the ground, dealing damage to and slowing the movement speed and attack speed of nearby enemy land units for 6 (3) seconds.

| Level | DMG | AS | MS |
|---:|---:|---:|---:|
| 1 | 75 | 15 | 20 |
| 2 | 100 | 25 | 25 |
| 3 | 180 | 30 | 30 |
| 4 | 250 | 35 | 35 |
| 5 | 300 | 40 | 40 |
| 6 | 500 | 45 | 45 |

Notes:
- war3map.w3a entry A0G9 based on AHtc.
- Learn tooltip was used for the primary table shape.

### Storm Bolt

Ability `AHtb` based on `AHtb`.

A magical hammer that is thrown at an enemy unit, causing damage and stunning the target.

| Level | Damage | Duration | Hero Duration |
|---:|---:|---:|---:|
| 1 | 125 | 1.5 | 1.5 |
| 2 | 225 | 2 | 2 |
| 3 | 350 | 2.5 | 2.5 |
| 4 | 450 | 3 | 3 |
| 5 | 550 | 3.5 | 3.25 |
| 6 | 800 | 4 | 3.5 |

Notes:
- war3map.w3a entry AHtb based on AHtb.
- Learn tooltip was used for the primary table shape.

### Bash

Ability `A00D` based on `AHbh`.

Gives a chance that an attack will do bonus damage and stun an opponent for a short duration.

| Level | Chance | DMG + | Stun 1 | Stun 2 |
|---:|---:|---:|---:|---:|
| 1 | 10 | 25 | 2 | 1 |
| 2 | 15 | 35 | 3 | 1.25 |
| 3 | 20 | 45 | 4 | 1.5 |
| 4 | 25 | 55 | 4 | 1.75 |
| 5 | 30 | 65 | 4 | 2 |
| 6 | 35 | 80 | 5 | 2 |

Notes:
- war3map.w3a entry A00D based on AHbh.
- Learn tooltip was used for the primary table shape.

### Avatar

Ability `AHav` based on `AHav`.

Grants the hero a bonus to Armor, HP, DMG and grants spell immunity for a limited duration.

| Level | Damage Bonus | Armor Bonus | Hit Point Bonus | Duration |
|---:|---:|---:|---:|---:|
| 1 | 30 | 5 | 500 | 45 |
| 2 | 40 | 10 | 750 | 47 |
| 3 | 50 | 15 | 1000 | 50 |

Notes:
- war3map.w3a entry AHav based on AHav.
- Learn tooltip was used for the primary table shape.

## Blood Mage

Rawcode `H009`. Ability list: `AHfs`, `AHbn`, `AHdr`, `AHpx`.

### Flame Strike

Ability `AHfs` based on `AHfs`.

Conjures a pillar of fire which damages ground units in a target area over time.

| Level | DPS | AoE | Duration |
|---:|---:|---:|---:|
| 1 | 5.5 | 220 | 2 |
| 2 | 6.5 | 230 | 2 |
| 3 | 11 | 240 | 2 |
| 4 | 13.5 | 250 | 2 |
| 5 | 20 | 260 | 2 |
| 6 | 29 | 280 | 2 |

Notes:
- war3map.w3a entry AHfs based on AHfs.
- Learn tooltip was used for the primary table shape.

### Banish

Ability `AHbn` based on `AHbn`.

Turns a non-mechanical unit Ethereal. Ethereal units cannot attack and have their movement speed reduced. Ethereal units also take 66% more damage from spells and magic attacks, but also receive 66% more healing.

| Level | Movement Speed 1 | Movement Speed 2 | Movement Speed 3 |
|---:|---:|---:|---:|
| 1 | 30 | 12 | 4 |
| 2 | 40 | 15 | 5 |
| 3 | 50 | 18 | 6 |
| 4 | 60 | 48 | 7 |
| 5 | 70 | 60 | 8 |
| 6 | 80 | 120 | 9 |

Notes:
- war3map.w3a entry AHbn based on AHbn.
- Learn tooltip was used for the primary table shape.

### Siphon Mana

Ability `AHdr` based on `AHdr`.

Drains mana from an enemy unit, also drains life levels 4+ Can also be cast on an ally to transfer the caster's mana

| Level | Data A | Data B | AoE | Range | Cooldown | Hero Duration |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | — | 5 | — | 650 | 15 | 4 |
| 2 | — | 7 | — | 675 | 15 | 4 |
| 3 | — | 12 | 825 | 750 | 15 | 5 |
| 4 | 8 | 17 | 875 | 800 | 15 | 5 |
| 5 | 10 | 20 | 875 | 800 | 15 | 5 |
| 6 | 12 | 25 | 900 | 800 | 15 | — |

Notes:
- war3map.w3a entry AHdr based on AHdr.
- Learn tooltip was used for the primary table shape.

### Phoenix

Ability `AHpx` based on `AHpx`.

Summons a Phoenix - a strong flying unit that burns nearby enemies. Has Magic Immunity and Resistant Skin. The Phoenix creates an Egg when it dies that will Hatch into a new Phoenix if not killed.

| Level | Units Summoned 1 | Units Summoned 2 |
|---:|---:|---:|
| 1 | 1 | 200 |
| 2 | 2 | 200 |
| 3 | 3 | 200 |

Notes:
- war3map.w3a entry AHpx based on AHpx.
- Learn tooltip was used for the primary table shape.

## Blademaster

Rawcode `O003`. Ability list: `AOwk`, `A00G`, `A041`, `AOww`.

### Wind Walk

Ability `AOwk` based on `AOwk`.

Allows the hero to become invisible, and move faster for a set amount of time. When the hero attacks a unit to break invisibility, he will deal bonus damage.

| Level | DMG | MS + | Duration |
|---:|---:|---:|---:|
| 1 | 90 | 20 | 18 |
| 2 | 150 | 25 | 20 |
| 3 | 225 | 30 | 23 |
| 4 | 275 | 35 | 25 |
| 5 | 375 | 45 | 27 |
| 6 | 500 | 55 | 30 |

Notes:
- war3map.w3a entry AOwk based on AOwk.
- Learn tooltip was used for the primary table shape.

### Critical Strike

Ability `A00G` based on `AOcr`.

Gives a chance to do more damage on an attack.

| Level | Chance to Critical Strike | Damage Multiplier |
|---:|---:|---:|
| 1 | 20 | 2 |
| 2 | 20 | 2.5 |
| 3 | 22 | 3 |
| 4 | 23 | 3.5 |
| 5 | 24 | 4.5 |
| 6 | 25 | 6 |

Notes:
- war3map.w3a entry A00G based on AOcr.
- Learn tooltip was used for the primary table shape.

### Mirror Image

Ability `A041` based on `AOmi`.

Confuses the enemy by creating illusions of the Blademaster and dispelling all magic from the Blademaster. Higher level illusions also deal a percentage of the Blademaster's damage.

| Level | Images | Image Damage |
|---:|---:|---:|
| 1 | 1 | 0 |
| 2 | 2 | 0 |
| 3 | 3 | 0 |
| 4 | 4 | 10 |
| 5 | 5 | 20 |
| 6 | 8 | 40 |

Notes:
- war3map.w3a entry A041 based on AOmi.
- Learn tooltip was used for the primary table shape.

### Bladestorm

Ability `AOww` based on `AOww`.

Deals damage to nearby enemies each second and grants Spell Immunity for a set duration.

| Level | DPS 1 | DPS 2 | DPS 3 |
|---:|---:|---:|---:|
| 1 | 135 | 250 | 7 |
| 2 | 235 | 300 | 7 |
| 3 | 350 | 325 | 7 |

Notes:
- war3map.w3a entry AOww based on AOww.
- Learn tooltip was used for the primary table shape.

## Far Seer

Rawcode `O004`. Ability list: `A001`, `AOsf`, `AOcl`, `AOeq`.

### Silence

Ability `A001` based on `ANsi`.

Prevents enemies in an area from casting spells for a set duration. Higher levels also prevent melee and ranged attacks.

| Level | AoE | DUR 1 | DUR 2 | CD |
|---:|---:|---:|---:|---:|
| 1 | 200 | 9 | 3 | 15 |
| 2 | 250 | 9 | 4 | 16 |
| 3 | 300 | 9 | 5 | 17 |
| 4 | 350 | 9 | 6 | 18 |
| 5 | 400 | 9 | 7 | 19 |
| 6 | 400 | 9 | 8 | 20 |

Notes:
- war3map.w3a entry A001 based on ANsi.
- Learn tooltip was used for the primary table shape.

### Feral Spirit

Ability `AOsf` based on `AOsf`.

Summons Wolves to fight the Far Seer's enemies. Each rank adds additional abilities to the Wolves.

| Level | Wolves |
|---:|---:|
| 1 | 2 |
| 2 | 3 |
| 3 | 4 |
| 4 | 5 |
| 5 | 6 |
| 6 | 7 |

Notes:
- war3map.w3a entry AOsf based on AOsf.
- Learn tooltip was used for the primary table shape.

### Chain Lightning

Ability `AOcl` based on `AOcl`.

Deals damage to a single enemy, and then jumps to additional nearby enemies. Deals less damage with each jump.

| Level | DMG | Jumps | Jump Loss |
|---:|---:|---:|---:|
| 1 | 115 | 5 | 10 |
| 2 | 155 | 8 | 10 |
| 3 | 220 | 9 | 10 |
| 4 | 265 | 11 | 9 |
| 5 | 330 | 13 | 7 |
| 6 | 575 | 15 | 1 |

Notes:
- war3map.w3a entry AOcl based on AOcl.
- Learn tooltip was used for the primary table shape.

### Earthquake

Ability `AOeq` based on `AOeq`.

Channels an Earthquake in the target area. Units have their movement speed reduced greatly, and buildings take damage each second.

| Level | DMG | MS | Cooldown | Duration |
|---:|---:|---:|---:|---:|
| 1 | 75 | 75 | 90 | 40 |
| 2 | 100 | 85 | 0.85 | 50 |
| 3 | 150 | 99 | 0.99 | 60 |

Notes:
- war3map.w3a entry AOeq based on AOeq.
- Learn tooltip was used for the primary table shape.

## Tauren Chieftain

Rawcode `O005`. Ability list: `AOsh`, `AOws`, `AOae`, `AOre`.

### Shockwave

Ability `AOsh` based on `AOsh`.

Damages enemy land units in a straight line. Total damage cannot exceed a certain cap.

| Level | DMG | DMG Cap | Range |
|---:|---:|---:|---:|
| 1 | — | — | 750 |
| 2 | — | — | — |
| 3 | — | — | 875 |
| 4 | 270 | 3240 | 925 |
| 5 | 340 | 4080 | 950 |
| 6 | 570 | 7200 | 975 |

Notes:
- war3map.w3a entry AOsh based on AOsh.
- Learn tooltip was used for the primary table shape.

### War Stomp

Ability `AOws` based on `AOws`.

Damages nearby enemy land units and stuns them for a set time.

| Level | DMG | Duration 1 | Duration 2 | AoE |
|---:|---:|---:|---:|---:|
| 1 | 50 | 2 | — | 300 |
| 2 | 80 | 2.25 | 2.25 | 350 |
| 3 | 100 | 2.5 | 2.5 | — |
| 4 | 135 | 2.75 | 2.75 | 400 |
| 5 | 180 | 3 | 3 | 450 |
| 6 | 250 | 3.25 | 3.25 | 550 |

Notes:
- war3map.w3a entry AOws based on AOws.
- Learn tooltip was used for the primary table shape.

### Endurance Aura

Ability `AOae` based on `AOae`.

Increases the movement speed and attack speed of nearby friendly units.

| Level | AS + | MS + | AoE |
|---:|---:|---:|---:|
| 1 | — | 15 | — |
| 2 | — | — | 925 |
| 3 | 20 | 25 | 950 |
| 4 | 25 | — | 975 |
| 5 | 30 | 50 | 1000 |
| 6 | 40 | 60 | 1250 |

Notes:
- war3map.w3a entry AOae based on AOae.
- Learn tooltip was used for the primary table shape.

### Reincarnation

Ability `AOre` based on `AOre`.

When killed, the hero will come back to life after a short delay.

| Level | Cooldown | Revive Delay |
|---:|---:|---:|
| 1 | 400 | 6 |
| 2 | 380 | — |
| 3 | 300 | 4 |

Notes:
- war3map.w3a entry AOre based on AOre.
- Learn tooltip was used for the primary table shape.

## Shadow Hunter

Rawcode `O006`. Ability list: `AOhw`, `AOhx`, `AOsw`, `AOvd`.

### Healing Wave

Ability `AOhw` based on `AOhw`.

Heals a single target, then jumps to other injured nearby allies. Heals less on each jump.

| Level | Heal | Jumps | Jump Loss |
|---:|---:|---:|---:|
| 1 | 140 | 4 | 20 |
| 2 | 220 | 4 | 20 |
| 3 | 300 | 5 | 20 |
| 4 | 385 | 6 | 20 |
| 5 | 470 | 7 | 15 |
| 6 | 750 | 12 | 5 |

Notes:
- war3map.w3a entry AOhw based on AOhw.
- Learn tooltip was used for the primary table shape.

### Hex

Ability `AOhx` based on `AOhx`.

Transforms an enemy unit into a critter, disabling its abilities and attack.

| Level | Duration 1 | Duration 2 | Cooldown |
|---:|---:|---:|---:|
| 1 | 4 | 2 | 8 |
| 2 | 5 | 2.5 | 8 |
| 3 | 6 | 3 | 8 |
| 4 | 7 | 3.5 | 7.5 |
| 5 | 8 | 4 | 7.5 |
| 6 | 9 | 4.5 | 7.5 |

Notes:
- war3map.w3a entry AOhx based on AOhx.
- Learn tooltip was used for the primary table shape.

### Serpent Ward

Ability `AOsw` based on `AOsw`.

Summons immobile Serpent Wards that attack nearby enemies with piercing damage for a set amount of time. Serpent Wards have Spell Immunity.

| Level | Wards | CD | DUR |
|---:|---:|---:|---:|
| 1 | 2 | 9 | 20 |
| 2 | 3 | 8 | 22.5 |
| 3 | 2 | 7 | 25 |
| 4 | 3 | 6 | 25 |
| 5 | 3 | 6 | 25 |
| 6 | 4 | 6 | 30 |

Notes:
- war3map.w3a entry AOsw based on AOsw.
- Learn tooltip was used for the primary table shape.

### Big Bad Voodoo

Ability `AOvd` based on `AOvd`.

While channeling this spell, all nearby allied units except the caster are invulnerable.
Lasts 20 seconds.

| Level | Lasts | AoE | Cooldown |
|---:|---:|---:|---:|
| 1 | 20 | — | 160 |
| 2 | 20 | 900 | 140 |
| 3 | 20 | 1000 | 120 |

Notes:
- war3map.w3a entry AOvd based on AOvd.
- Learn tooltip was used for the primary table shape.

## Death Knight

Rawcode `U002`. Ability list: `AUdc`, `AUdp`, `AUau`, `AUan`.

### Death Coil

Ability `AUdc` based on `AUdc`.

Heals an injured Undead ally, or deals half damage to an enemy non-Undead unit.

| Level | Heal | Cooldown |
|---:|---:|---:|
| 1 | 200 | 6 |
| 2 | 500 | 6 |
| 3 | 800 | 7 |
| 4 | 1045 | 8 |
| 5 | 1500 | 9 |
| 6 | 2070 | 5 |

Notes:
- war3map.w3a entry AUdc based on AUdc.
- Learn tooltip was used for the primary table shape.

### Death Pact

Ability `AUdp` based on `AUdp`.

Sacrifices an allied Undead unit, and converts a percentage of its hit points into life and mana for the caster.

| Level | Life | Mana |
|---:|---:|---:|
| 1 | 75 | 5 |
| 2 | 150 | 10 |
| 3 | 200 | 20 |
| 4 | — | 30 |
| 5 | 400 | 40 |
| 6 | 500 | 60 |

Notes:
- war3map.w3a entry AUdp based on AUdp.
- Learn tooltip was used for the primary table shape.

### Unholy Aura

Ability `AUau` based on `AUau`.

Increases the movement speed and life regeneration rate of nearby friendly units.

| Level | AoE | HP/s + | MS + |
|---:|---:|---:|---:|
| 1 | — | 2.8 | 5 |
| 2 | 950 | 4.2 | 10 |
| 3 | 1000 | 6 | 15 |
| 4 | 1050 | 8 | — |
| 5 | 1100 | 10 | 35 |
| 6 | 1250 | 15 | 45 |

Notes:
- war3map.w3a entry AUau based on AUau.
- Learn tooltip was used for the primary table shape.

### Animate Dead

Ability `AUan` based on `AUan`.

Raises nearby corpses to fight for the Death Knight. These units last for 40 seconds.

| Level | Number of Corpses | Cooldown |
|---:|---:|---:|
| 1 | 8 | 140 |
| 2 | 16 | 140 |
| 3 | 24 | 160 |

Notes:
- war3map.w3a entry AUan based on AUan.
- Learn tooltip was used for the primary table shape.

## Lich King

Rawcode `U003`. Ability list: `A00P`, `AUdr`, `AUfu`, `AUdd`.

### Frost Nova

Ability `A00P` based on `AUfn`.

Damages enemies in an area, with extra damage dealt to the intial target. Reduces the movement speed and attack rate of affected units by 25% for a set duration.

| Level | DMG | Tar DMG + | AoE | DUR 1 | DUR 2 |
|---:|---:|---:|---:|---:|---:|
| 1 | 60 | 110 | 0 | 2 | 1 |
| 2 | 130 | 150 | 250 | 2.5 | 2 |
| 3 | 180 | 175 | 300 | 2.75 | 2.5 |
| 4 | 240 | 200 | 350 | 3 | 2.75 |
| 5 | 315 | 225 | 400 | 3 | 3 |
| 6 | 570 | 300 | 425 | 4 | 4 |

Notes:
- war3map.w3a entry A00P based on AUfn.
- Learn tooltip was used for the primary table shape.

### Dark Ritual

Ability `AUdr` based on `AUdr`.

Sacrifices a friendly undead unit, and converts its hit points into mana for the caster. At higher levels, the caster also gains life.

| Level | Mana | Life | Cooldown |
|---:|---:|---:|---:|
| 1 | 10 | 0.33 | 2 |
| 2 | 15 | 0.66 | 1.9 |
| 3 | 20 | 1 | 1.8 |
| 4 | 25 | 10 | 1.7 |
| 5 | 30 | 15 | 1.6 |
| 6 | 35 | 20 | 1.25 |

Notes:
- war3map.w3a entry AUdr based on AUdr.
- Learn tooltip was used for the primary table shape.

### Frost Armor

Ability `AUfu` based on `AUfu`.

Temporarily grants bonus armor to a friendly unit. Melee attackers also have their movement and attack speed reduced by 25% for a set duration.

| Level | Armor | DUR | Slow DUR |
|---:|---:|---:|---:|
| 1 | 2 | 40 | 3 |
| 2 | 3 | 40 | 5 |
| 3 | 6 | — | 5 |
| 4 | 9 | — | 5 |
| 5 | 12 | — | 10 |
| 6 | 15 | 60 | 12 |

Notes:
- war3map.w3a entry AUfu based on AUfu.
- Learn tooltip was used for the primary table shape.

### Death And Decay

Ability `AUdd` based on `AUdd`.

While channeling, ALL units in the area of effect lose a percentage of their maximum life per second. Lasts 20 seconds.

| Level | DMG | AoE | Cooldown |
|---:|---:|---:|---:|
| 1 | 6 | 500 | 180 |
| 2 | 8 | 550 | 170 |
| 3 | 10 | 600 | 160 |

Notes:
- war3map.w3a entry AUdd based on AUdd.
- Learn tooltip was used for the primary table shape.

## Dread Lord

Rawcode `U004`. Ability list: `AUav`, `AUsl`, `AUcs`, `A0HT`.

### Vampiric Aura

Ability `AUav` based on `AUav`.

Nearby friendly non-mechanical melee units regain a percentage of their damage with basic attacks as health.

| Level | DMG to Heal | AoE |
|---:|---:|---:|
| 1 | 17 | 800 |
| 2 | 35 | 850 |
| 3 | 45 | 900 |
| 4 | 60 | 950 |
| 5 | 65 | 1000 |
| 6 | 75 | 1250 |

Notes:
- war3map.w3a entry AUav based on AUav.
- Learn tooltip was used for the primary table shape.

### Sleep

Ability `AUsl` based on `AUsl`.

Puts a target non-mechanical enemy to sleep. It is invulnerable and cannot act for a short duration, then remains asleep for a much longer duration. A sleeping unit awakes if it is attacked.

| Level | Sleep Duration 1 | Sleep Duration 2 | Cooldown |
|---:|---:|---:|---:|
| 1 | 20 | 3 | 10 |
| 2 | 40 | 4 | 10 |
| 3 | 60 | 5 | 10 |
| 4 | 80 | 6 | 10 |
| 5 | 100 | 7 | 10 |
| 6 | 110 | 8 | 10 |

Notes:
- war3map.w3a entry AUsl based on AUsl.
- Learn tooltip was used for the primary table shape.

### Carrion Swarm

Ability `AUcs` based on `AUcs`.

Deals damage to all non-mechnical enemies in a cone. Total damage cannot exceed a certain cap.

| Level | DMG | DMG Cap |
|---:|---:|---:|
| 1 | 85 | 900 |
| 2 | 125 | 1500 |
| 3 | 200 | 2400 |
| 4 | 275 | 3200 |
| 5 | 360 | 4500 |
| 6 | 570 | 8000 |

Notes:
- war3map.w3a entry AUcs based on AUcs.
- Learn tooltip was used for the primary table shape.

### Inferno

Ability `A0HT` based on `AUin`.

Summons an Infernal, damaging and stunning enemies for 4 (2) seconds in a small area of effect.
Infernals have Permanent Immolation, Resistant Skin, Spell Immunity and deal chaos damage. Higher ranks have more abilities.

| Level | DMG | DUR |
|---:|---:|---:|
| 1 | 75 | 160 |
| 2 | 150 | 160 |
| 3 | 175 | 160 |

Notes:
- war3map.w3a entry A0HT based on AUin.
- Learn tooltip was used for the primary table shape.

## Crypt Lord

Rawcode `U005`. Ability list: `AUim`, `AUts`, `A029`, `AUls`.

### Impale

Ability `AUim` based on `AUim`.

Deals damage to and stuns enemy non-mechnical land units in a straight line for a set duration.

| Level | DMG | Duration | Range |
|---:|---:|---:|---:|
| 1 | 65 | 0.75 | 500 |
| 2 | 115 | 1 | 525 |
| 3 | 185 | 1.5 | 575 |
| 4 | 225 | 2.25 | 600 |
| 5 | 320 | 2.5 | 625 |
| 6 | 540 | 3 | 625 |

Notes:
- war3map.w3a entry AUim based on AUim.
- Learn tooltip was used for the primary table shape.

### Spiked Carapace

Ability `AUts` based on `AUts`.

Passively increases the Hero's armor and reflects a percentage of damage taken by melee attackers.

| Level | Armor + | Reflect |
|---:|---:|---:|
| 1 | 3 | 25 |
| 2 | 6 | 50 |
| 3 | 9 | 75 |
| 4 | 12 | 100 |
| 5 | 15 | 125 |
| 6 | 20 | 225 |

Notes:
- war3map.w3a entry AUts based on AUts.
- Learn tooltip was used for the primary table shape.

### Carrion Beetles

Ability `A029` based on `ACs7`.

Summons Carrion Beetles.
Carrion Beetles are melee attackers with Spell Immunity. Higher levels also gain additional abilities.

| Level | Beetles |
|---:|---:|
| 1 | 3 |
| 2 | 4 |
| 3 | 5 |
| 4 | 6 |
| 5 | 7 |
| 6 | 9 |

Notes:
- war3map.w3a entry A029 based on ACs7.
- Learn tooltip was used for the primary table shape.

### Locust Swarm

Ability `AUls` based on `AUls`.

Creates a group of invulnerable locusts that attack nearby enemies for 30 seconds, dealing spell damage. When the spell ends, they return to and heal the caster for a percentage of the damage they dealt.

| Level | Locusts | Heal | CD |
|---:|---:|---:|---:|
| 1 | 22 | 400 | 180 |
| 2 | 25 | 400 | 180 |
| 3 | 35 | 400 | 180 |

Notes:
- war3map.w3a entry AUls based on AUls.
- Learn tooltip was used for the primary table shape.

## Keeper of the Groove

Rawcode `E002`. Ability list: `AEer`, `AEah`, `A007`, `AEtq`.

### Entangling Roots

Ability `AEer` based on `AEer`.

Immobilizes, prevents the attacks of and deals damage every second to an enemy non-mechanical unit for a set duration.

| Level | DMG | Duration 1 | Duration 2 | Cooldown |
|---:|---:|---:|---:|---:|
| 1 | 35 | 7 | 2 | 8 |
| 2 | 45 | 10 | 3 | 8.5 |
| 3 | 60 | 12 | 4 | 9 |
| 4 | 75 | 15 | 5 | 9.5 |
| 5 | 90 | 20 | 6 | 9.5 |
| 6 | 105 | 25 | 6 | 9.5 |

Notes:
- war3map.w3a entry AEer based on AEer.
- Learn tooltip was used for the primary table shape.

### Thorns Aura

Ability `AEah` based on `AEah`.

Nearby friendly units reflect a percentage of melee damage taken.

| Level | Reflect | AoE |
|---:|---:|---:|
| 1 | 18 | 900 |
| 2 | 25 | 925 |
| 3 | 55 | 950 |
| 4 | 65 | 975 |
| 5 | 75 | 1000 |
| 6 | 90 | 1250 |

Notes:
- war3map.w3a entry AEah based on AEah.
- Learn tooltip was used for the primary table shape.

### Force Of Nature

Ability `A007` based on `ACs7`.

Summons Treants.
Treants are melee attackers. Higher levels gain abilities.

| Level | Treants |
|---:|---:|
| 1 | 3 |
| 2 | 4 |
| 3 | 5 |
| 4 | 6 |
| 5 | 7 |
| 6 | 9 |

Notes:
- war3map.w3a entry A007 based on ACs7.
- Learn tooltip was used for the primary table shape.

### Tranquility

Ability `AEtq` based on `AEtq`.

While channeling, nearby friendly units are healed rapidly over time.

| Level | Heal | Duration | Cooldown |
|---:|---:|---:|---:|
| 1 | 3.75 | 30 | 60 |
| 2 | 7 | 30 | 60 |
| 3 | 9.5 | 30 | 60 |

Notes:
- war3map.w3a entry AEtq based on AEtq.
- Learn tooltip was used for the primary table shape.

## Priestess of the Moon

Rawcode `E003`. Ability list: `AEst`, `A0DY`, `AEar`, `AEsf`.

### Scout

Ability `AEst` based on `AEst`.

Summons Owl Scouts that last for 30 seconds.
Owl Scouts are flying units that can cast Mana Burn and have True Sight. Higher level Owls can attack.

| Level | Owls | Mana Burn | Damage |
|---:|---:|---:|---:|---:|
| 1 | 2 | 25 | — |
| 2 | 2 | 25 | 23-32 |
| 3 | 3 | 50 | 33-42 |
| 4 | 3 | 50 | 43-52 |
| 5 | 3 | 65 | 53-62 |
| 6 | 3 | 65 | 63-72 |

Notes:
- war3map.w3a entry AEst based on AEst.
- Learn tooltip was used for the primary table shape.

### Stun Arrow

Ability `A0DY` based on `ANfb`.

Damages a single non-mechanical enemy and stuns them for a short duration.

| Level | DMG | Duration 1 | Duration 2 |
|---:|---:|---:|---:|
| 1 | 150 | 5 | 1.5 |
| 2 | 200 | 6 | 1.75 |
| 3 | 250 | 7 | 2 |
| 4 | 300 | 8 | 2.25 |
| 5 | 375 | 9 | 2.5 |
| 6 | 450 | 10 | 3 |

Notes:
- war3map.w3a entry A0DY based on ANfb.
- Learn tooltip was used for the primary table shape.

### Trueshot Aura

Ability `AEar` based on `AEar`.

Nearby allied ranged units gain bonus damage.

| Level | DMG + | AoE |
|---:|---:|---:|
| 1 | 25 | 900 |
| 2 | 30 | 925 |
| 3 | 35 | 950 |
| 4 | 45 | 975 |
| 5 | 55 | 1000 |
| 6 | 60 | 1250 |

Notes:
- war3map.w3a entry AEar based on AEar.
- Learn tooltip was used for the primary table shape.

### Starfall

Ability `AEsf` based on `AEsf`.

While channeling, nearby enemy units take damage every 1.25 seconds. Deals 90% less damage to buildings. Lasts for up to 15-20 seconds.

| Level | DMG | Cooldown |
|---:|---:|---:|
| 1 | 175 | 220 |
| 2 | 275 | 210 |
| 3 | 350 | 200 |

Notes:
- war3map.w3a entry AEsf based on AEsf.
- Learn tooltip was used for the primary table shape.

## Demon Hunter

Rawcode `E00F`. Ability list: `AEmb`, `AEim`, `AEev`, `AEme`.

### Mana Burn

Ability `AEmb` based on `AEmb`.

Destroys the mana of a target, and deals spell damage to it equal to the mana removed.

| Level | Mana Burned | Cooldown | Range |
|---:|---:|---:|---:|
| 1 | 175 | 10 | 450 |
| 2 | 250 | 10 | 500 |
| 3 | 350 | 6 | 550 |
| 4 | 500 | 6 | 625 |
| 5 | 600 | 6 | 650 |
| 6 | 750 | 6 | 650 |

Notes:
- war3map.w3a entry AEmb based on AEmb.
- Learn tooltip was used for the primary table shape.

### Immolation

Ability `AEim` based on `AEim`.

Burns nearby enemy non-mechanical units every second. Drains mana until deactivated manually.

| Level | AoE | Mana Cost |
|---:|---:|---:|
| 1 | 210 | 8 |
| 2 | 215 | 10 |
| 3 | 225 | 11 |
| 4 | 240 | 12 |
| 5 | 260 | 13 |
| 6 | 290 | 15 |

Notes:
- war3map.w3a entry AEim based on AEim.
- Learn tooltip was used for the primary table shape.

### Evasion

Ability `AEev` based on `AEev`.

Gives a percentage chance to avoid basic attacks, taking no damage.

| Level | Dodge Chance |
|---:|---:|
| 1 | 20 |
| 2 | 30 |
| 3 | 40 |
| 4 | 50 |
| 5 | 60 |
| 6 | 70 |

Notes:
- war3map.w3a entry AEev based on AEev.
- Learn tooltip was used for the primary table shape.

### Metamorphosis

Ability `AEme` based on `AEme`.

Transforms the Demon Hunter for a set duration. While in Demon Form, his attacks deal chaos damage, are ranged, and deal damage in a small area of effect. In addition, he gains a large bonus to hit points.

| Level | HP Bonus | Duration | Cooldown |
|---:|---:|---:|---:|
| 1 | — | — | — |
| 2 | 750 | 70 | — |
| 3 | 1200 | 80 | — |

Notes:
- war3map.w3a entry AEme based on AEme.
- Learn tooltip was used for the primary table shape.

## Warden

Rawcode `E005`. Ability list: `AEfk`, `AEbl`, `AEsh`, `AEsv`.

### Fan of Knives

Ability `AEfk` based on `AEfk`.

Instanty damages nearby non-mechanical enemies. Total damage cannot exceed a certain cap. Range slightly improves with each level.

| Level | DMG | Cap | Cooldown |
|---:|---:|---:|---:|
| 1 | 110 | 1000 | 8 |
| 2 | 150 | 1600 | 9 |
| 3 | 220 | 2500 | 10 |
| 4 | 275 | 3200 | 10 |
| 5 | 330 | 4600 | 11 |
| 6 | 570 | 7200 | 11 |

Notes:
- war3map.w3a entry AEfk based on AEfk.
- Learn tooltip was used for the primary table shape.

### Blink

Ability `AEbl` based on `AEbl`.

Teleports the hero a 'short' distance.

| Level | Distance | Cooldown |
|---:|---:|---:|
| 1 | 900 | 10 |
| 2 | 1000 | 9 |
| 3 | 1100 | 8 |
| 4 | 1200 | 7 |
| 5 | 1300 | 6 |
| 6 | 1400 | 5 |

Notes:
- war3map.w3a entry AEbl based on AEbl.
- Learn tooltip was used for the primary table shape.

### Shadow Strike

Ability `AEsh` based on `AEsh`.

Damages a single target and then inflicts additional periodic damage to the target every 3 seconds for a set duration. During this time, the target moves 25% slower.

| Level | DMG | DOT | Duration 1 | Duration 2 |
|---:|---:|---:|---:|---:|
| 1 | 75 | 20 | 15 | 7 |
| 2 | 150 | 60 | 16 | 7 |
| 3 | 225 | 90 | 17 | 7 |
| 4 | 300 | 120 | 18 | 7 |
| 5 | 375 | 150 | 19 | 7 |
| 6 | 550 | 180 | 20 | 7 |

Notes:
- war3map.w3a entry AEsh based on AEsh.
- Learn tooltip was used for the primary table shape.

### Vengeance

Ability `AEsv` based on `AEsv`.

Creates powerful Avatars.
Avatars can raise invulnerable Spirits from corpses and last for 180 seconds.

| Level | Avatars | Cooldown |
|---:|---:|---:|
| 1 | 1 | 180 |
| 2 | 2 | 170 |
| 3 | 3 | 160 |

Notes:
- war3map.w3a entry AEsv based on AEsv.
- Learn tooltip was used for the primary table shape.
