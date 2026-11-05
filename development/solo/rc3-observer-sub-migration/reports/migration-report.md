# rc3 Observer-Substitution Migration Report

**Target map:** `Reforged_Footmen_Frenzy_v7.9.9W-rc3.w3x` (full 12-player rc3)
**Baseline script:** extracted `war3map.j`, SHA256 `cdef1d67…d81b7d8` (53,277 lines)
**Modified script:** `work/war3map.j`, SHA256 `8e110b82…cb680541` (+23 functions, net +576 lines)
**Reference:** Solo Foots commit `3b37c26` "Add observer substitution workflow" (`git diff 127e93d 3b37c26 -- src/war3map.j`)
**Date:** 2026-07-25

The Solo commit was **not** applied mechanically. It targets a 4-slot Solo build and references systems that do not exist in rc3 (`SoloCam_*`, `SoloFootsDisplayMessage*`) and a 4-ID leave registration. Everything below is the rc3-native adaptation.

---

## 1. Verified rc3 facts (before designing)

| Fact | Evidence in baseline |
|---|---|
| Gameplay slots are player ids **0–11**, four teams of three (engine teams 0–3) | `main()` `SetPlayerTeam(Player(0..11), 0..3)` — lines 51436–51512 |
| Observers are ids **12–23**, all on **engine team 4** | `main()` `SetPlayerTeam(Player(12..23), 4)` — lines 51532–51543 |
| rc3 registers leave events for **all** ids 0–11 (not 0/4/7/11) | `InitTrig_player_leaves` — lines 49602–49613 |
| Leave cleanup **recomputes** the acting player from `GetTriggerPlayer()` | `Trig_player_leaves_Actions` line 49532 |
| Votekick fires the leave trigger via **`TriggerExecute`** (so `GetTriggerPlayer()` is invalid there) and redirects via `udg_Votekick_Target_Player` | `Trig_Votekick_Vote_Yes_or_No_Actions` line 24325; `Trig_player_leaves_Func001C` line 49439 |
| Observer full-map vision is a **script-created fog modifier** per team-4 player, handle never stored | `Trig_Observer_Vision_Fix_Func001A` line 16028 |
| rc3 already ships a spectator camera (`FF_oc_*`) gated on **team == 4** | `FF_oc_CanObserve` line 52417 |
| Victory/defeat keys off `udg_player_active[]` / `udg_leave_or_votekick[]`, **not** slot state | `Trig_check_if_team_active_*` lines 49118–49328 |
| KOTH income counts team members by **slot state == PLAYING** | `Trig_KOTH_Income_Func006Func001C` line 17466 |
| `ConvertedPlayer(n)` = `Player(n-1)`; `udg_player_active` is 1-based (index 1..12) | leave/destroyed cleanup throughout |
| Team forces `udg_team[1..4]` contain only canonical players 0–11 | lines 14022–14042 |

The observer IDs **were confirmed to be 12–23** (task assumption verified against `main()`), so the reference's 12–23 scan range is correct for rc3.

---

## 2. Integration points (every edit)

All edits were spliced by unique text anchor (never by line index) because `war3map.j` has mixed line endings (the appended `FF_*` block uses bare LF; the generated body uses CRLF). There is exactly one real `globals` block (column-0 `globals`/`endglobals`, balanced 1/1), but the substring `endglobals` appears on 11 lines (10 are vestigial `//endglobals from <lib>` comment markers), so a naïve `endglobals` anchor is ambiguous — the R1 anchor uses the preceding unique line. The splice script asserts each anchor occurs exactly once. Baseline byte-hash was re-verified immediately before writing.

| # | Location (baseline line) | Change | Requirement |
|---|---|---|---|
| R1 | globals block, before `endglobals` (2860) | Added the `SoloSub_*` global state (mappings, pending flags, dialog/timer/button handles, alliance snapshot arrays, fog-modifier array, saved colour/name) | state model |
| R2 | before `// Trigger: KOTH Income` (17462) | Inserted the entire 23-function `SoloSub` system | whole system |
| R3 | `Trig_player_leaves_Actions` top (49528) | Inserted `if SoloSub_LeavePrelude() then return endif`; changed the non-votekick branch to `udg_temp_player = SoloSub_EffectiveLeaver()` | #1,#2,#8,#12, leave interception |
| R4 | `InitTrig_player_leaves` (49613) | Added leave-event registration for observers 12–23 on the **same** `gg_trg_player_leaves` trigger | #12, validation #5 |
| R5a | `Trig_KOTH_Income_Func006Func001C` (17466) | `slotState==PLAYING` → `SoloSub_IsEffectivePlayer` | #7, KOTH income |
| R5b | `Trig_player_leaves_Func009Func003Func001C` (49446) | same predicate swap (hill-reset-on-leave) | #7, KOTH size |
| R5c | `Trig_player_destroyed_Func013Func003Func001C` (49664) | same predicate swap (hill-reset-on-destroy) | #7, KOTH size |
| R6 | `Trig_Observer_Vision_Fix_Func001A` (16031) | Record each observer's fog-modifier handle into `SoloSub_observerFog[]` | observer vision |
| R7 | `Trig_player_destroyed_Actions` top (49779) | Inserted `call SoloSub_OnPositionDestroyed(...)` | #9 |
| R8 | `InitCustomTriggers` (50659) | Added `call InitTrig_SoloSub()` (once) after `InitTrig_Observer_Vision_Fix()` | init, validation #6 |

