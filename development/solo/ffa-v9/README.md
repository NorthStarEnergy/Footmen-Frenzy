# Solo Foots FFA v9

Installed in `C:\Users\User\OneDrive\Documents\Warcraft III\Maps\Foots FFA\Solo_Foots_8P_FFA_v9.w3x`.

SHA256: `95b99c17614caffa7670b2d2994be17017d6931c7267b38442a334fe53fd100c`

The middle radius is reduced 15% from v8 (nominal circle area reduction 27.75%). Terrain, pathing, cliff blockers, eight middle shops, entrance vision and forward neutral camps follow the same contraction. Displacement tapers to zero at radius 3300; towers, bases, rear shops and outer terrain remain unchanged. BLP1 minimaps are regenerated.

Validation: runtime and editor JASS compile; 1,295 archive entries round-trip; verify.py passes path connectivity for 688 starting footmen, ten colossus waves and all shops/towers, and regression checks for eight-player forces, shop pages, altar stock, scoring and visibility. In-game rendering/gameplay has not been tested.

The user's King-mode question refers to vassal conquest, NOT King of the Hill. V8 and v9 do not contain this mode. The current branch eliminates defeated players. An earlier implementation exists in `C:\Users\User\Documents\ChatGPT\Footmen Frenzy\mini-foots\audit\solo-latest-test05\files\war3map.j`, with SKKing-based sovereignty, captures and whole-kingdom transfers, base rebuild after three seconds, one-use -defect with ten-second protection, -king status, succession on king departure, and a twenty-second all-player conquest hold. No vassal-mode port was requested or made in this terrain revision.
