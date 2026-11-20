# FF799X — Observer Poker v2

Separate prototype based on the released **FF799X - Orianna v4** 12-player map. Does not modify the original release or the concurrent v5 source work.

## Start playing

In Warcraft III, open Custom Games → Test → **FF799X - Observer Poker v2**. V1 remains available separately.
Start with yourself as the only human, in any normal or custom observer slot. No computer lobby slot is required. The prototype automatically gives you observer-team membership, reveals and pauses the battlefield, and opens your table against the scripted Computer after two seconds. The normal Footmen runtime is deliberately skipped in this one-human practice mode; this is a poker test, not a solo Footmen battle.

With two or more humans, the ordinary Footmen runtime runs. Humans in the map's custom observer team automatically receive independent computer-opponent tables. Active combat players receive no poker panel. Use the map's custom observer slots, not Warcraft's native observer/referee role. Native observer input is not supported or verified by this prototype. Defeated-player admission and human-versus-human seating are not implemented yet.

Click Fold, Check/Call, Raise, or All-in. Raise uses the minimum legal raise; All-in is capped at the effective stack. Click Next hand after settlement. Hide keeps the hand running; type **-poker** to reopen. A 30-second timeout checks when free, otherwise folds. The bot acts after two seconds.

Both seats start at 500 play chips; blinds are 5/10, dealer rotates, and stacks carry between hands. If a stack reaches zero, Next hand explicitly resets both to 500 for continued practice. No Warcraft gold, lumber, units, rewards or persistent currency are used for poker. Each observer has a separate table. Heads-up all-ins cap commitments to the smaller stack, so there is no multiway side-pot engine.

V2 replaces the text-only panel with a green felt table, 52 original large white card faces, red hearts/diamonds, dark clubs/spades, patterned card backs, community-card placeholders and a dealer marker. Chip piles change with stack/pot size; adjacent numbers are the exact amounts (pile graphics are indicators, not denomination accounting). A turn countdown, amount to call and action buttons remain visible. Computer cards remain hidden until showdown; folded hands stay hidden. The bot uses only its own cards and the exposed board, with a simple heuristic and occasional bluffs. Shuffling uses an isolated deterministic RNG with a fixed reproducible test seed. This is casual practice, not secure hidden information against modified clients.

`ui-preview.png` is an offline layout preview using the shipped card/chip textures and runtime positions, not an in-game screenshot. Warcraft supplies its own button and text rendering. `deck-preview.png` shows all 52 packaged card faces.

## Verification

- Actual JASS rule functions executed via a Python translation with integer division: all nine ranking classes, 1,000 independent seven-card comparisons, 1,000 simulated hands, plus short blinds, all-in caps, reopening rules, isolation, duplicate actions and bot hidden-card independence.
- Full script passes pjass. Runtime source restores exactly to its baseline after removing the added module/globals and startup hook.
- 144 mocked card-display checks verify private opponent cards and unrevealed community cards stay hidden, table visibility is local, and UI updates leave the poker state unchanged.
- All 60 BLP1 textures include mipmaps and a separately verified alpha plane. All card faces and the offline table composition were visually inspected.
- Re-extracted payloads match; all 1,314 unrelated archive entries are preserved. The import manifest additionally registers the 60 textures.
- **Warcraft engine visuals, startup and multiplayer desync testing remain pending.** These checks are not a live playtest.

Build with the bundled Python running `build.py`. It generates artwork with `make_art.py`, runs rules and UI checks through `test_ui.py`, compiles, packages with the existing .NET MPQ tool and verifies the archive. `poker.j` holds the original rules; `ui.j` supplies the v2 renderer and startup layout inserted during the build. The local 32-bit pjass compiler requires execution outside the current Windows sandbox. `Install.ps1` copies only this separately named v2 prototype into both Warcraft Test folders and verifies hashes.

The authoritative script is `src/war3map.j`. Inherited World Editor trigger source is not synchronized; saving in World Editor may replace runtime changes. Preserve the builder/module when editing.

First live checks: launch alone from a normal slot; see automatic table; check/call through a showdown; fold; raise/all-in; reload after bust; hide/reopen and timeout. Then host with an active player and custom observer, verify private panels, bot actions, no desync and uninterrupted battle. With two custom observers, verify independent stacks and tables.