---

## 3. rc3-specific adaptations vs the Solo reference

### 3.1 Leave interception (the biggest structural difference)
Solo's `SoloSub_InterceptLeave` set `udg_temp_player` and returned `false` to let cleanup continue. **That cannot work in rc3** because `Trig_player_leaves_Actions` immediately *overwrites* `udg_temp_player` from `GetTriggerPlayer()`. The rc3 design therefore splits into two calls at the top of the *existing* combined action (deterministic ordering, no second trigger):

* `SoloSub_LeavePrelude()` → returns `true` to **suppress** all destructive cleanup, `false` to continue.
* `SoloSub_EffectiveLeaver()` → supplies the player the cleanup should act on (the inherited canonical slot for a substitute leave; otherwise `GetTriggerPlayer()`), stashed via `SoloSub_leaveInheritNumber`.

Decision matrix inside `LeavePrelude`:

| Leave kind | Action | Return |
|---|---|---|
| **Votekick** (`udg_Votekick_Defeat_Kicked_Player`) | do nothing (checked *first*, before any `GetTriggerPlayer()` — which is invalid under `TriggerExecute`) | `false` → rc3's votekick path runs byte-unchanged |
| **Ordinary gameplay leave, slot still active** | mark `SoloSub_pendingPlayer`, announce `-sub` | `true` (suppress) |
| **Gameplay leave, slot already inactive** (e.g. previously eliminated) | none | `false` (original rc3 behaviour) |
| **Unassigned observer leave** | if it was the invited observer, notify + reset flow | `true` (suppress) |
| **Substitute leave** | sever mapping, stash canonical number | `false` → `EffectiveLeaver` returns the canonical slot, cleanup runs **once** |

