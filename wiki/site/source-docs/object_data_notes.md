# Object Data Notes

Readable object data references:

- `../extracted/799W-tester/files/war3map.w3u`: units
- `../extracted/799W-tester/files/war3map.w3a`: abilities
- `../extracted/799W-tester/files/war3map.w3t`: items
- `../extracted/799W-tester/files/war3map.w3q`: upgrades
- `../extracted/799W-tester/files/war3map.imp`: imports

## Verified Unit Object Example

From `war3map.w3u`:

```text
Base unit rawcode: Udea
Custom unit rawcode: U002
Likely unit: Death Knight
```

Example fields recovered:

```text
usrg = 3600
ubba = 250
urac = creeps
uhrt = always
urun = 250
uwal = 250
ucbs = 0.75
```

These are raw object-editor field IDs. Keep raw dumps separate from design notes until field names are mapped.
