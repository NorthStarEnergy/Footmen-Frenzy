# Solo Foots FFA v8

Installed map: `C:\Users\User\OneDrive\Documents\Warcraft III\Maps\Foots FFA\Solo_Foots_8P_FFA_v8.w3x`

SHA256: `300b82fcacb9a4aff31ee1bc409f50a942f072de1765e569034f64dc952127d2`

Changes: matched tower pairs at radius 3640 and lateral offsets -640/+640; ordered rear shop rows; two-page creep and recipe shops without separate page buildings; eight alternating central weapon/armor shops; explicit Tavern and Human Altar art in unit and skin tables; removal of inherited hero tier prerequisites while preserving the two-hero cap; eight independent player forces; eight-player scoreboard and -kd; observer full vision and day/night entrance vision; four large middle colossi and equal camp distribution for active bases. Terrain and BLP1 minimaps are preserved from v7.

799X port uses the installed v71 donor, including 179 Gragus/Orianna/Guardian functions, their object/assets dependencies, and the attack-range helper. It does not indiscriminately replace the solo map with the four-team donor's rules or import the uninstalled experimental v80 rewrite.

Validation: runtime JASS and synchronized editor source compile; 1,295 archive entries round-trip; `verify.py` passes the edited control-flow checks for forces, paging, altar stock/cap, scoring and fog; ten simulated colossus waves distribute equally to eight sectors without overlapping spawn coordinates; shops, camps and towers connect to the center; all 16 towers remain on grass. Installed file hash matches the release.

Actual Warcraft III rendering, purchases and live multiplayer behavior remain untested. Test v8 explicitly; older map versions remain in the same folder.

Build: use the bundled Python executable to run `build.py` from this workspace. The legacy JASS tools need unsandboxed execution. Then run `verify.py`. `build.py` reuses the existing v7 compiler/editor/archive pipeline and v4 object/placement tools.
