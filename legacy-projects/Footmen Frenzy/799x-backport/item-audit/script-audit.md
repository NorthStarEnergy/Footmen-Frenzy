# Scripted item audit

Static script audit complete for item-specific runtime handlers; no in-game execution performed. Direct abilities and recipes are integrated separately by the main audit.

## IGs1

- Suppresses enemy non-item spellcasting across the map for 120 seconds. Native silence radius 99999; refreshed every 0.25 seconds with 0.6-second buff. Newly spawned/revived or dispelled enemies are affected again on the next pulse.
- Repeated use by the same player refreshes their 120-second timer. Different players have independent timers; cleanup removes buffs only when no opposing source remains. Item abilities bypass the script guard.

Evidence: GSI_Init:5134, GSI_Start:5106, GSI_Guard:5056, GSI_Pulse:5066, GSI_Expire:5079.

## I024

- Applies a 90-second Sleep to a nonhero enemy; Sleep invulnerability field is also 90 seconds.
- Removes ACmi spell immunity before the cast; restores ACmi only for unit types n01P and n00U.

Evidence: Trig_ITEM_Null_Rod_Actions:49741.

## I017

- Selects non-enemies within 500 of the target point and attempts level-2 A06B invisibility: 55 seconds on normal units, 50 seconds on heroes. Organic allied/neutral ground and air target filter applies.

Evidence: Trig_ITEM_Scroll_of_Invisibility_Actions:49893, Trig_ITEM_Scroll_of_Invisibility_Func007A:49884.

## I02P

- Gives living allied nonmechanical, nonstructure, non-magic-immune units within 1000 +150% movement speed and +150% attack speed for 20 seconds; damage-taken bonus is 0%.
- Separately heals eligible allied organic units within 600 for 200 HP through a dummy item. No mana restoration.
- Removes the scroll on cast, regardless of remaining displayed charges. Starts A07C cooldown for 25 seconds on the caster.

Evidence: Trig_ITEM_Scroll_of_Frenzy_Actions:49967, Trig_ITEM_Scroll_of_Frenzy_Func008Func001Func001C:49923, Trig_ITEM_Scroll_of_Frenzy_Func013A:49960.

## I02T

- Attempts to remove dead nonhero nonstructure corpses within 800 of the target point.

Evidence: Trig_ITEM_Purge_the_Dead_Actions:50038, Trig_ITEM_Purge_the_Dead_Func002002003:50005, Trig_ITEM_Purge_the_Dead_Func005A:50029.

Caveat: The GroupEnum filter uses GetEnumUnit() rather than GetFilterUnit(). Its result depends on unrelated enumeration context; intended corpse cleanup is not reliable from static analysis. Gameplay code is unchanged.

## I01P

- Randomly selects up to 26 non-enemy units within 400 of the target point and attempts Anti-Magic Shell on each. Shell lasts 40 seconds and has a 200 spell-damage absorption field.

Evidence: Trig_ITEM_Scroll_of_AntiMagic_Actions:50075, Trig_ITEM_Scroll_of_AntiMagic_Func008A:50066.

## I021

- Selects non-enemies within 600 of the target point and attempts Inner Fire: +5% attack damage and +1 armor for 60 seconds.

Evidence: Trig_ITEM_Scroll_of_Inner_Fire_Actions:50115, Trig_ITEM_Scroll_of_Inner_Fire_Func007A:50106.

## I022

- Selects non-enemies within 400 of the target point and uses dummy Wand of Illusion I023 on each. I023 inherits AIil: 60-second illusion, 0% outgoing damage and 200% incoming damage.

Evidence: Trig_ITEM_Scroll_of_Illusion_Actions:50204, Trig_ITEM_Scroll_of_Illusion_Func007A:50195.

## I005

- Creates one o002 Healing Ward of the Gods for 90 seconds: 4000 HP, 75 fortified armor. Regeneration aura heals 30% maximum HP per second within 1600, targeting organic ground/air allies and neutrals.

Evidence: Trig_ITEM_God_Wards_Actions:50229.

## rat6

- On an attack-start event by a hero carrying Forked Fury against a nonstructure, non-magic-immune target, rolls 1..16; 3,7,12,15 trigger (25%). Requires A0HZ cooldown expired.
- Proc casts ACfl forked lightning for 250 damage to up to 8 targets; 900 cast range, 945 maximum length, 400 maximum spread, 165 area field. Starts a 10-second A0HZ cooldown.

Evidence: Trig_ITEM_Forked_Fury_NEW_Conditions:50326, Trig_ITEM_Forked_Fury_NEW_Func006C:50356, Trig_ITEM_Forked_Fury_NEW_Func006Func003Func010C:50333, Trig_ITEM_Forked_Fury_NEW_Actions:50372.

Caveat: Trigger uses EVENT_PLAYER_UNIT_ATTACKED, so proc does not require attack damage to land.

## ofro

