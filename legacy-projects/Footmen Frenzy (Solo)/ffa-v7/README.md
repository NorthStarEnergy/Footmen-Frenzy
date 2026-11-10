# Eight-player FFA v7

Source: the v6 eight-player map. Output: `release/Solo_Foots_8P_FFA_v7.w3x`.

The inner layout is compressed radially while the outer walls stay fixed. Cliff tips are trimmed to a minimum radius of 2,220. Grass extends toward base entrances with a gently irregular boundary. Each tower moves 64 units sideways, retaining its forward position. Each main/start location moves 96 units toward its rear wall. Center weapon and armor shops follow the compacted layout and are seated on ground with 64-unit cardinal pathing clearance. Doodads, pathing, shadows, placement records and gameplay creation coordinates are updated together. Terrain-derived minimaps use BLP1.

The hero tavern uses explicit Spirit Lodge artwork in both unit and skin tables, matching the visible recipe-shop model, with a neutral-market parent and building flag. Page one contains ten different SD categories; the remaining choices are random without replacement. The complete Gragus and Orianna systems and dependencies are ported from the polished six-player v3 map, together with that migration's Guardian/lantern dependencies. Their roster entries are 93 and 92, respectively. The existing Next-page cycle remains.

`build.py` builds the map, compiles both runtime and synchronized editor source, parses object data and verifies archive readback. `verify_layout.py` checks connectivity for all eight bases, 16 towers, five center shops and 688 footman positions, verifies grass under towers, roster/category availability, tavern model settings and BLP1 minimaps. `layout-preview.png` is a terrain-data schematic; yellow marks mains, red towers and cyan center weapon/armor shops. It is not an in-game screenshot.

Both scripts use the bundled Python runtime and existing StormLib/JASS tooling referenced in the build. Live visual and gameplay verification remains pending. The script/compiler checks cannot establish that tavern art renders correctly in the running client.
