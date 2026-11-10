# Solo Foots 8P FFA + King v11

Installed: `C:\Users\User\OneDrive\Documents\Warcraft III\Maps\Foots FFA\Solo_Foots_8P_FFA_v11.w3x`

SHA256: `b5d4549efa9e3d9e12336416dfbd3bd2d8c51833b363c12cea0372fbc67f19a1`

UI source: the latest installed 799X Test map, `FF799X_Rx_Stalker_v71.w3x`, SHA256 `c76bb8429f1df124ffe743354bc81fb9ffc300cd406f64b1fd92823b5c900c88`. Build reads that installed archive directly. Its custom frame UI consists of zoom controls and the detailed player Stats panel; all 27 related functions and three TOC/FDF assets are included with roster/stat adaptations. Uninstalled experimental later-numbered map branches are not the donor.

Zoom: vertical slider beside the minimap, numeric distance, lock button, 1400-6000 range, saved `FFR_Zoom.txt` preference, `-z`/`-zoom` chat support for all 24 game slots including observers. Camera restore updates the numeric label and slider. Camera distance/far-plane visuals remain local and do not reveal fog of war.

Stats: minimap Stats button, local panel/close toggle, eight roster-ordered player rows, hero icons/levels, unit kills/deaths, hero kills/deaths, ten-second allied assists, hill captures, buildings destroyed and successful Transmute target-death counts. The UI death handler is registered before normal/King death handling so captures cannot turn a victim into an ally before building stats are counted. King-mode personal and kingdom scoring remain intact.

Shop corrections: audited 81 placed shops and eight starting taverns. Rear rows follow the original stock-family order with a tavern seat and the previously overlooked upgrades shop. Rows follow each base's actual wall rather than a fixed radius; all shops face the map center. Eight middle weapon/armor shops remain alternating. The single Archvault moved from the central objective to a wall-tip position. Constructed hero altars are also faced toward center, without overriding the player's chosen build location. Shops have at least 192 center-to-center spacing; clear rear-wall and front-approach checks pass. Own-base/kingdom-base vision is 1500 to include the rear rows, with checks that it does not reveal opposing towers. Bases, towers, terrain and pathing are otherwise unchanged from v10.

Build and checks: `build.py`, `shops.py`, `verify_ui.py` (also runs `verify_king.py`), and `verify_shops.py`. Runtime/editor JASS compile, 1,298 archive entries round-trip and installed hash matches. Tests execute the actual packaged JASS with native mocks: zoom clamps/lock/cache/local isolation, Stats local toggles and eight-slot counters, King-mode 56 directed captures/defections and all previous scenarios. Shop checks compare binary placements with runtime creation, inward angles, wall gaps, own visibility, spacing, and path connectivity after conservative shop footprints are added.

Live rendering/multiplayer test remains pending. A prior computer-use inspection found an ongoing Warcraft III match; it was not ended to load this map. Do not report mock tests as in-game verification.
