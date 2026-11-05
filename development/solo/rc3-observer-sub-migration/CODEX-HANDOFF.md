# Handoff to Codex — rc3 Observer-Substitution migration

**From:** Claude (Claude Code session), 2026-07-25
**What:** An rc3-native port of the Solo Foots observer-substitution workflow (commit `3b37c26`) into the authoritative full-12-player rc3 map. Static-validated, packed, round-trip-verified. **Not yet runtime-tested.**

This is a self-contained brief. You do not need the Claude chat log — everything is on disk.

> Every concrete claim below was independently re-verified against the on-disk files by 6 separate checks — all **CONFIRMED**, zero discrepancies (hashes, round-trip, parse/structure, leave+votekick ordering, vision/camera teardown, the three KOTH swaps + the deliberately-untouched identical line, init wiring). The artifact/path caveats those checks surfaced are folded into §1–§4 below.

---

## 1. Where everything is

Workspace: `C:\Users\Ryan1\Documents\Solo Foots Development\rc3-observer-sub-migration\`

| File | SHA256 | Role |
|---|---|---|
| `baseline\war3map.j` | `cdef1d67f73ac9aba5b4bbd7cc2b0633860bbb22ae29fc5ff9abe7326d81b7d8` | Untouched rc3 extract = migration baseline |
| `work\war3map.j` | `8e110b8252e1b6407771855c747735a1782fdddb7e1f16f1cd0f8f19cb680541` | **Modified script — the deliverable source** |
| `war3map.rc3-observer-sub.diff` | — | Unified diff baseline→work, **for human review only** — see caveat below |
| `Reforged_Footmen_Frenzy_v7.9.9W-rc3-observer-sub-test.w3x` | `040b1705481bebc5ac6740a1ba33bc5a8f3a65f4e2cbe19a93fad4ba7128d003` | Packed test map (copy also in `Maps\799b\`) |
| `reports\{migration,validation}-report.md`, `reports\manual-test-checklist.md` | — | Full write-ups |

> **Canonical artifact = `work\war3map.j` (SHA `8e110b82…`).** Only that file — or the byte-identical script embedded in the test `.w3x` — reproduces the validated hash. **The `.diff` does NOT reproduce it byte-for-byte:** `git diff --no-index` stripped the CRLF line endings, so `baseline + diff` yields uniform-LF/CRLF variants with *different* SHAs (the JASS content is textually identical — 0 diffs after `tr -d '\r'` — so behavior is unaffected, but the byte/hash chain the whole validation rests on breaks). Treat the diff as a review record; to integrate, take `work\war3map.j` wholesale, not a patched reconstruction.

Baseline source of the extract: `…\Solo Foots Development\tmp\rc3-12p-inspect\files\war3map.j`.
Original packed map (**do not overwrite**): `…\Warcraft III\Maps\799b\Reforged_Footmen_Frenzy_v7.9.9W-rc3.w3x` (SHA `a2a938a2a636f1ade7f067a4fa9232cfd6ae7369351dbc65c0fb34cc2617dbab`, unchanged by this work).

Tools used, each in its **own subdir** of `…\Solo Foots Development\tools\bin\`: `JassParseCheck\JassParseCheck.exe`, `ReplaceWar3MapScript\ReplaceWar3MapScript.exe`, `MpqExtract\MpqExtract.exe` (last extracts under `<outdir>\files\`).

---

## 2. What changed (10 edits, all in `war3map.j`)

A `SoloSub_*` system of 23 functions plus 10 splices (net +576 lines). Edits were made by unique text anchor (never line index) because rc3's `war3map.j` has **mixed line endings** — the appended `FF_*` block uses bare LF, the generated body uses CRLF. There is exactly **one** real `globals` block (column-0 `globals`/`endglobals`, balanced 1/1), but the substring `endglobals` appears on **11 lines** (10 are vestigial `//endglobals from <lib>` comment markers from a merge tool), so a naïve `endglobals` anchor is ambiguous — anchor on the preceding unique line. The 10 edits collapse to **9 diff hunks** because R2 (SoloSub insert) and R5a (KOTH predicate) are ~4 lines apart and merge.

| # | Site (baseline line) | Change |
|---|---|---|
| R1 | globals, before `endglobals` (2860) | `SoloSub_*` global state |
| R2 | before `// Trigger: KOTH Income` (17462) | the 23-function `SoloSub` system |
| R3 | `Trig_player_leaves_Actions` top (49528) | `if SoloSub_LeavePrelude() then return endif`; non-votekick branch → `udg_temp_player = SoloSub_EffectiveLeaver()` |
| R4 | `InitTrig_player_leaves` (49613) | leave-event registration for observers 12–23 on the **same** `gg_trg_player_leaves` |
| R5a/b/c | KOTH-income + hill-reset-on-leave + hill-reset-on-destroy predicates | `slotState==PLAYING` → `SoloSub_IsEffectivePlayer` |
| R6 | `Trig_Observer_Vision_Fix_Func001A` (16031) | record each observer's fog-modifier handle in `SoloSub_observerFog[]` |
| R7 | `Trig_player_destroyed_Actions` top (49779) | `call SoloSub_OnPositionDestroyed(...)` |
| R8 | `InitCustomTriggers` (50659) | `call InitTrig_SoloSub()` (once) |

Design: gameplay leave (0–11, still active) → preserve position + mark pending + announce `-sub`; an **active teammate** invites an available observer (12–23, team 4); on accept the observer gets shared advanced control of the canonical slot, mirrored alliances, allied vision (leftover full-map observer vision torn down via the tracked fog modifier), colour/team/name change, camera released. Substitute leave → maps to canonical, rc3 cleanup runs once. Inherited base destroyed → observer freed, rc3 elimination continues. Votekick / full 0–11 registrations / KOTH / victory-defeat / visibility / multiboard all preserved. See `reports\migration-report.md` for every rc3-specific adaptation and the full edge-case matrix.

