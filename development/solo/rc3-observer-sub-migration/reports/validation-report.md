# rc3 Observer-Substitution Validation Report

Date: 2026-07-25. All commands were run against the files in this migration workspace.

## 0. Artifacts & hashes

| File | SHA256 |
|---|---|
| `baseline/war3map.j` (untouched rc3 extract) | `cdef1d67f73ac9aba5b4bbd7cc2b0633860bbb22ae29fc5ff9abe7326d81b7d8` |
| `work/war3map.j` (modified) | `8e110b8252e1b6407771855c747735a1782fdddb7e1f16f1cd0f8f19cb680541` |
| `…-rc3-observer-sub-test.w3x` | `040b1705481bebc5ac6740a1ba33bc5a8f3a65f4e2cbe19a93fad4ba7128d003` |
| original `…-rc3.w3x` (must be unchanged) | `a2a938a2a636f1ade7f067a4fa9232cfd6ae7369351dbc65c0fb34cc2617dbab` (identical before and after packaging) |

## 1. Baseline is byte-for-byte the rc3 embedded script — PASS
Extracted `war3map.j` from the **original** `…-rc3.w3x` → SHA256 `cdef1d67…d81b7d8`, identical to `baseline/war3map.j`. The splice script also re-asserts this hash immediately before writing, so the modification is provably built on the pristine rc3 script.

## 2. JASS parse (War3Net) — PASS
```
JassParseCheck.exe work/war3map.j
OK   …\work\war3map.j (9,503 top-level declarations)   EXITCODE=0
```
The bundled `Footmen Frenzy Development/tools/JassCheck` uses the same `War3Net.CodeAnalysis.Jass` parser (verified in its `Program.cs`), so it adds nothing beyond this. No pjass binary exists on disk; the checks below cover the semantic items pjass would catch.

## 3. Static structural checks — PASS

| Check | Result |
|---|---|
| Undefined functions | Every `SoloSub_*`/`InitTrig_SoloSub` call resolves to a definition (0 unresolved). Every native/BJ called (`DisplayTimedTextToPlayer`, `GetPlayerAlliance`, `SetPlayerAlliance`, `CreateFogModifierRectBJ`, `GetLastCreatedFogModifier`, `DestroyFogModifier`, `GetPlayableMapRect`, `ResetToGameCameraForPlayer`, dialog BJs, `ConvertedPlayer`, `GetConvertedPlayerId`, …) exists in `common.j`/`Blizzard.j`. |
| Undefined globals | All referenced globals exist: new `SoloSub_*` (added), `udg_all_players`, `udg_player_active`, `udg_Votekick_Defeat_Kicked_Player`, `FF_oc_mode`, `FF_oc_followed`. |
| Duplicate functions | `grep '^function ' | sort | uniq -d` → none. `function`/`endfunction` balance 2963/2963. |
| Duplicate globals | `SoloSub_*` names are unique (no prior use). One `globals`/`endglobals` at column 0, balanced. |
| Invalid local placement | War3Net parse succeeded (would be a syntax error otherwise); all `SoloSub_*` locals are declared at function top. |
| Invalid JASS syntax | Parse OK. |
| Function count delta | 2940 → 2963 = **+23**, exactly the SoloSub function set. |

## 4. Event registration — PASS
* Gameplay leave 0–11 on `gg_trg_player_leaves`: **present** (all 12 retained).
* Observer leave 12–23 on the **same** trigger: **present** (added).
* `-sub` chat registered for Player(0..11) via loop in `InitTrig_SoloSub`.
* Choose/confirm dialog events registered via `TriggerRegisterDialogEventBJ`.

## 5. Init wiring — PASS
`InitTrig_SoloSub` defined once, called once, from `InitCustomTriggers` (after `InitTrig_Observer_Vision_Fix`). It is defined textually before `InitCustomTriggers`, satisfying JASS define-before-use.

## 6. No references to absent Solo-only systems — PASS
`grep 'SoloCam_mode|SoloCam_followed|SoloFootsDisplayMessage'` → **0** matches.

## 7. Define-before-use ordering — PASS (manual)
`SoloSub_IsEffectivePlayer` is used first at the KOTH-income predicate (baseline 17466); the SoloSub block is inserted before it (17462). `LeavePrelude`/`EffectiveLeaver`/`OnPositionDestroyed`/`InitTrig_SoloSub` are all defined before their call sites (49528 / 49779 / 50659). Intra-block callees precede callers.

## 8. Packaging & round-trip — PASS
* `ReplaceWar3MapScript …-rc3.w3x work/war3map.j …-rc3-observer-sub-test.w3x war3map.j` → payload SHA `8e110b82…` (== `work/war3map.j`).
* Original `…-rc3.w3x` SHA identical before and after packaging → **original map not modified**.
* `MpqExtract …-rc3-observer-sub-test.w3x …` → embedded `war3map.j` SHA `8e110b82…` == modified source (**byte-for-byte round-trip**). The lone `MpqExtract` failure is `(listfile)`, a known always-fail on these maps (not a regression).
* Non-script MPQ files unchanged between original and test map: `war3map.w3i` identical, `war3map.w3u` identical. Since player-slot controls live in `war3map.w3i` (unchanged) and `main()`'s `SetPlayerTeam(Player(0..11), …)` is outside the diff, **gameplay slots 0–11 remain `MAP_CONTROL_USER`** in the test map.

## 9. Handle-leak review — PASS (see migration report §5)
No new force/group/rect/location/unit/effect handles. Fog modifiers are destroyed-before-recreated (≤1 per observer). Dialogs/timer/triggers are game-lifetime singletons. Buttons follow rc3's existing votekick-dialog pattern.

## What static validation does **not** cover
Static analysis cannot verify runtime behaviour of shared advanced control, live fog-modifier vision, event ordering under real network conditions, or desync. Those require the controlled multiplayer test matrix (see `manual-test-checklist.md`). **Do not treat this map as production-ready on static validation alone.**

## Commands (reproducible)
```bash
# 1. baseline == original embedded
MpqExtract.exe  "…\Maps\799b\Reforged_Footmen_Frenzy_v7.9.9W-rc3.w3x"  verify-orig
sha256sum verify-orig/files/war3map.j        # cdef1d67…

# 2. parse
JassParseCheck.exe work/war3map.j            # OK, exit 0

# 3. structure
grep -c '^function ' work/war3map.j          # 2963
grep -oE '^function [A-Za-z0-9_]+' work/war3map.j | sort | uniq -d   # (none)

# 4/5/6. registration, init, absent symbols
grep -o 'TriggerRegisterPlayerEventLeave(gg_trg_player_leaves, Player([0-9]*))' work/war3map.j   # 0..23
grep -c 'call InitTrig_SoloSub()' work/war3map.j                    # 1
grep -c 'SoloCam_mode\|SoloCam_followed\|SoloFootsDisplayMessage' work/war3map.j  # 0

# 8. package + round-trip
ReplaceWar3MapScript.exe "…-rc3.w3x" work/war3map.j "…-rc3-observer-sub-test.w3x" war3map.j
MpqExtract.exe "…-rc3-observer-sub-test.w3x" verify-extract
sha256sum verify-extract/files/war3map.j     # 8e110b82…  == work/war3map.j
```
