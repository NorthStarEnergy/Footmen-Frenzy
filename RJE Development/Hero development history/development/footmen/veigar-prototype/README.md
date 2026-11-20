# Veigar prototype — 799X v33

Built on FF799X_Rx_Mundo_v32, retaining its prior changes.

Load FF799X_Rx_Veigar_v33.w3x and type `-veigar` in chat to summon a temporary Lich-model hero beside your current hero (or at your starting location). Repeating the command selects the same hero or revives it at the start location. Both abilities are available immediately without spending skill points. The prototype does not replace your main hero or occupy a tavern slot.

- **E — Event Horizon:** immediate 300-radius circular boundary, lasting 3 seconds. Its 50-unit-wide rim stuns enemies touching it on creation or crossing it afterward for 1.5 seconds, once per enemy per cage. The interior is freely traversable. 80 mana, 18-second cooldown, 900 cast range.
- **W — Dark Matter:** marks a 225-radius area, then drops a dark effect from above and deals 300 magic damage after 1.25 seconds. Enemies can escape before impact. 100 mana, 10-second cooldown, 900 cast range.

These are initial prototype balance values, not a claim of current League of Legends tuning. Both spells exclude allies, buildings, invulnerable and magic-immune units. Each cast has independent state; caster death does not cancel a launched spell, but removing the caster does. Cages use swept segment checks, so scripted displacement across a boundary also counts as crossing. Full-map unit scans support fast crossings; performance with many simultaneous cages needs engine testing.

## Verification

`checks.py` executes the spell JASS through the existing project translator with mocked Warcraft natives: 28 geometry, targeting, timing, overlap, death/removal and cleanup checks pass. `build.py` compiles the complete script with pjass, reads back the four changed archive payloads, and verifies 1,348 unrelated archive entries are unchanged. Existing object records are retained; only the prototype hero and three abilities are added. Live Warcraft visuals, targeting UI and feel remain untested.

Rebuild with the bundled Python runtime and `build.py`. The existing 32-bit pjass compiler requires execution outside this session's sandbox. `Install.ps1` checks the generated checksum before copying the release into both existing Warcraft Maps/Test locations and the shared 799x-backport/release directory.
