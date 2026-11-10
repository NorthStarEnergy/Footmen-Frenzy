# v80 weaker-team kill rewards

Built from the v79 sustained-lag colo map. Separate TEST artifact; not installed or deployed.

## Rule

Normal Pub only, using the existing v67 mode gate. Starting at hero level 7, XP and kill gold are multiplied by `1 - min(0.60, max(0, hero fractional level - opposing baseline - 1) * 0.15)`.

The opposing baseline is the mean fractional level of active registered primary heroes on the victim's team. Dead heroes remain in that average. Missing/inactive heroes are excluded; no valid baseline means no penalty. For a hero victim, its own fractional level raises the baseline if higher than its team's mean. Killing a strong hero on a weaker team therefore remains worthwhile.

| Lead above baseline | Reward retained |
| --- | --- |
| 1 level or less | 100% |
| 2 levels | 85% |
| 3 levels | 70% |
| 4 levels | 55% |
| 5+ levels | 40% |

Fractional leads interpolate. This multiplier applies after the existing progression rate. A level-10 hero versus a level-7 team receives 70% of its usual rewards: base kill XP * 70% existing rate * 70% new factor = 49% of base XP. A level-7 ally sharing that kill retains its own catch-up rate.

Army units, summons and hero victims qualify. XP is evaluated separately for each recipient; gold uses the killing player's primary hero, including kills by that player's army, summon or spell dummy. Neutral units/colos and structures are exempt from the discount. Passive income, transfers, lumber and base-destruction pooled gold are not routed through the discount.

## Reward plumbing

Warcraft's built-in kill awards do not provide a victim-dependent per-recipient multiplier. Normal Pub therefore uses explicit kill XP and player-victim bounty awards, with native XP set to zero and player bounty flags disabled. Other modes keep their native paths. The handler registers before the map's other death handlers so it reads the victim before cleanup and pays ordinary XP before scripted supplements. It is initialized once, with mode entry/exit restoring or disabling native rewards as appropriate.

The handler uses the map's 18-entry GrantHeroXP table, the native normal-unit XP recurrence, 75% summoned-victim factor, 1200 range, nearby allied sharing with global allied fallback, and level-18 exclusion from the share divisor. Dead, suspended, illusion, inactive and unregistered heroes do not receive these ordinary kill awards. Tower kills give no ordinary XP; passive structures and locust victims give no ordinary XP. All recipient rates are snapshotted before payouts to avoid a level-up changing a later recipient's share on the same kill. Fractions are carried per primary hero, reset on replacement. Native neutral gold remains enabled; player-victim gold rolls the authored bounty dice and displays the resulting payout to the killer.

All five existing scripted supplement call sites now pass their death victim to the multiplier. The four existing winning-factor gold bonus branches also apply the factor. The anti-cheat 25% XP rate remains in the explicit XP calculation and cannot re-enable native XP. v77 colo levels/curve, v78 level-10 catch-up and v79 capped colo assistance are preserved.

## Validation and remaining engine checks

The actual JASS helpers execute in a Python translation harness with mocked Warcraft natives: curve bounds and monotonicity, primary identity, team averaging, higher-level hero victims, recipient-specific catch-up, sharing/range/global fallback, summon factor, bounty dice, anti-cheat, mode transitions, excluded recipients, simultaneous level-up rate snapshots, fraction handling and table cleanup. Runtime pjass and authoritative WCT JassHelper/pjass compilation are required by build.py. Packed files are reread byte-for-byte; unrelated archive entries are compared against v79.

This is NOT engine-playtested. Because ordinary Pub payouts are now explicit, compare equal-level kills against v79 before assessing balance. Include shared and distant XP, all base tiers, any experience-granting items, custom summoned/illusion units, tower kills, simultaneous AoE deaths and colo clearance. The handler targets this map's registered primary-hero model and does not implement Warcraft's separate melee single-hero town-hall-tier XP bonus. Confirm that none of the custom base upgrades activate that native bonus; if they do, preserve it in the explicit base-XP path before release. Native XP rounding/event order and bounty display behavior also need in-game comparison. Do not treat compilation or mocked tests as an engine equivalence guarantee.

Rebuild with the bundled Python and build.py. On this machine the legacy JASS compilers require execution outside the restricted sandbox. Tuning constants are in globals.j; reward code is in rewards.j.
