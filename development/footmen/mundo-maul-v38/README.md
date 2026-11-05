# Mundo Maul — consolidated v38

Built from consolidated Stats UI v37. Mundo's C ability is now **Maul**.

- Enemy heroes and creeps (including player-owned creep types) are flipped behind Mundo. Reuses the prior half-second Fling with 50/80/110/140/170/200 magic damage. Flips can be used while digesting.
- Other eligible allied/enemy organic ground units are swallowed through native Kodo Devour on Mundo himself. Digestion, damage-based self-healing, burp, allies-only completion burst, native bounty/XP and cargo release remain unchanged.
- Shared range 250, cooldown 20 seconds, no mana or added health cost. All six active/research descriptions and the hero description use Maul.
- Previous Devour exclusions remain for the swallow branch. Neither branch affects flying, mechanical, magic-immune, invulnerable or Colossal targets. Allied heroes/creeps are not flipped. Spell-resistant soldiers remain ineligible for swallowing.
- Native Devour is a hidden helper behind the visible targeted Maul ability, because native Devour cannot safely provide hero targeting. Failed/interrupted helper casts clear pending state and refund Maul's cooldown. One meal per Mundo; another flip does not replace the meal.

136 behavior/object checks pass against the actual translated JASS, including the existing Cleaver, Demon Ascension, Undying and Devour regressions. The full map compiles. Archive readback and function/object comparisons verify unrelated v37 content is preserved, including its Stats UI and Pub insta-mass changes. Live Warcraft testing is still pending for native spell dispatch, cargo and visuals.

Build with `build.py`, run `checks.py`, compile `src/war3map.j` using the existing pjass/common.j/Blizzard.j, run `pack.py`, then use `Install.ps1` to install the verified new filename in both Test folders. Earlier versions remain intact.
