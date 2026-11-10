# v14 balance and construction update

Installed Solo_Foots_8P_FFA_v14.w3x in the OneDrive Warcraft III Maps/Foots FFA directory. SHA256 bbbf6ca6c12f2b2365db5a5fa4dfc6f8a32b82aa098e1ddbc00c33116480dc1b.

Production timer intervals divided by 1.2 (20% more frequent waves). Starting gold 200. First tech tier 500; remaining main tiers already 1250/2000/3500/12000. Existing same-tier unit swaps retain their separate prices. Item costs reduced 10%, rounded to nearest gold, except original costs above 7000. Rod of Envy 1500 and Rod of Death 1250 override that discount. Standard inherited prices resolved from local base/custom game SLK data. All defined main bases and defensive/summoned tower types have 10% more HP. Detailed changes in verification.json.

Peasant build menu retains the altar and adds Scout Tower for 250 gold, no lumber. Scout Tower hotkey T within build menu; native Human Build B remains separate from custom peasant Blink Z at (1,2) and Repair (2,2). Blink clone preserves existing behavior and does not change other units' Blink.

Construction start validates five footprint samples on Yhdg/Ygsb grass, within 1450 of the owner's original base, radius at least 2700 from mid, and closest to that owner's base among all eight. Warcraft's normal placement/pathing rules also apply. Invalid builds are removed and 250 gold refunded. Cap is four living defensive towers including preplaced towers, upgraded forms and unfinished construction. Death/cancellation naturally frees slots because the count is computed from current units, rather than a lifetime counter. Summoned hero towers are buffed but excluded from the defensive construction cap.

Runtime and synchronized editor JASS compile; 1298 archive entries verified. verify.py checks prices, health, startup resources, production intervals, eight-sector construction permissions, dirt/mid/enemy rejection, cap and dead-slot reuse. Terrain, placement and UI assets unchanged. Live gameplay/rendering verification remains pending. Construction rejection occurs on starting construction rather than as a custom placement-preview overlay.
