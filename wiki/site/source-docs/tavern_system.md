# Tavern System

This is the recommended first system to document and eventually migrate.

## Goals

- Define hero pools in data files.
- Define tavern rawcodes in data files.
- Populate taverns from weighted pools.
- Prevent duplicate heroes within the same tavern.
- Keep debug output easy to enable and disable.

## Open Questions

- How many taverns are active in the current map?
- How many heroes should each tavern stock?
- Should duplicates be prevented globally or only within each tavern?
- Are categories equal weight, or should some categories appear more often?
- Should tavern stock refresh during the game?

## Future Lua Shape

```lua
PopulateAllTaverns()
PopulateTavern(tavernUnit, poolName, count)
PickRandomUniqueHeroes(pool, count)
```
