# Solo Foots 8 Player FFA v4

Built from the BLP1 minimap repair of Compact FFA v3. The original eight-player terrain, pathing, minimap pixels, hero pools, timing, and combat systems are preserved.

- One physical recipe shop per base. Next page switches its stock between the original eleven and six recipes. The tiny second-page building is removed.
- All 84 off-center shop placements face the map center, in both gameplay creation and editor placement data. Hero taverns also face inward.
- Eight active-player base taverns replace the SD/AP/AR ground selectors. The existing 24-choice hero pool uses one Next page button, cycling through 10, 10, and 4 heroes and back to the start.
- Normal public/KOTH setup starts automatically after initialization. The old host mode dialog and AFK setup are disabled.
- Startup and both game-start camera branches center each local player's view on their actual main building.

Output: `release/Solo_Foots_8P_FFA_v4.w3x`.

## Verification

`build.py` compiles gameplay JASS, preprocesses and compiles the synchronized editor wrapper, validates object-table boundaries, and verifies all 1,214 archive payloads after packing. Only `war3map.j`, `war3map.wct`, `war3map.w3u`, `war3mapUnits.doo`, and the lobby title in `war3map.w3i` change. The two BLP1 minimaps are preserved.

`verify_behavior.py` executes the edited JASS control flow with mocked Warcraft natives. It verifies eight taverns, no selector creation, all hero pages and wraparound for every player, recipe paging, and camera isolation and main-building targeting for all eight players. This does not replace in-game verification.

Use the local Python runtime at `C:/Users/User/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe` to run `build.py` and then `verify_behavior.py`. The build uses the existing StormLib archive helper in the neighboring Footmen Frenzy project's `six-player-ffa` directory and local Warcraft JASS API definitions under `Documents/Codex/2026-10-28/thi/work`. The legacy compiler may require execution outside the desktop sandbox.

Live Warcraft III testing remains pending.
