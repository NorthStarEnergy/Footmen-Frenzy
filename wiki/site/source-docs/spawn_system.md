# Spawn System Notes

Readable source: `extracted/799W-tester/files/war3map.j`

## Why This System Is Hard To Tune

The map does not simply let spawned units use their Object Editor stats.

The spawn triggers create a unit from `udg_spawn_unit[index]`, then immediately overwrite many fields:

- max HP
- current HP
- armor
- defense type
- base damage
- attack dice
- attack sides
- attack cooldown
- attack range
- unit level
- bounty values

That means changing a spawned unit in Object Editor may do nothing if the trigger later overwrites that field.

## Current Legacy Spawn Groups

| Trigger | Active | Timing | Spawn indexes |
|---|---|---:|---|
| `eight` | yes | `udg_spawnTimer`, 8.00 seconds | `0-13`, `31-43` |
| `five` | disabled at init, enabled by `Tech_Delay_T1` when `udg_version == 5` | 6.25 seconds | `14-20`, `44-50` |
| `ten` | disabled at init, enabled by `Tech_Delay_T1` when `udg_version == 5` | 8.75 seconds | `21-30` |
| `eight_mass_bonus` | registered, dormant until `udg_spawnMassTimer` starts | 20.00 seconds during premass bonus | `0`, then `31-43` path exists |

## Current Balanced/New Spawn Groups

These triggers exist but are disabled in the extracted script and no `EnableTrigger` call was found for them.

| Trigger | Timing | Spawn indexes |
|---|---:|---|
| `eight_new` | 8.00 seconds | `0-3` |
| `ten_new` | 10.00 seconds | `20-35` |
| `twelve_new` | 12.00 seconds | `40-43` |

## Replacement Direction

Use `src/systems/individual_spawn_rates.jass`.

The replacement keeps the current stat arrays but removes the hardcoded timer groups. Every spawn index gets its own `ISR_SetRate(index, seconds)` value.

This makes changes like "nerf Dark Knight spawn rate" or "make Rifleman slower than Headhunter" a one-line edit instead of a rewrite of the `eight`, `five`, and `ten` trigger ranges.
