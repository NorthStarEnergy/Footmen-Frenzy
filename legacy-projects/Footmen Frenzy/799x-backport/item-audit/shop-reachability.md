# Shop reachability and summon audit

Checked placed-unit creation functions, all script references, dynamic AddItemToStock calls, all map unit utra/ubui/uupt/useu edges, inherited unit profiles. Page handlers select existing units; they do not create page shops.

| Shop ID | Shop | Reachable | Reason |
|---|---|---|---|
| n000 | Archvault | True | Created in map initialization. |
| n004 | Armor Shop | True | Created in map initialization. |
| n007 | Personal Shop | True | Created in map initialization. |
| n012 | Altar of Legends | True | Created in map initialization. |
| h001 | Footmen Frenzy Reforged | True | Created in map initialization. |
| n01B | Weapons Shop | True | Created in map initialization. |
| n01T | Protection Shop | True | Created in map initialization. |
| n01Y | Recipes Shop | True | Created in map initialization. |
| h01G | Mode - Selector | True | Created in map initialization. |
| n02K | Archvault | False | No creation or reachable build/train/upgrade/sold-unit path. |
| h02H | OBS commands | False | No creation or reachable build/train/upgrade/sold-unit path. |
| n02N | Assault Shop | True | Created in map initialization. |
| n02V | Assault Shop | False | Page button handlers select this type if already nearby; no creation or incoming build/train/upgrade path exists. |
| n02Z | Recipes Shop | True | Created in map initialization. |
| n03Z | Assault Shop | False | Page button handlers select this type if already nearby; no creation or incoming build/train/upgrade path exists. |
| n045 | Waveplayers Shop | True | Created in map initialization. |
| n046 | Kids Store | True | Created in map initialization. |
| h010 | Stockpile Tower | False | No creation or reachable build/train/upgrade/sold-unit path. |
| u01B | Tomb of Relics | False | Only incoming path is u01C -> u01B upgrade; u01C is never created or made available. Scout Tower upgrades do not include either shop. |
| u01F | Ancient Texts | False | No creation or reachable build/train/upgrade/sold-unit path. |

## Custom Hero purchases

96 tokens explicitly added to temporary shops. All actual object prices match script refund prices: True.

- Only the generated hero can purchase in its own team build area.
- One ability per Z/X/C/V slot; occupied slot rejects further purchases.
- Each ability can be learned only once per team.
- Only one Z AoE ability per team.
- Successful purchase adds level-1 ability and removes token; denied purchases refund configured price and restock token.
- Build closes after 45 seconds and all 32 shops are removed.
- No script to upgrade purchased ability levels or free/reassign slots was found. UnitAddAbility does not itself make purchased spells part of the hero skill-learning list.
- No explicit UnitMakeAbilityPermanent call is present in the purchase handler.
- Shops use n000 and retain its 11 static items while adding 12 tokens. Actual command-card visibility of all added stock requires game verification.

