# Mundo health-kit test build

Standalone test map based on combined v68; it does not include the parallel Lux work. The user-facing activation key for Poison Gas is X; W is the learn key. Click X again to switch it off. The established spell resistance, cloud duration, poison linger and 12/16/20/24/28/32 HP per second are retained. Existing cloud damage was implemented in v64 but had not been live-tested; this revision adds the first hit on first scan and separates cloud scheduling from the cleaver state.

Mundo's base INT, INT growth, initial/max mana and mana regeneration are zero. Hidden AMi0-AMi9 and AMj0-AMj9 stat offsets cancel acquired INT; a quarter-second update recomputes them and forces max/current mana to zero, including mana granted by items. No new visible passive icon is created. Native Warcraft behavior for zero base INT, negative stat offsets, item interactions and a zero maximum mana bar must be tested in game.

Runtime pjass and editor jasshelper/pjass passed. 18 checks execute translated shipped JASS under mocked natives, including target filters, initial damage, poison ticking, overlapping scans, toggle, health drain, survival shutoff, cleaver state, and multiple INT bonuses/removal. The map was not launched in Warcraft.

Integration: `prepare.py` is based on the v68 release and contains the changes in one place. Rebase its patch onto the current combined map, preserving unrelated script functions and WCT editor chunks; add the 20 new ability records, modify only HMu1's resource fields, and append the maintenance note. Do not overwrite other agents' complete map files with this test map.
