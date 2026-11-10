# Solo Foots 8P FFA + King v12

Installed map: `C:\Users\User\OneDrive\Documents\Warcraft III\Maps\Foots FFA\Solo_Foots_8P_FFA_v12.w3x`

SHA256: `94f3c5c402f7365a6074b64bf0f7516889c5129698e621140c33449f9a29d154`

Fixes the shop-page audit findings from v11. Previously both first pages contained 11 purchases plus a Next unit, in addition to the neutral shop's Select Buyer control. Next also explicitly used Select Buyer's (3,2) position. The new cards have at most ten purchases, Next at (2,2), and Select Buyer at (3,2). Both ordinary and skin object tables agree on icon positions, labels and art. Page controls have explicit zero initial delay, zero cost/food/requirements, and one-second stock replenishment as a fallback.

All 21 creeps remain available in three forward-cycling pages (10/10/1). All 17 recipes remain in two pages (10/7). Shops initialize before the mode-choice dialog, rather than only after it. Page refresh is deferred until the sale transaction completes, then reselects the same physical shop. Timer state is isolated per shop. Navigation tokens bypass the creep cap/bounty trigger. The old pub-mode stock injection is disabled because its turtle and troll are already in the page pool.

Warcraft's default neutral marketplace removal trigger is filtered only for recipe shops, so their purchased recipes can replenish normally. Other shops retain their existing cleanup behavior. Recipe and creep prices, balance, initial stock delays and replenishment intervals are otherwise unchanged. Neutral shops still require a buyer within their normal interaction range; navigation does not authorize remote purchases.

Build: `build.py`. Runtime and synchronized editor JASS compile successfully; all 1,298 archive entries round-trip. `verify_pages.py` audits merged object/skin command cards and runs packaged JASS with mocks for post-event stock consumption, all 16 physical paged vendors, repeated cycles/wrap, independent pending shops, pub-mode injection, default cleanup isolation, and normal purchases. `verify_ui.py` runs zoom/stats and King-mode regression checks, including all 56 directed capture/defect pairs. Terrain, placements, models, UI assets and King logic are unchanged from v11.

Live rendering and multiplayer testing remain pending. Warcraft was observed running an existing match and was not ended. A fresh match using v12 is required; an already loaded map cannot receive these edits.

Engine behavior references used in the audit: [firsthand command-card capacity test](https://www.hiveworkshop.com/threads/ordering-a-shop-to-cast-select-hero.297645/) and [neutral marketplace cleanup investigation](https://www.hiveworkshop.com/threads/about-natives-additemtostock-additemtoallstock-addunittostock-addunittoallstock.251815/). The cleanup implementation was also confirmed directly in the local Blizzard.j toolchain file.