| Gold | Token | Ability | Slot |
|---:|---|---|---|
| 150 | Firebolt (Z015) | ANfb | Z |
| 225 | Shadow Strike (Z021) | AEsh | Z |
| 225 | Howl of Terror (Z024) | ANht | Z |
| 225 | Summon Hawks (C063) | ANsw | C |
| 250 | Wind Walk (Z019) | AOwk | Z |
| 250 | Death Coil (Z020) | AUdc | Z |
| 250 | Howl of Terror (X030) | A0G2 | X |
| 250 | Blink (X032) | AEbl | X |
| 250 | Devour Magic (C059) | Advm | C |
| 250 | Summon Quilbeast (C062) | ANsq | C |
| 275 | Shockwave (Z008) | AOsh | Z |
| 275 | Storm Bolt (Z013) | AHtb | Z |
| 275 | Drunken Haze (X027) | ANdh | X |
| 275 | Sleep (X036) | AUsl | X |
| 275 | Spiked Carapace (X045) | AUts | X |
| 275 | Wind Walk (X047) | ANwk | X |
| 275 | Shadow Strike (C058) | A0LH | C |
| 275 | Summon Beetles (C064) | A029 | C |
| 275 | Summon Wolves (C065) | AOsf | C |
| 300 | Breath of Fire (Z002) | ANbf | Z |
| 300 | Forked Lightning (Z006) | ANfl | Z |
| 300 | Acid Bomb (Z012) | ANab | Z |
| 300 | Thunder Clap (Z022) | AHtc | Z |
| 300 | Frost Armor (X028) | AUfu | X |
| 300 | Banish (X033) | AHbn | X |
| 300 | Healing Spray (X034) | ANhs | X |
| 300 | Thorns Aura (X037) | AEah | X |
| 300 | Incinerate (X046) | ANic | X |
| 300 | Death Coil (C050) | ACdc | C |
| 300 | Serpent Wards (C060) | AOsw | C |
| 300 | Summon Treants (C066) | A007 | C |
| 300 | Magic Resistance (C071) | A03T | C |
| 300 | Slow Poison (C072) | Aspo | C |
| 325 | Frost Nova (Z001) | AUfn | Z |
| 325 | Fan of Knives (Z003) | AEfk | Z |
| 325 | Chain Lightning (Z005) | AOcl | Z |
| 325 | Carrion Swarm (Z007) | AUcs | Z |
| 325 | Impale (Z014) | AUim | Z |
| 325 | War Stomp (Z023) | Awrs | Z |
| 325 | Silence (X025) | ANsi | X |
| 325 | Thunderclap (X029) | A0FZ | X |
| 325 | Brilliance Aura (X039) | AHab | X |
| 325 | Preservation (X041) | A09B | X |
| 325 | Healing Wave (C051) | AOhw | C |
| 325 | Endurance Aura (C052) | AOae | C |
| 325 | Devotion Aura (C056) | AHad | C |
| 325 | Summon Bear (C061) | ANsg | C |
| 325 | Feedback (C068) | Afbk | C |
| 350 | Cluster Rockets (Z011) | ANcs | Z |
| 350 | Justice Hook (Z017) | A0GU | Z |
| 350 | Hex (X026) | AOhx | X |
| 350 | Death Wards (X031) | A0FD | X |
| 350 | Divine Shield (X035) | AHds | X |
| 350 | Vamp Aura (X038) | AUav | X |
| 350 | Evasion (X042) | AEev | X |
| 350 | Bloodlust (Jaood) (X043) | A0ID | X |
| 350 | Polymorph (X048) | ACpy | X |
| 350 | Command Aura (C053) | ACac | C |
| 350 | Trueshot Aura (C054) | AEar | C |
| 350 | Unholy Aura (C055) | AUau | C |
| 350 | Summon Clockwerk Goblins (C067) | A0AH | C |
| 375 | Thunder Axe (Z004) | A0L0 | Z |
| 375 | Bash (X044) | ACbh | X |
| 375 | Critical Strike (C069) | AOcr | C |
| 375 | Spell Shield (C070) | A0QC | C |
| 400 | Flamestrike (Z009) | AHfs | Z |
| 400 | Flaming Lasso (Z016) | Amls | Z |
| 400 | Firestorm (Z018) | A051 | Z |
| 400 | Pocket Factory (X040) | ANs1 | X |
| 400 | Cattlebruiser Frost Strike / Cold Strike (C049) | A0PZ | C |
| 400 | Tichmech Aura - Angel of Doom version (C057) | A012 | C |
| 500 | Blizzard (Z010) | AHbz | Z |
| 650 | Resurrection (V078) | AHre | V |
| 650 | Tranquility (V079) | AEtq | V |
| 650 | Avatar (V084) | AHav | V |
| 650 | Doom (V085) | ANdo | V |
| 700 | Panda Ultimate (V074) | ANtm | V |
| 700 | Death and Decay (V075) | AUdd | V |
| 700 | Transmute (V076) | A0G0 | V |
| 700 | Animate Dead (V086) | AUan | V |
| 700 | Big Bad Voodoo (V091) | AOvd | V |
| 700 | Locust Swarm (V094) | AUls | V |
| 750 | Summon Chimaeras (V073) | A039 | V |
| 750 | Inferno (V077) | AUin | V |
| 750 | Stampede (V088) | ANst | V |
| 750 | Summon Phoenix (V092) | AHpx | V |
| 750 | Summon Druids (V093) | A00Y | V |
| 750 | Mass Serpent Ward (V095) | A0EN | V |
| 800 | Yamamoto Cannon (V080) | Afod | V |
| 800 | Shadow's Ultimate (V081) | A044 | V |
| 800 | Strong Man Ever's Ultimate (V082) | A030 | V |
| 800 | Drunken Templar's Ultimate (V087) | A0GC | V |
| 800 | Exophate's Ultimate (V089) | A07Q | V |
| 800 | Starfall (V090) | AEsf | V |
| 850 | Zeus Ultimate (V083) | A0U6 | V |
| 850 | Reincarnation (V096) | AOre | V |

## Summoned units

- Summons one Siege Engine for 40s: 1300 HP, 50 fortified armor, 275 move speed. Enabled weapon 1 deals 151-161 siege damage every 1s at 250 range, targeting structures/debris only. Weapon 2 data exists but attacks-enabled=1 disables it. No unit abilities.
- Summons 12 Penguins of Chaos for 120s each: 15000 HP, 35 fortified armor, 500 move speed, 1 HP/s regeneration. Weapon 1: 101-108 chaos damage every 0.5s at 128 range vs ground/debris/items/wards. Weapon 2: 51-58 chaos damage every 2s at 128 range vs structures. 70% cleave in 200 radius; 900-radius aura reduces enemy attack and move speed by 80%; spell immunity (magic damage factor 0) and Resistant Skin.