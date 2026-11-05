# Final Spark — Lux laser spell, v70

Built on the verified combined v68 map (completed Veigar and Pub XP changes).

Open `release/FF799X_Rx_Lux_FinalSpark_v70.w3x`. In Debug mode or a solo game, type **-lux**, select the extra Sorceress-model Lux caster, then press **V** and click a direction. The faint amber line brightens during a one-second charge, then instantly flares into a wide beam with a white core, gold body, orange bloom, a source flash, and a short fading afterglow. Original positional charge and blast sounds are included. The line provides temporary vision and follows terrain heights in eight joined sections.

**-lux2** and **-lux3** switch the same test caster to rank 2 or 3. Repeating a command refreshes mana/cooldown after the current charge, or revives a dead test caster. The temporary hero is outside the draft and tavern roster. Normal multiplayer requires Debug to use these testing commands.

| Property | Value |
| --- | --- |
| Spell / test hero IDs | ALxR / HLx1 |
| Charge | 1 second; direction and origin locked on cast |
| Range / damage width | 3400 / 200 Warcraft units |
| Damage | 400 / 650 / 900 + 1.0 × Intelligence, magic |
| Mana | 100 / 150 / 200 |
| Cooldown | 70 / 60 / 50 seconds |
| Damage timing | Once at the end of the charge, along the whole line |
| Targets | Enemy ground and air units; excludes buildings, invulnerable, magic-immune and Locust units |

Damage, Intelligence, owner, direction and origin snapshot at cast. Enemies can dodge the warning. The laser pierces all units and does not collide with terrain. Its finite rectangle stops at the playable map boundary. The caster cannot act during the charge; death, removal or ownership transfer before firing cancels it and releases its lock. Existing unrelated stuns retain their own locks. Mana/cooldown remain spent on a cancelled cast. After firing, caster death does not erase the afterglow. Balance values adapt the spell to this map; they are not claimed to be League of Legends tuning.

For permanent integration, give **ALxR** to the intended hero through `uabi` (or `UnitAddAbility`) and set its rank. The spell handler is independent of the test hero's unit ID. It currently uses V and the Channel base order `channel`; reserve that order on the recipient hero. `globals.j` and `spell.j` are synchronized into the map's editor WCT source, so a World Editor save preserves the spell. The original roster and prior heroes are retained.

Validation: runtime pjass, editor JassHelper plus pjass, 73 executable checks against the actual translated JASS, 2,000 randomized geometry cases, 100 consecutive casts with strict resource cleanup checks, model/texture round trips, object-record preservation, and full archive payload comparison. **No Warcraft engine visual, native targeting, multiplayer or balance playtest has been performed.** The included preview is an offline rendering of the generated assets and actual spell visual state, not a game capture.

Rebuild in order with the project's bundled runtimes: `prepare.py`, `assets.cjs`, `checks.py`, `compile.py`, `pack.py`. The existing 32-bit JASS compiler requires execution outside the sandbox on this machine. All build outputs stay in this folder. This build is not installed or deployed.

Reference behavior: Riot's Lux page describes gathering energy then firing a beam through all targets: https://www.leagueoflegends.com/en-us/champions/lux/ . The requested classic faint-line-to-wide-blast presentation is the visual target.
