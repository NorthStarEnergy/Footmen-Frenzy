# FF799X Casino v1.2 — test map

Open `release/FF799X_v42_Casino_v1_2_TEST_ONLY.w3x` in Warcraft III. The lobby name is **FF799X - Casino v1.2 TEST ONLY**. Use an ordinary human player slot or one of the map's custom observer slots; no computer lobby slot is needed for blackjack bots. Native observer/referee input is outside this prototype's supported setup.

Click **Casino** at the right edge, or type **-blackjack**, **-bets**, or **-challenges**. Blackjack uses the same green felt, large card faces, card backs, chip artwork and native buttons as Observer Poker v2. Betting, challenges and rules use a plain navy panel. Text and controls have wider horizontal margins. Poker remains accessible for custom observers through its tab and `-poker`; that inherited poker game still uses practice chips.

## Blackjack

The v1.2 presentation uses shorter labels and a packaged Liberation Sans Bold font. Buttons share explicit color semantics across poker and the casino: Fold/decrease/decline/cancel are red; Raise/increase/double/bet/accept are green; Check/Stand are grey; Call/Hit are light green. Check becomes Call when money is owed, and its fill changes with the action. Blue denotes switching/actions and gold denotes the current selection. Disabled controls are muted. Font copyright and the SIL Open Font License are shipped in `art/CasinoUI/FONT-LICENSE.txt` and inside the map.

- Every player starts with an independent solo table against the dealer and two scripted bots. **Join community** seats you at the shared six-human table. You can switch tables after your wager has settled, or while you have no wager in the current round.
- Choose gold using **-10**, **+10**, **+50**, **2x**, **Half**, or type **-stake 250**. Stakes are even amounts from 10 through 10,000, limited by available account gold and remaining house backing. Click **Place wager** to commit. There is no automatic repeat betting.
- Solo dealing starts after three seconds. The community table accepts wagers for twelve seconds from its first wager; unfunded seats sit out that round. Everyone at a table shares one dealer and one two-deck shoe.
- Hit, stand, double on an initial two-card hand, or split matching values once. Split aces receive one additional card each and stand; split 21 pays the ordinary 1:1 rate. No resplitting, insurance or surrender. Dealer peeks for a natural and stands on all 17, including soft 17. Blackjack returns 2.5 times the stake, other wins return twice the stake, and pushes return the stake.
- Turns allow twenty seconds; timeout or disconnection stands. Bots act from their own hand total and stand at 17. The dealer hole card stays face down until reveal. Other players' totals are visible in the seat list. Large hands show their first six cards with an explicit notice; their total includes every card.
- Each table has its own shuffled 104-card shoe, containing exactly two copies of each card. The cut is conservative for a full six-seat table: shuffle between rounds when more than 26 cards have been consumed. No live card is recycled. If a shoe is exhausted unexpectedly, the entire round is void and wagers are returned.

## Match betting

Five tabs support **first hero kill**, **scores a base kill**, **first base lost**, **first to level 16**, and **team to win**. In the map's single-block player-winner mode, the last tab uses individual player outcomes instead of team outcomes.

All five markets close at elapsed map time **2:10**, with a **2:00** last-call announcement. If a first-event outcome happens earlier, that market immediately closes and settles. There is no Colossus-spawn rule.

Rows show money placed, its percentage of that market's betting volume, a distribution bar and current decimal odds. Select a row to preview the quote **including your proposed wager's impact** and its total payout. The quote on an accepted ticket is fixed. The displayed total return includes the original stake. A player's selected hero supplies the opening prior for first hero kill: names containing Shadow or Cattle receive three times the neutral opening weight. Thereafter prices respond to hero picks and money placed, rather than base health or a late-game outcome signal.

**Scores a base kill** is a separate yes proposition for each player: every backed player who destroys an enemy base can win. It is not restricted to the first base kill. Unsuccessful selections lose at match end. First-event markets with no qualifying event and winner markets without a definitive result are void and refund their stakes. Hero kills exclude illusions and allied kills. Base destruction and final victory use the map's existing destruction and canonical account-settlement hooks.

