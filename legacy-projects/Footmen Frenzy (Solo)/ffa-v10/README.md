# Solo Foots 8P FFA + King v10

Installed map: `C:\Users\User\OneDrive\Documents\Warcraft III\Maps\Foots FFA\Solo_Foots_8P_FFA_v10.w3x`

SHA256: `4cc6606c5f908e81aa92bad8eec0a3a3b5c05b54050aabb12948bf07bebcc787`

At startup, the first active human in the eight-slot roster receives Normal FFA / King Mode choices. Normal FFA is the 20-second timeout default; missing Red falls back to the next active human. Game/mass clocks restart after selection. Hero tavern selection follows the mode choice.

King mode retains the previous conquest rules: killing an enemy main base captures that player for the attacker's sovereign; taking a sovereign takes their whole kingdom. Vassals remain active and keep their own units, resources and upgrades. Bases rebuild after three one-second ticks at their captured tier, maximum health/mana and position, with production/autosend preferences and Overdrive research/cooldown restored. Rebuilt bases receive eight seconds of protection. Each player may use `-defect` once while captured, becoming independent with ten seconds of protection (rebuild protection may extend it if the base is still rebuilding). `-king` reports kingdom status. The kingdom wins after holding all active players for 20 seconds; defection cancels that countdown. Departed kings have a live successor.

Kingdoms share alliances, experience and vision, but not direct unit control. The scoreboard shows all eight players, their king, kingdom kill/capture totals, defection status and hill gold; `-kd` retains personal K/D. King of the Hill income follows the current kingdom, dividing the entire payout across its active members and assigning the remainder to its king. Captures/succession carry kingdom historical totals. Normal FFA retains its separate rules and board.

Eliminated FFA players receive full-map vision immediately. A hero death or becoming a vassal does not eliminate a player and does not grant full-map vision. Existing observers retain full vision. Captured vassals retain kingdom vision; defection revokes former kingdom vision.

Build: `build.py` imports the earlier `solo-latest-test05` SK implementation and integrates it with the v9 roster, startup, scoring, base-death, departure, hill, and editor-runtime pipeline. `integration.j` contains roster adapters, restored base controls, hill payouts, mode UI and eliminated-player vision. V9 terrain, placements, pathing, unit/ability data, minimaps and other assets remain byte-identical.

Verification: runtime and editor JASS compile; all seven object tables parse; 1,295 archive entries round-trip; installed file hash matches. `verify_king.py` executes the packaged JASS with stateful native mocks: 56 directed capture/defection pairs, base rebuild/state preservation, whole-kingdom transfers, all eight sovereign victory/cancellation cases, king succession and departed vassals, sizes 1-8 hill payout conservation, shared vision/control invariants, personal and kingdom scoring, sparse lobbies, randomized transitions, host-only/idempotent startup selection, and full-map vision for all eight eliminated-player slots.

Live testing: Warcraft III was inspected using the computer-use skill, but an existing match was running. The match was left intact. V10 menu rendering, real-engine captures/defection, and multiplayer synchronization remain unverified; do not describe the mock simulation as an in-game playtest.
