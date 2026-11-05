# SoloFoots v1.7 Performance Test 6

## Output

- Test map: `C:\Users\Ryan1\Documents\Warcraft III\Maps\Solo Foots\SoloFootsv1.7-Performance-Test-6.w3x`
- Map SHA256: `227CF0E8FA9A72B6648159A6F2A7F6AD6561010B2513EB266D22B76A18FC8EDB`

## No Mute hero blacklist

The map's WTS object metadata contains three units with the `(nomute)` editor suffix:

| Hero | Rawcode |
|---|---|
| Falcon | `E01G` |
| Corruptor | `H05E` |
| Witch Doctor | `H05N` |

Test 6 blocks all three in four places:

1. The normal random tavern picker rejects their rawcodes.
2. Every hero-stock call, including Mirror and Classic branches, uses the same checked helper.
3. Unit availability is disabled for all 24 player slots when SD starts.
4. Their preplaced showroom copies are removed before taverns are stocked.

The three rawcodes were already outside the normal 91-hero SD catalogue. The explicit blacklist prevents a later catalogue expansion from accidentally enabling them.

## Verification

- Build script SHA256: `E8C08B774E9FAAC5DCF05E3A83900116D17806B46EEA855DFA8D1BFAE0D5B9B1`.
- Round-trip script SHA256: exact match.
- Object-data SHA256: `B0F8043E9D18088AD264B64F4AAAA0FFCD813EAB6288CE915A1FCCB2CA1C332E`.
- Round-trip object-data SHA256: exact match.
- `pjass`: passed on source and round-trip script.
- `JassParseCheck`: passed on source and round-trip script.
- 1,204 files extracted; the pre-existing broken `(listfile)` is the only warning.
- All 1,202 files other than `war3map.j` and `war3map.w3u` match Test 5 exactly.

Gameplay execution still requires Warcraft III. In game, verify that none of the three units appears in either tavern and that normal taverns still contain 12 choices each.
