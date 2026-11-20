# Mundo Cleaver Wound test

Build: `release/FF799X_Rx_Mundo_Cleaver_Wound_Test.w3x`.
Includes the earlier Mundo Disease Cloud and zero INT/mana work. Based on the separate v68-derived Mundo health-kit map; parallel Lux, Stalker and icon changes are not included.

On cleaver contact: small blood impact and positional native `MetalMediumChopFlesh` sound. Surviving targets receive a 0.2-second movement lock, followed by a 70% movement slow for 2 seconds. Only Speed Scroll's `Bspe` haste is canceled and suppressed on the struck unit (checked every 25 ms). Other buffs remain. A genuine dispel clears the slow and ends haste suppression. Repeated hits refresh one wound rather than stacking.

The movement stop still uses the engine's Ensnare movement-root behavior internally, but through new AMwR/BMwR records. All projectile, target and buff artwork is blank, so the stock falling net is not used. Both a native 0.2-second duration and explicit timer cleanup remove this private root; the stock Beng buff is never removed, to avoid interfering with unrelated roots. This is not PauseUnit or a stun, although native Ensnare can interrupt channeling. The slow uses new AMwS/BMwS records and affects movement only. Native speed floors and other buffs may affect the final speed; 70% is the configured debuff strength.

The timer ends on expiry, dispel, death, unit removal, ownership change, invulnerability, magic immunity, or replacement. It removes only its own buffs and casting helpers. Failed helper orders are cleaned up. The first 0.1 second allows native casts to complete; absence of the slow after that cancels the wound. Damage, healing, projectile movement, pickup and bloodied bonus formulas are unchanged.

Validation: runtime pjass, synchronized editor JassHelper/pjass, 40 executed mocked JASS/object checks, and archive/object preservation. The installed game's UnitCombatSounds.slk confirms the native sound label. An in-game playtest is still needed to verify dummy cast timing, visuals, sound and movement behavior in the engine.

Rebuild: run `prepare.py`, `compile.py`, `checks.py`, `pack.py` with bundled Python. `prepare.py` optionally accepts an absolute baseline map path that already includes the prior Mundo health-kit patch. It refuses an already-patched cleaver. Run every validation again after rebasing.

Integration: add `hashtable MW_Hash = null` to runtime and WCT globals; insert wound.j before MU_OnCleaverHit; copy only the changed MU_OnCleaverHit and MU_Init changes; add AMwR/AMwS and BMwR/BMwS objects; update AMu1 tooltips. Preserve other agents' code and object records. `changes.json` lists the exact delta; never overwrite a combined map with this standalone build.

Engine checks: hit a moving hero, confirm no net and movement resumes after 0.2 seconds; apply Speed Scroll before and during the wound; try it after 2.2 seconds; dispel the wound; test repeated hits and death; confirm normal attacks/spells and intended channel interruption; listen for one flesh chop on normal and lethal hits.
