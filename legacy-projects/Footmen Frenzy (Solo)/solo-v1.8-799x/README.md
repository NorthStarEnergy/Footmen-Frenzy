# Solo Foots v1.8 — four-player 799X update 08

Playable output: `release/Solo_Foots_v1.8_4P_799X_UPDATE08.w3x`.

Base: `Solo_Foots_v1.8_4P_PRELOAD_TEST07.w3x`, the newest four-player solo baseline found locally. Donor: `FF799X_Rx_Fed_Rewards_v80_TEST.w3x`, the latest mainline 799X artifact found in the neighboring project. Exact paths and hashes are in `migration.json`.

## Included

- Latest Gragus runtime: barrel presentation and detonation, Fortitude healing/armor and cleanup across all six ranks, body slam, ultimate, cast animations, and supporting effects.
- Latest Gul'dan (the Orianna ability kit): current Gul'dan model/voice and cast animations, orb movement and carrier tracking, command effects, Protect, Shockwave, tooltips, icons, and cleanup.
- Both heroes join the existing solo random/category selection pool at roster indices 92 and 93. Category 1 is used because solo supports 11 categories; donor category 15 would not be a regular category choice. Existing random tavern offerings are retained, so neither hero is guaranteed in every match's random stock.
- Architect recruitment now reads upgrades and ownership from the actual caster rather than a stale shared player index. Solo's message filtering is retained.
- The donor's effective attack-range setter is applied to absolute army range assignments in spawn, preload, upgrade, recruitment, and unburrow paths. Existing incremental bonuses and sniper-specific paired changes remain intact.
- 39 scoped object records and 45 imported presentation assets, including disabled buttons, Gragus portrait, and model textures. Runtime tooltips are restricted to the imported heroes.

## Compatibility decisions

The four-player slots, teams, terrain, shops, KOTH, solo spawn timing, selection policy, economy, XP, camera, preload, and existing cleanup/item-limit improvements are preserved. The source comparison found 446 differing shared functions; this is not a list of 446 missing fixes. Many donor bodies precede solo's leak fixes, item refactor, pooled spawning, and solo-specific behavior. `shared-differences.json` inventories them and `migration.json` lists the exact imported and changed functions.

799X's team taverns, roster additions for other custom heroes, observer/backend features, army balance changes, and v67–v80 team-based Pub/colossus/reward progression are not transplanted. These are separate systems or balance policies, not drop-in four-player solo fixes. Guardian remains subject to solo's existing excluded-hero policy.

## Verification and delivery

- Final runtime passes pjass with local Warcraft native definitions.
- Every object table parses to its exact boundary; unrelated object records remain equal.
- Every OM_/FS_ function is byte-for-byte equal to the v80 donor's function body.
- Targeted actual-JASS translation tests cover repeat-safe Fortitude cleanup for all six ranks, damage/heal/radius progression, and repeated effective range updates under mocked native behavior.
- Packed payloads read back byte-for-byte. All 1,208 unrelated archive members remain unchanged.
- 6,966 total assertions, mostly preservation checks; these are not 6,966 gameplay scenarios.
- SHA-256: `7529c5a174b2ee98fc5e0b90bdd20276a0ec14f0850501962907722a28415300`.
- Installed into new `Maps/Solo Foots/GPT/Solo_Foots_v1.8_4P_799X_UPDATE08/` and `Maps/Solo Foots/Solo Tests/` paths. TEST07 is retained.

Warcraft III engine playtesting remains pending. Test both heroes through selection, death/revival, every ability rank, Fortitude recast/expiry, orb leash/ownership changes, and a full four-player match. Mock tests cannot establish actual engine animation, sound, native range semantics, or multiplayer synchronization.

Do not save this map through World Editor: as documented by the parent project, the baseline GUI trigger sources do not represent its compiled runtime. `src/war3map.j` and the scoped object/assets here are authoritative for this update.

## Rebuild

Use the bundled Python runtime to run `build.py` from the project root. Compile `src/war3map.j` using the local pjass plus common.j/Blizzard.j and save output to `compiler.log`, then run `verify_pack.py`. The legacy compiler needs execution outside the desktop sandbox on this machine. Helper libraries are reused read-only from the neighboring Footmen Frenzy project. `inspect.py` extracts the inputs by known member names; these archives do not contain a listfile. Diagnostic/adaptation scripts record the investigation and are not rebuild steps.