Key rc3 gotchas the port had to handle (reusable facts):
- **Votekick fires the leave trigger via `TriggerExecute(gg_trg_player_leaves)`** with `udg_Votekick_Defeat_Kicked_Player=true` → `GetTriggerPlayer()` is invalid there; the prelude checks that flag first and preserves rc3's votekick branch verbatim.
- Observer vision is a **script fog modifier** per team-4 player (`CreateFogModifierRectBJ(FOG_OF_WAR_VISIBLE)`, handle discarded) — removable at runtime once tracked; **not** an engine referee slot.
- rc3 has its own spectator camera `FF_oc_*` gated on `GetPlayerTeam==4`; there is **no** `SoloCam_*` and **no** `SoloFootsDisplayMessage*`.
- Victory/defeat keys off `udg_player_active[]`/`udg_leave_or_votekick[]`, not slot state, so it needed no change. `SoloSub_IsEffectivePlayer(canonical) == (slotState==PLAYING)` whenever no substitution is active, so R5a/b/c are no-ops in ordinary games.

---

## 3. Validation already done (see `reports\validation-report.md`)

- `JassParseCheck.exe work\war3map.j` → **OK, exit 0**, 9,503 declarations.
- No undefined functions/globals; no duplicate functions/globals; `function`/`endfunction` balanced 2963/2963 (+23); every native/BJ exists in JassHelper `common.j`/`Blizzard.j`; define-before-use verified.
- Leave events 0–23 registered; `InitTrig_SoloSub` defined & called exactly once; **0** references to `SoloCam_*`/`SoloFootsDisplayMessage*`.
- Original rc3's embedded `war3map.j` == `baseline` (`cdef1d67…`); test map's embedded `war3map.j` == `work` (`8e110b82…`, byte-for-byte round-trip); original `.w3x` unchanged; `war3map.w3i` and `war3map.w3u` identical between original and test map → slots 0–11 remain `MAP_CONTROL_USER`.

---

## 4. What I'd like you (Codex) to do

1. **Independently re-verify** (the tree is shared; confirm nothing drifted). Note each tool is in its own subdir:
   - `"…\tools\bin\JassParseCheck\JassParseCheck.exe" work\war3map.j` → expect `OK`, exit 0.
   - re-hash the four files above (canonical: `work\war3map.j` == `8e110b82…`).
   - `grep -c 'SoloCam_\|SoloFootsDisplayMessage' work\war3map.j` → 0; confirm Player(0)..Player(23) leave registrations and a single `call InitTrig_SoloSub()`.
   - **also re-confirm the non-script claim** (none of the 6 automated checks re-derived it): extract `war3map.w3i` from both the original and test `.w3x` and confirm they’re identical — this is what backs "slots 0–11 stay `MAP_CONTROL_USER`."
2. **Decide pipeline integration — recommended default:** treat `work\war3map.j` as the source of truth and drop it in **wholesale** (it is byte-exact and round-trip-verified). My test map was built by injecting it straight into the rc3 `.w3x` with `ReplaceWar3MapScript` (repoints the `war3map.j` block to appended uncompressed bytes; old bytes stay as dead data). **Do not** rebuild `work` from `baseline + war3map.rc3-observer-sub.diff` — that will show a phantom hash "drift" that is purely CR bytes (see the §1 caveat). If you must patch a *differently-located* `war3map.j`, use `git apply -p1` from the workspace root (diff paths are `a/baseline/… b/work/…`), expect CRLF normalization, and re-derive behavior from JASS content, not the hash. **Never regenerate `war3map.j` from World Editor** — it wipes the injected script.
3. **Run / coordinate the controlled multiplayer test** in `reports\manual-test-checklist.md` (20 scenarios). Priorities: #8 shared-advanced-control command coverage, #9 no residual enemy/full-map vision, #11 single cleanup on substitute leave, #15 KOTH size/income during a sub.
4. **Resolve the observer-slot type first — this gates the vision tests, it is not a footnote.** My vision teardown works *only* if rc3 grants observer sight via the script fog modifier (which it does in `Trig_Observer_Vision_Fix`). If any observer slot is configured as a true engine referee/observer in `war3map.w3i`/lobby, script cannot revoke that slot's vision, and test #9 becomes meaningless until this is settled. Confirm the slot type before/at the start of multiplayer testing.

---

## 5. Known risks / unverified

- **All runtime behavior is unverified** — shared advanced control (unit orders, shops, custom `-commands` keyed on `GetTriggerPlayer()`), live fog-vision teardown, resource spending, event ordering, desync. Static validation cannot cover these.
- **Observer vision** is the one engine caveat (see #4 above).
- **Governance deviation:** I removed Solo's enemy fallback — only active teammates can `-sub` a lost position; a team with no active human teammate can't be subbed (documented, intentional).
- **Not production-ready on static validation alone.**

Open questions (with recommended defaults so this is actionable even without a reply):
- **Build pipeline location.** I injected directly into the rc3 `.w3x`; if this map has a verified-build path (like the Solo `Build-VerifiedMap.ps1` / recode-pass flow), that's the better long-term home. *Default if unanswered:* the direct-inject test map is fine for the controlled multiplayer test — fold into your pipeline only when promoting past testing.
- **Code placement.** *Default:* keep the `SoloSub` block inline where it is (before the KOTH-Income trigger). Relocating it into a `src/systems/*.jass` module to match your recode-pass convention is optional cleanup, **not** required for correctness, and would only churn the byte-exact artifact — do it as a deliberate follow-up pass, not as part of accepting this change.
