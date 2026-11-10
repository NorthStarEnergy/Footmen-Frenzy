# 799X v10 — verified item findings (partial)

This is not the complete shop inventory. Values below come from the map's item and ability object data. Casts and scripted effects still need review, so an item may have effects not listed here. Prices are gold. The map creates shop units n004, n01B, n012, n007, n01Y, n01T, n02N, n02Z, n045 and n046, among others; shop listings alone do not establish every dynamically available item.

| Gold | Item | Verified object-data abilities |
|---:|---|---|
| 100 | Robe of the Magi +10 | +10 intelligence (+4 and +6 abilities). |
| 150 | Medaillon of Glim | +4 armor and +100 maximum mana. |
| 200 | Ring of Protection +5 | +5 armor and +4 strength. |
| 250 | Belt of Giant Strength +10 | +10 strength. |
| 250 | Gloves of Haste | +20% attack speed. |
| 300 | Pendant of Mana | +300 maximum mana. |
| 300 | Claws of Attack +25 | +25 attack damage. |
| 400 | Ring of Resilience | +100 maximum health and 10% spell damage reduction. |
| 500 | Periapt of Vitality | +400 maximum health. |
| 500 | Shockwave | Cast: 500 damage; 1,200 maximum distance; 300 final area. |
| 600 | Shield of the Gods | +8 armor and +300 maximum health. |
| 600 | Totem of Might | +10 agility and +5 attack damage. |
| 1,200 | Mantle of Intelligence +25 | +25 intelligence; Brilliance Aura has 3.5 mana regeneration per second at level 1. |
| 1,200 | Scroll of Beating | Roar: +150% damage, 1,200 radius, 180 seconds. |
| 1,500 | Shockwave of the Gods | Cast: 1,400 damage; 1,300 maximum distance; 300 final area. |
| 2,000 | Gauntlets of Ogre Strength +30 | +30 strength and +15 health regeneration per second. |
| 2,500 | Claws of Ultimate Devastation | +100 attack damage. |
| 3,000 | Scroll of Frenzy | The trigger affects eligible allied units within 1,000 range with a 20-second Berserk ability whose movement and attack speed fields are both +150%; it removes the scroll on use. The caster also receives a separate Berserk effect. |
| 30,000 | Ring of J33Bus | +1,000 to each attribute, invulnerability, and 70% cleaving attack. |

## Corrected tooltip

Scroll of Frenzy's old tooltip claimed a 1,200 radius and three charges. The spell trigger selects units within 1,000 range and removes the item on use. It also claimed 200% attack speed for the nearby-unit effect, while the A0LS Berserk ability used by the trigger has a 150% attack-speed field. A corrected tooltip is included in the separate ItemTooltipAudit map. Its caster effect and an additional triggered area heal need full gameplay review before the item can be considered completely audited.

The corrected map was verified to have just the one skin-object tooltip changed; the map script, item and ability data, unit data, strings, placed units and map information match the original. It has not been tested in Warcraft III.
