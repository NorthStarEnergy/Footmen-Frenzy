# Soul Hook v70 production review

**Verdict: hold for fixes and engine testing. Suitable as a test candidate; not production approved.**

Reviewed `\\10.0.0.106\Users\Ryan1\Transfer\DemonKnight_SoulHook_v70\FF799X_Rx_DemonKnight_SoulHook_v70.w3x` on October 30, 2026. Map SHA-256: `f311fd6821d1746504a6cbfb93fdc0a23937758c3b6ff4843bff7b05f076fd9b`. The local copy is under `actual/`. No map code or remote files were modified.

## Findings to resolve before release

1. **[P2] Existing drag suppresses a separate cast's damage and stun.** `actual/war3map.j:8436` places the `-32` drag claim check around the entire catch, including hit registration, damage, stun and visuals. A target being dragged by another Soul Hook receives none of these effects from a second hook while the claim exists. Reproduced by overlapping two casters: the first rank-1 hook deals 120; the second rank-6 hook deals zero instead of 320 and issues no stun. This makes cast effectiveness depend on unrelated displacement ownership. Keep per-hook hit registration/damage/stun independent of the decision to allocate or replace a drag. Add an overlapping-caster regression case.

2. **[P2] Reaping Axe and Soul Hook can move the same victim simultaneously.** Soul Hook owns displacement through hash key `-32` (`8436–8452`); Reaping Axe uses `-3` (`8180–8190`). Neither checks the other's claim. Both kind-2 and kind-12 states move the same unit each tick (`8584–8605`, `8641–8659`). Reproduced with the hero's ordinary Z/C combination: the victim moves 28.125 + 40 = **68.125 units in one 31.25 ms tick**, rather than Soul Hook's specified 40. This also lets both pull budgets accumulate on the victim. Establish an explicit displacement priority/replacement rule shared by these two abilities, or deliberately specify and test stacking if that is the intended design. Each hook still needs its independent damage hit.

3. **[P2] Return-trip catches disagree with the supplied behavior description.** `DK_HookCatch(i)` runs unconditionally after head movement at `8629`, including while `DK_Return[i]` is true. An enemy entering the path only after the turnaround is caught, damaged, stunned and dragged. Reproduced in the executable checks. The README describes checks on the way out. Choose outbound-only or both-pass behavior and align code, tooltips, documentation and balance tests. This is a behavior mismatch; both-pass catching is not inherently invalid.

## Smaller targeting issue

The catch is a circle sampled at discrete head positions, rather than a swept capsule. A stationary target at `(84.375, 149)` relative to a caster at `(0, 0)` aiming along +X is missed on both passes, despite being 149 units from the trajectory. This is a small edge inconsistency in the advertised 300-wide catch. Use segment-to-target distance if a continuous corridor is desired. Current code does implement a literal radius around each sampled head position.

The head travels 450 units and has a 150 radius, so its forward catch can reach roughly 600 units from the cast origin. That follows from the code; balance and tooltip wording should account for it. Damage has no target-count cap. These are tuning considerations, not proven balance defects.

## Evidence and strengths

- Independently matched the packaged map hash and baseline v68 hash. Compared full runtime function bodies: exactly four changed functions and four added hook functions, matching the supplied scope. Global declarations are identical. The four supplied hook helper bodies match the packed script.
- Inspected packaged `ADk5`, `ADk6`, `HDk1` and `hgr1` object records. Soul Hook is in the hero's ability list; its rank mana/cooldown/range values and stun durations match the documented numbers. Channel uses `carrionswarm`; Reaping Axe uses `shockwave`.
- Executed translated bodies from the **packaged JASS**, including the actual allocator, tick, catch, drag step, free routine and death handler, with mocked Warcraft natives. All six ranks produced the correct damage, a 150-unit drag from initial distance 300, and clean state/group/effect/lightning ownership.
- Collision snap rejection restored the original victim position. Caster death, including synchronous death during the damage callback, cleaned the head and drag claims. One hundred sequential casts left no active DK states, groups, effects, tethers or hash claims.
- The hook helpers contain no client-local gameplay branches. This is encouraging code evidence, not proof of multiplayer synchronization.

Reproduction harness: `review_checks.py`; results: `review-checks.json`; identity/source comparison: `independent-verification.json`; extracted object evidence: `actual/objects.json`.

## Remaining release gate

**No Warcraft engine, editor-save, multiplayer, visual or balance playtest was performed in this review.** Supplied compiler success was reported by the author; this review did not rerun pjass. Mocked native calls cannot prove actual Storm Bolt order acceptance, stun/spell-block interactions, collision behavior, or frame-time performance.

After fixing the findings, test map loading and editor round-trip; all six learn ranks and C/E hotkeys; actual stun duration and immunity/spell-block behavior; walls, cliffs, buildings and crowded units; simultaneous hooks and the Z/C combination; source death/removal/ownership transfer; and repeat casts with multiple clients. Stress-test dense Footmen armies: every caught victim allocates a stun dummy, a flash state and potentially a drag state, while allocation scans for free slots. No engine performance conclusion is established.

Preserve this v70 package. Deliver any implementation changes as a new candidate version, then repeat the logic checks and required engine tests before production approval.
