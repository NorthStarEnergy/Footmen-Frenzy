# rc3 Observer-Substitution Migration — deliverables

Port of the Solo Foots observer-substitution workflow (commit `3b37c26`) into the
authoritative full 12-player rc3 map, adapted to rc3's own leave/KOTH/vision/votekick/camera code.

## Contents
| Path | What it is |
|---|---|
| `baseline/war3map.j` | Untouched rc3 extract (SHA `cdef1d67…`), the migration baseline |
| `work/war3map.j` | Modified rc3 script (SHA `8e110b82…`) — the deliverable source |
| `war3map.rc3-observer-sub.diff` | Unified diff, baseline → work (9 hunks) |
| `Reforged_Footmen_Frenzy_v7.9.9W-rc3-observer-sub-test.w3x` | Packed test map (also copied to `…\Maps\799b\`) |
| `reports/migration-report.md` | Every integration point + rc3-specific adaptation |
| `reports/validation-report.md` | All validation commands & results |
| `reports/manual-test-checklist.md` | 20-scenario controlled-multiplayer test matrix |
| `tools-out/verify-extract/` | Files extracted from the test map (round-trip proof) |
| `tools-out/verify-orig/` | Files extracted from the original rc3 map (baseline proof) |

## One-paragraph summary
When a gameplay player (0–11) leaves normally, the position is preserved and marked pending
instead of being cleaned up; an active teammate types `-sub`, invites an available observer
(12–23, team 4), and on acceptance the observer gets shared advanced control of the canonical
slot with mirrored alliances, appropriate allied vision (leftover full-map observer vision is
torn down via the tracked fog modifier), a colour/team/name change, and its spectator camera
released. A substitute leaving maps back to the canonical slot and runs rc3 cleanup once; a
destroyed inherited base frees the observer and continues rc3's elimination. Votekick, the full
0–11 leave registrations, KOTH, victory/defeat, visibility and multiboard behaviour are preserved.

**Not production-ready on static validation alone** — requires the controlled multiplayer test
matrix. The one engine caveat is observer vision (see reports).