- Whenever a unit already carrying buff B00L is attacked, a dummy casts A06R Frost Nova: 0 primary and 0 area damage; 175 radius and 1-second normal/hero slow duration.

Evidence: Trig_ITEM_Orb_of_Frost_Conditions:50403, Trig_ITEM_Orb_of_Frost_Actions:50410.

Caveat: This supplementary trigger checks the target buff, not whether the attacker currently carries Orb of Frost. Direct AIob cold values remain separate.

## tcas

- Constructs the selected wall orientation. After construction completes, wall lives for 40 seconds.
- Wall taunt orders enemy units within 550 to attack the wall.

Evidence: Trig_ITEM_Wall_Actions:50537, Trig_ITEM_Wall_taunt_Actions:50621.

## tgrh

- Constructs the selected wall orientation. After construction completes, wall lives for 40 seconds.
- Wall taunt orders enemy units within 550 to attack the wall.

Evidence: Trig_ITEM_Wall_Actions:50537, Trig_ITEM_Wall_taunt_Actions:50621.

## I02F

- AIil cast-finish handler checks whether the caster carries rat6 (Forked Fury). If so, kills all nonhero units owned by that player with the caster's unit type.

Evidence: Trig_ITEM_Illusion_Actions:50683, Trig_ITEM_Illusion_Func005Func004A:50668.

Caveat: This anti-illusion handler matches AIil, not custom A0PP. It does not expressly test IsUnitIllusion; it kills matching nonheroes.

## I01H

- Casting A08I also creates a dummy Flame Strike A08H at the target point: 350 radius, 17 full damage per 0.1-second interval, 2-second full-damage duration; 10 half damage per 0.25-second interval with 4-second duration field; building damage factor 0.1; maximum-damage cap 0.
- Dummy exists for 5 seconds. Ground enemies and neutrals only.

Evidence: Trig_ITEM_Scepter_Actions:50721.

## tkno

- Pickup automatically uses the Tome of Power only below hero level 18. At level 18 or above the item is dropped. Nonhero purchases are replaced with a ground item.

Evidence: Trig_ITEM_tomes_on_lv18_Actions:49699, Trig_ITEM_packhorse_buy_Actions:49646.

## stel

- Nonhero purchases are removed from the buyer and recreated on the ground. Packhorses cannot pick this up; an attempted pickup within integer distance 200 removes the ground item.

Evidence: Trig_ITEM_packhorse_buy_Actions:49646, Trig_ITEM_packhorse_pickup_Actions:49590.

## tgxp

- Nonhero purchases are removed from the buyer and recreated on the ground. Packhorses cannot pick this up; an attempted pickup within integer distance 200 removes the ground item.

Evidence: Trig_ITEM_packhorse_buy_Actions:49646, Trig_ITEM_packhorse_pickup_Actions:49590.

## tret

- Use while tracked by Guardian Energy Chamber removes the unit from that tracked group. Packhorses cannot pick this up.

Evidence: Trig_Guardian_Energy_Chamber_Tome_Of_Retraining_Actions:40375, Trig_ITEM_packhorse_pickup_Actions:49590.

## Pickup restrictions

| Item | Maximum copies | Prohibited unit IDs |
|---|---:|---|
| rat9 | 1 | O003 |
| stwa | 1 | O003, O00X |
| mcou | 1 |  |
| I02J | 1 |  |
| rwiz | 1 |  |
| ofro | 1 |  |
| I042 | 1 |  |
| ratf | 1 |  |
| ckng | 1 |  |
| I03C | 1 |  |
| belv | 1 |  |
| tmmt | 1 |  |
| rde3 | 1 |  |
| bgst | 1 |  |
| cnob | 1 |  |
| I006 | 2 |  |
| I009 | 2 |  |
| ciri | 1 |  |
| rlif | 1 |  |
| desc | — | H01I, E005, E007, H02G, E00U, N01L, E00Z |
| I01H | — | H01I, E005, E007, H02G, E00U, N01L, E00Z |
| evtl | — | O00X, O003, E00F, N00C, N00I |
| I04A | — | O00X, O003, E00A, E00U, E00O, H036 |
| tret | — | H02I, N00Z, H01H, H00A |
| modt | — | H02D |
| nspi | 1 | O003 |

Slippers of Agility, Soldier's Mask and Talisman of Evasion are mutually exclusive.

## Unbound / non-shop handlers

- A0QM: Thunderfury Staff selects A0QN purge for enemies (450 triggered normal/normal damage plus 1000 summoned-unit damage; 5s normal/1s hero duration) or A0QE for friends. No item has A0QM in its iabi list.
- A0DA: Interchange swaps caster and target positions and starts 60-second cooldown. I01D pickup preserves player timer, but I01D currently has no A0DA in its ability list; do not list this as a Ring of Titans cast ability.
- A0EH: Starts 5-second A0EH cooldown on all allied heroes; belongs to starting I01C, not shop sror.