Odds are capped at 20.00x and use virtual opening weights so the first bet has a defined price. A separate 1,000,000-gold casino bank reserves the maximum profit for every accepted house wager, including blackjack. If backing is insufficient, the wager is declined before any player gold moves. Match tickets are capped at 4,095 per match; payout work runs in batches of 64 to avoid one very large settlement trigger. Market data is cached for UI updates.

## Player challenges

Challenges can be proposed at any time before the match result, including after 2:10. Select an opponent and a team/player to win. The proposer backs that winner; the recipient explicitly agrees to back that outcome **not winning**, at the same stake. Both stakes form the pot. The recipient sees the target, amount, pot and thirty-second offer expiry before clicking **Accept challenge**.

Offers hold the proposer's stake; decline, cancellation or expiry returns it. Acceptance holds the opponent's stake as well. One accepted challenge per player at a time. Definitive results transfer the pot; a drawn or incompatible result returns both stakes. Challenges use no house funds.

## Account gold and limitations

The wallet uses the supplied map's `FGA_gold`, `FGA_ready`, debt and local-save implementation. It never spends Warcraft battlefield resource gold. Wagers are removed immediately into casino escrow. Returned principal bypasses debt repayment; only profits go through `FGA_Award`. Credit that cannot fit under the profile's balance cap remains pending in the running match rather than being discarded.

This retains the supplied **experimental player-local profile**. It is not authoritative, tamper-proof, crash-safe or transactionally recoverable across computers. A disconnected player's client cannot save later payouts. Casino escrow and tickets live in the current match, so a crash or quit can leave saved stakes lost. Use this as a gameplay test, not a dependable persistent economy. Shuffling is synchronized casual-game state and is not secret against modified clients.

## Verification and sources

`rule-tests.json` records execution of the actual JASS functions through a Python translator with JASS division semantics: 600 random blackjack rounds, another 100 rounds carrying shoes forward, soft aces, natural/push payouts, splitting, doubling, shared turn ownership, exhaustion refunds, gold conservation, debt handling, fixed odds and movement, the exact cutoff, base outcomes, FFA/draw outcomes, challenge acceptance/expiry, and a full 4,095-ticket settlement. Mocked native frame calls check that renderers preserve gameplay state, foreign panels remain hidden and dealer hole cards remain face down.

`verification.json` records full-map pjass compilation, round-trip verification of 73 payloads, preservation of 1,335 unrelated archive entries, and exact restoration of the input battle script after removing the casino additions and its three integration points. The original input map is not modified. `blackjack-preview.png`, `betting-preview.png`, `challenges-preview.png`, and `rules-preview.png` are offline compositions from the actual frame coordinates and shipped textures; native Warcraft text/button rendering can differ. **No Warcraft engine or multiplayer desync playtest has been performed.**

Source modules are `wallet.j`, `blackjack.j`, `markets.j`, `duels.j`, `ui.j`, `start.j`, and `casino-globals.j`. The build reads the original map from `C:/Users/User/Downloads/FF799X_v42_account_gold_TEST_ONLY.w3x` and the existing Observer Poker v2 module/artwork. Run `test_casino.py` and `build.py` with the bundled Python runtime. The existing 32-bit pjass executable requires execution outside the current Windows sandbox. `preview.py` produces the offline layout images. The generated authoritative runtime script is `src/war3map.j`; saving this map in World Editor can replace script changes because inherited trigger source is not synchronized.

First live checks: open alone in an ordinary slot, wait for account loading, open Casino, wager 50 gold, verify debit/settlement and reopen the profile. Exercise hit/stand/double/split and switching to/from the community table. Then host two human clients: share a community round, verify turn ownership and the dealer hole card on both clients, place bets on opposite outcomes, watch the 2:00/2:10 cutoff, resolve each game event, accept a challenge, and confirm balances save without desync.
