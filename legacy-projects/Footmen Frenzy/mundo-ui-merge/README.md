# Combined UI repair and Mundo test map

Use `release/FF799X_Rx_UI_Repair_Mundo_Combined_Test.w3x` for the combined test. This merges the complete Mundo health-kit, Cleaver Wound and Disease Cloud ramp into the UI agent's repaired v71 map. The inherited v71 content includes Lux, Veigar and the existing Stalker implementation. It does not make the later requested Stalker movement/Blink fixes.

Disease Cloud transitions from light green through darker green and purple/dark green to near-black over 10 seconds. Damage and health drain rise linearly from their previous base values to double, then stay capped while active. Toggling off resets the ramp. Existing trails keep their emitted color and damage; overlapping clouds from the same Mundo do not stack. Low health shuts down the toggle before drain kills Mundo. At rank 6, damage rises from 110 to 220/sec and health drain from 32 to 64/sec. Existing regeneration still offsets net health loss.

Mundo's invisible zero Intelligence/mana enforcement and the updated cleaver are included: 0.2-second movement stop without net artwork, 70% slow for 2 seconds, Speed Scroll haste suppression, and flesh impact sound/blood. Details remain in the `mundo-cloud-ramp` and `mundo-cleaver-wound` developer notes.

The UI repair's string table and eight restored icon/model files remain byte-identical to its repaired v71 release. The merge changed only nine existing Mundo functions, added eleven helper functions, updated Mundo ability text/INT, added private abilities/buffs, and imported 21 cloud models. Runtime/editor scripts remain synchronized. Unrelated function bodies and object fields were verified unchanged; 1,378 archive entries were preserved and 1,358 known original files were fully decoded successfully.

Validation: runtime pjass, editor JassHelper/pjass, 65 cloud checks, 40 cleaver checks and 10 zero-resource checks passed. These execute translated JASS with mocked Warcraft natives and inspect object/model data. In-game visuals, native timing and behavior still need playtesting. The map has not been installed or deployed.

Baseline: `ui-label-repair/release/FF799X_Rx_v71_UI_Labels_Icons_Fixed.w3x`, SHA-256 `f382c0c30a08d78d195e8444a831bd621f88f57c7f63188976bb0260fafa28ac`. `changes.json` records the exact merged delta; `verification.json` records the output hash. Rebuild by running `prepare.py` with a repaired baseline path, then `compile.py`, `checks.py`, `cleaver_checks.py`, `resource_checks.py`, and `pack.py`. Preparation refuses conflicting edits instead of silently replacing them.
