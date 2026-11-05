# SoloFoots v1.7 KOTH Autostart Test

## Fix

King of the Hill was unable to start because normal solo mode explicitly set `udg_mode_koth` to false and the KOTH trigger initializers contained no actions or timer/death events.

This build:

- enables KOTH during normal solo-mode startup;
- executes the KOTH mode trigger automatically;
- creates the neutral hill immediately when normal solo mode starts;
- restores the original KOTH setup, income, hill-death, reset, display, progression, and invulnerability trigger wiring;
- leaves the retired Colossal system disabled.

## Verification

- `JassParseCheck`: passed with 8,873 top-level declarations.
- Test-map SHA256: `201E27C17F857C1FECF8647022EC988965FE0DC1620B6D2A98FE71AB296761F2`.
- Source script SHA256: `EEF66B700C467785AB7CB3A6EF4F2D366A355339A8D189381D45388269ABBB9E`.
- Round-trip extracted script SHA256: exact match.
- 1,204 files extracted; the pre-existing broken `(listfile)` remains the only extraction warning.

## In-game check

Start a normal solo game and confirm that the neutral KOTH hill appears at map center as soon as the game mode starts. Kill the hill and confirm that ownership changes, income begins every three seconds, and the three-second invulnerability expires.
