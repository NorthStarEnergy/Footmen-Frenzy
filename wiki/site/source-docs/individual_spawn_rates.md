# Individual Spawn Rates

New source file:

```text
src/systems/individual_spawn_rates.jass
```

Injected test build:

```text
releases/799W-tester-individual-spawn.w3x
```

## What It Changes

The old system uses timer groups:

- `eight`: indexes `0-13` and `31-43`
- `five`: indexes `14-20` and `44-50`
- `ten`: indexes `21-30`

That makes spawn speed a property of a range, not a unit.

The new system gives every spawn index its own rate:

```jass
call ISR_SetRate(2, 11.00)   // Dark Knight
call ISR_SetRate(34, 9.50)   // Knight duplicate path
call ISR_SetRate(44, 7.25)   // Burning Archer
```

## Integration Steps

These steps have already been applied to the injected test build above.

1. Import or paste `individual_spawn_rates.jass` as custom script.
2. Keep the existing `set spawn variables` and `set base` setup triggers.
3. Disable old spawn triggers to prevent double spawning:

```jass
call DisableTrigger(gg_trg_eight_start_timer)
call DisableTrigger(gg_trg_eight)
call DisableTrigger(gg_trg_five)
call DisableTrigger(gg_trg_ten)
```

4. Start the scheduler after spawn/base setup:

```jass
call ISR_Start()
```

5. In `Tech Delay T1`, replace:

```jass
call EnableTrigger(gg_trg_ten)
call EnableTrigger(gg_trg_five)
```

with:

```jass
call ISR_UnlockTech1SpawnGroups()
```

## Useful Calls

```jass
call ISR_SetRate(2, 11.00)       // Dark Knight spawns every 11 seconds
call ISR_SetRate(2, 0.00)        // Dark Knight does not spawn
call ISR_SetUnlocked(2, false)   // Temporarily lock Dark Knight spawns
call ISR_SetUnlocked(2, true)    // Unlock Dark Knight spawns again
```

## Notes

The system still uses the existing arrays:

- `udg_spawn_unit`
- `udg_unit_HP`
- `udg_unit_armor`
- `udg_unit_att_base`
- `udg_unit_range`
- `udg_unit_level`
- bounty arrays

So it preserves the current trigger-applied stat model, while removing the timer-group limitation.
