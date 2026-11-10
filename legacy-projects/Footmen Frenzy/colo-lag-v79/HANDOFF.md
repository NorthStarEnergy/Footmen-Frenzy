# v79 sustained-lag colo XP assistance

Built from v78, retaining the level-10 fractional catch-up, v77 colo curve and middle-boss levels, and v75 army spawn-level fix. Normal Pub only. No fixed-wave milestone deadlines.

For each active registered primary hero, the next milestone is 10, 13 or 16. The field qualifies when a strict majority of the other surviving teams have a strict majority of their active primary heroes at that milestone. In a four-team game that means two other teams, normally with two of their three heroes at the milestone. With two teams remaining, the one opposing team represents the field. Defeated teams and teams with no active primary heroes are ignored.

The hero must remain at least one full fractional level below the milestone for 90 continuous seconds while the field qualifies. Before activation, breaking either condition resets the wait. Once activated, help tapers through the last fractional level and stops at the milestone. It also stops if the field no longer qualifies. Reaching the next band or replacing the primary hero requires a fresh wait. The existing anti-cheat penalty cannot be bypassed by this extra award.

Only direct colo units and the middle boss are tagged. The tag records their original spawn wave. At death, live nearby primary heroes on the killing team share the unmodified native XP value for the extra-award calculation. Advanced heroes still count in the divisor. Only eligible lagging heroes receive extra XP; subsequent summons, ordinary armies, hero kills and untagged units do not award this extra bonus.

Extra XP = floor(base colo XP / nearby live allied primary heroes * min(1.0, 0.4 * fractional milestone deficit)). This is an additional final XP grant, not multiplied again by the existing player XP handicap. It is capped by both the current milestone shortfall and the remaining wave budget.

Each player's extra-XP budget per original spawn wave is half the XP band between their current level and the next, fixed when the first eligible kill is processed. All packs and the middle boss from the same wave share that budget. It does not reset on repick, collecting another team's pack, or a new wave spawning while old units remain alive. Example: a level-7 hero has an 800-XP band to level 8, so that wave's extra budget is at most 400 XP. This is bounded help, not a guaranteed level or an automatic timed grant.

Payments run on a zero-delay timer after the death event so current XP is rechecked after normal XP awards. The extra grant is clamped at the target and revalidates hero identity, alive state, eligibility and mode. Tags are consumed once, timer state is cleaned, and native-rate refresh runs after payment. Engine event ordering and simultaneous multiplayer deaths still require in-game validation.

Validation: actual JASS helpers executed through the translation harness with mocked natives. Checks cover majority/remaining-team rules, continuous 90-second waits, fractional deficits, all three milestones, duplicate kills, repicks, participation, current shortfall, original-wave budgets, disabled modes and anti-cheat. 1,920 payout-cap cases pass. Runtime pjass and authoritative editor JassHelper/pjass pass. Runtime/WCT/source_roundtrip agree; packed payloads re-read exactly; 1,400 unrelated entries preserved. Not installed or deployed.

Tuning: globals.j contains delay, minimum deficit, bonus-per-level and cap constants. Rebuild with bundled Python using build.py; the legacy compilers need execution outside the restricted sandbox on this machine.
