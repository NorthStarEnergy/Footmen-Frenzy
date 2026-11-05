# UI labels and archive asset repair

Ready for use and narrow integration. No other chat's source files were changed.

Outputs:
- release/FF799X_Rx_v67_UI_Labels_Icons_Fixed.w3x: repaired version of the installed Pub XP v67 lineage.
- release/FF799X_Rx_v71_UI_Labels_Icons_Fixed.w3x: repaired Stalker v71 lineage, suitable as the baseline for the separate Mundo integration. SHA-256: f382c0c30a08d78d195e8444a831bd621f88f57c7f63188976bb0260fafa28ac.

Findings:
- v65/v64 strings had normal CRLF; v66 prepare decoded raw CRLF and then used Windows write_text, producing CRCRLF. v67 repeated this, producing CRCRCRLF. Fixed repeated CR runs throughout war3map.wts without changing text, string IDs, or intended logical newlines. All 16,692 string records remain.
- Eight assets remain in the archive hash table but cannot be read through StormLib beginning in the available v54 UI/startup source. Restored their exact readable v53 bytes: Brew/EnergyPotion, LightningBolt, disabled UnholyFrenzy, disabled RottenAura, Katana, disabled FrostShock, Void Arrow model, AbyssAura model.
- This is not evidence that the custom label functions were deleted. Archive-preservation checks that preserve unreadable compressed payloads are insufficient to detect these failures.
- Fixed the WTS writers in taverns-v66/prepare.py and pub-xp-v67/prepare.py so rebuilding does not repeat the newline corruption.

Validation:
- All known asset inventory names plus current import-manifest names were read from the output; readable predecessor assets match byte hashes, and restored assets match the donor.
- Every undeclared archive entry is preserved; runtime JASS, editor WCT, and object records are unchanged.
- v67: 1,334 named payloads verified, 1,352 unrelated archive entries preserved.
- v71: 1,358 named payloads verified, 1,376 unrelated archive entries preserved.
- No in-engine playtest or installation performed. Test timer title alignment, selected footman/hero names, overhead owner labels, and Brew purchase/inventory/disabled icons after starting a fresh match.

Integration:
Use repaired v71 as a baseline for the separate Mundo work; do not replace it with the older Mundo branch. repair.py also accepts an absolute input-map path and an output tag to apply the same narrow repair to another completed build. If the baseline is already repaired, do not rerun the script's assertion that WTS needed repair; preserve the repaired WTS and restored assets verbatim.