The votekick branch text (`Trig_player_leaves_Func001C` → `udg_Votekick_Target_Player`) is preserved **verbatim**, so votekick cannot become a pending substitution (requirement #11).

### 3.2 Messaging
`SoloFootsDisplayMessageToPlayer/ToForce` do not exist in rc3. Replaced with two thin wrappers over natives rc3 already uses:
* `SoloSub_MsgPlayer` → `DisplayTimedTextToPlayer(p, 0, 0, 20, s)`
* `SoloSub_MsgAll` → `DisplayTimedTextToForce(udg_all_players, 20, s)`

`udg_all_players` is a persistent force (`GetPlayersAll()`, set at init). **No temporary force is ever created or leaked.**

### 3.3 Camera integration
`SoloCam_mode` / `SoloCam_followed` do not exist. rc3 has its own spectator director `FF_oc_*`, gated on `GetPlayerTeam(p) == 4`. When a substitute joins the lost player's team, they leave team 4, so the director stops driving their camera automatically. In addition, `TryReplace`/`ReleaseObserver` explicitly clear `FF_oc_mode`/`FF_oc_followed` and call `ResetToGameCameraForPlayer` so the view is freed. This is the rc3-native equivalent of the Solo camera reset.

### 3.4 Observer vision (the review's flagged blocker) — resolved
`Trig_Observer_Vision_Fix` creates a permanent full-map `FOG_OF_WAR_VISIBLE` fog modifier for every team-4 player at 0.10s and discards the handle, so a substitute would keep enemy vision (exactly the review's warning). Fix:
* **R6** records each observer's fog modifier into `SoloSub_observerFog[pid]`.
* `SoloSub_TryReplace` calls `SoloSub_RemoveObserverVision` (destroys that fog modifier) after the team change — the substitute keeps only allied shared vision.
* `SoloSub_ReleaseObserver` calls `SoloSub_GrantObserverVision` to recreate the full-map fog modifier, restoring normal observer sight.

Because rc3 grants observer vision through a **script fog modifier** (not an engine referee/observer slot), it is fully removable at runtime. See Risks for the one residual caveat.

### 3.5 Alliance restoration — snapshot/restore instead of reconstruction
Solo *reconstructs* an assumed observer alliance layout on release. rc3 instead **captures** the observer's real outgoing and incoming state for all 8 alliance flags toward every one of the 24 players (`SoloSub_SnapshotObserverAlliance`) before substitution, and restores it exactly on release (`SoloSub_RestoreObserverAlliance`). All eight flags named in the task are covered:
`ALLIANCE_PASSIVE, HELP_REQUEST, HELP_RESPONSE, SHARED_XP, SHARED_SPELLS, SHARED_VISION, SHARED_CONTROL, SHARED_ADVANCED_CONTROL`.
During substitution the observer's diplomacy is mirrored from the lost player (`SoloSub_MirrorAlliance`, both directions) and the lost↔observer pair is granted shared + shared-advanced control and shared vision.

### 3.6 Effective-player counting
`SoloSub_IsEffectivePlayer(p)` is the rc3 adaptation of Solo's predicate:
* canonical slot (0–11): effective if `PLAYING` **or** pending **or** has a substitute;
* observer (12–23): effective only if it is **not** acting as a substitute and is `PLAYING`.

**Safety property:** for any slot with no pending/substitution state, `IsEffectivePlayer` is exactly equal to `slotState == PLAYING`. Therefore R5a/R5b/R5c are *no-ops in an ordinary game* and only change behaviour when a substitution is live. Victory/defeat (`check_if_team_active`, `END`) needed **no** change because they read `udg_player_active[]`/`udg_leave_or_votekick[]`, which the pending/suppress path keeps correct (a preserved position stays counted as active; a substitute leaving runs normal cleanup that flips those flags). The observer never counts as an extra gameplay participant because no gameplay counter iterates observers — team forces are static (canonical only), and `check_if_team_active` only indexes 1..12.

### 3.7 Governance deviation (intentional)
Solo allows *any* active player (including an enemy) to pick a substitute when the pending position has no active human ally. Per the task's "prefer active teammates / do not silently allow an enemy," this fallback was **removed**: `-sub` only offers positions the requester is allied to (`IsPlayerAlly`). Consequence: a team with no remaining active human teammate cannot be subbed — documented as an accepted limitation rather than handing the choice to an enemy.

---

## 4. Governance & edge-case handling

| Case | Handling |
|---|---|
| Multiple pending positions | `-sub` selects the **lowest-numbered** eligible pending slot the requester is allied to |
| No available observers | `HasObserverOnPage` empty → "There are no available observers to invite." |
| Requester leaves during selection | `LeavePrelude` resets the flow, then marks the requester pending |
| Invited observer leaves before answering | unassigned-observer branch notifies the selector and resets the flow |
| Request timeout | single `SoloSub_responseTimer` (30 s) → `SoloSub_ResponseTimedOut` |
| Position destroyed during selection | `SoloSub_OnPositionDestroyed` cancels the flow if it targets that slot |
| Observer accepts after request invalid | `ConfirmActions` → `TryReplace` re-validates (pending + availability); else "no longer available" |
| Substitute leaves | mapped to canonical, rc3 cleanup runs once |
| Votekicked gameplay player | preserved rc3 path; never becomes pending (checked first) |
| Votekicked substitute | impossible — votekick requires the target slot `== PLAYING` (line 24295); a subbed slot's canonical is not PLAYING, so it can't be targeted |
| Observer already substituting elsewhere | `IsAvailableObserver` excludes `playerForObserver != 0` |
| Repeated `-sub` | `SoloSub_flowActive` guard serialises requests |
| Team with no active human teammate | position cannot be subbed (see 3.7) — accepted limitation |
| Map ends with request open | `END` runs normally; the dialog/timer become irrelevant (no gameplay effect) |

---

## 5. Handles created by the migration (leak review)

* `SoloSub_chooseDialog`, `SoloSub_confirmDialog` — created once in `InitTrig_SoloSub`, live for the game.
* `SoloSub_responseTimer` — created once, paused between flows.
* Three command/dialog triggers in `InitTrig_SoloSub` — live for the game (locals nulled).
* Dialog **buttons** — recreated on each dialog rebuild; JASS exposes no `DestroyButton`, matching rc3's existing votekick dialogs (same pattern, not a new leak class).
* **Fog modifiers** — `RemoveObserverVision`/`GrantObserverVision` destroy the previous handle before creating a new one, so at most one per observer exists at a time (no accumulation).
* No new force, group, rect, location, unit, or effect handle is created. `SoloSub_MsgAll` reuses the persistent `udg_all_players` force.

Local `player`/`button` handle variables are nulled before function exit.

---

## 6. State model (globals added)

```
integer array    SoloSub_observerForPlayer   // canonical 1-based -> observerId+1
integer array    SoloSub_playerForObserver   // observerId -> canonical 1-based
boolean array    SoloSub_pendingPlayer       // canonical 1-based -> awaiting sub
string  array    SoloSub_observerOriginalName
playercolor array SoloSub_savedColor
fogmodifier array SoloSub_observerFog         // per-observer full-map vision handle
boolean array    SoloSub_snapOut / SoloSub_snapIn  // alliance snapshot [obs*192+other*8+flag]
dialog  SoloSub_chooseDialog / SoloSub_confirmDialog
timer   SoloSub_responseTimer
button  array SoloSub_observerButton; button cancel/next/prev/yes/no
player  SoloSub_selector
integer SoloSub_targetPlayerNumber / SoloSub_chosenObserverId / SoloSub_choosePage
boolean SoloSub_flowActive
integer SoloSub_leaveInheritNumber            // set by LeavePrelude, read by EffectiveLeaver
```

Names retained from the reference for traceability; implementations are rc3-native.
