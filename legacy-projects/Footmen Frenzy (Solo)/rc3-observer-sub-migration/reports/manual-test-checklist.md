# Manual Multiplayer Test Checklist — rc3 Observer Substitution

**Map:** `Reforged_Footmen_Frenzy_v7.9.9W-rc3-observer-sub-test.w3x` (also copied into `…\Warcraft III\Maps\799b\`).

This system **must** be tested in a controlled multiplayer game (LAN/lobby) with real observer slots filled. Shared advanced control, fog-modifier vision, resource spending, and leave-event ordering behave differently at runtime than in static analysis. Recommended lobby: fill several gameplay slots (ids 0–11) and at least 2–3 observer slots (ids 12–23, team 4). A "leave" = actually disconnect/quit that client (not defeat), unless the step says votekick.

Legend: **Setup → Action → Expected**. Record PASS/FAIL + notes per row.

| # | Scenario | Steps | Expected result |
|---|---|---|---|
| 1 | 12 players, no leavers | Start a full game; play a few minutes. | No `-sub` prompts. KOTH income, multiboard, victory/defeat all behave exactly as stock rc3. `-sub` from anyone → "There is no lost teammate you can currently choose a substitute for." |
| 2 | One player leaves; position offered | Player on team A leaves. | All players see "<name> was lost. An active teammate may type -sub…". The slot's base/units remain; team A is **not** eliminated; A's teammates are not given a Destroyer. An **active teammate** types `-sub` → observer-selection dialog appears listing available observers. |
| 3 | Observer accepts | From #2, teammate picks an observer; that observer clicks **Yes**. | Global "<observer> has entered the game for <name>." Observer message about full control. Observer is now on team A's colour/team, controls the left player's units/hero/production, can spend that slot's gold. |
| 4 | Observer declines | From #2, observer clicks **No**. | Selector told "<observer> declined…"; observer told "You declined…". Flow ends; another `-sub` can be started; slot remains pending. |
| 5 | Observer times out | From #2, invited observer does nothing for 30 s. | Both selector and observer told the request expired; dialogs close; slot remains pending; a new `-sub` works. |
| 6 | Requester leaves while choosing | Selector opens the dialog, then leaves before picking. | Flow resets cleanly (no stuck dialog for anyone). The **requester** also becomes pending and is announced for `-sub`. Another teammate can `-sub`. |
| 7 | Invited observer leaves while deciding | Selector invites observer X; X leaves before answering. | Selector told "<X> left before answering…"; flow resets; no gameplay-position cleanup runs for X (X was an observer). |
| 8 | Substitute commands & spends | After #3, the substitute issues unit orders, trains units, casts the hero, and spends gold/lumber of the inherited slot. | All orders work through shared advanced control; resources deplete from the inherited slot; produced units belong to the canonical slot. **Watch specifically for any command that silently no-ops** (report it — advanced control coverage is the top runtime risk). |
| 9 | No enemy/full-map vision | After #3, check the substitute's minimap/fog over **enemy** areas not seen by team A. | Substitute sees only what team A sees (allied shared vision + own units). Enemy bases outside allied sight are fogged. **If the substitute still sees the whole map, the vision teardown failed — report immediately.** |
| 10 | Allied vision present | After #3, an allied teammate reveals an area. | Substitute sees allied-shared vision normally (shared vision with team A is granted). |
| 11 | Substitute leaves → cleanup once | After #3, the substitute observer disconnects. | The inherited canonical slot runs rc3's normal leaver cleanup **exactly once** (elimination or ally-Destroyer per rc3 rules, "has left the game.." message, multiboard refresh). No double cleanup, no residual pending. |
| 12 | Inherited base destroyed → observer freed | After #3, enemies destroy the inherited base. | rc3's normal destruction/elimination runs for the canonical slot; the substitute is released: returned to team 4, original name/colour, full-map observer vision restored, free camera, alliances restored. Message: "The inherited position was eliminated…". |
| 13 | Unassigned observer leaves | An observer who is **not** substituting disconnects. | No gameplay-position cleanup; no pending mark; no "has left the game.." for a gameplay slot; teams/victory unaffected. |
| 14 | Votekick unchanged | Team votekicks one of its own active players (2 yes votes). | Exactly stock rc3 votekick: target defeated/removed, "…decided to kick…RIP", team-defeat logic proceeds. The kicked slot is **not** marked pending / **not** offered for `-sub`. |
| 15 | KOTH size & income during sub | Have a team hold the hill; one member leaves and is subbed; keep holding. | KOTH team size counts the subbed slot as **one** player (not zero, not two). Gold-per-player division and the 2-player division bonus match a same-size team with no substitution. Before-leave, during-pending, and after-sub all give the correct per-player income. |
| 16 | Victory/defeat correct | Run a game to completion with at least one active substitution in play. | Correct team wins/loses; a preserved (pending) position keeps its team alive (does not falsely eliminate); a substitute's team can still be defeated normally; `END` fires correctly. |
| 17 | Two pending positions | Two players (same or different teams) leave. | Both announced. `-sub` from a teammate offers the **lowest-numbered** pending slot that teammate is allied to. After filling one, `-sub` again offers the next eligible one. |
| 18 | No observers available | All observers gone/none present; a player leaves; teammate types `-sub`. | "There are no available observers to invite." Slot stays pending; no dialog. |
| 19 | Match ends with dialog open | Open a `-sub` selection/confirmation, then let the match end (base race). | Game ends normally; no crash/hang; leftover dialog/timer have no gameplay effect. |
| 20 | Released observer has no lingering control | After #12, the freed observer tries to command the (now dead) inherited units and check vision. | No shared/advanced control remains over the eliminated slot; no enemy vision; observer behaves as a normal observer (can use `-cam`). |

## Extra runtime watch-items (report if seen)
* **Desync**: all state changes use synchronous natives (team/colour/name/alliance/dialog) or per-player camera natives; no `GetLocalPlayer()` branch was added. Still, watch for desync around substitution and camera.
* **Shared advanced control edge cases**: shops, custom `-commands` keyed off `GetTriggerPlayer()`, hero-ability UI, item pipeline — a substitute acts through the observer's player handle, so any system that keys strictly off the *canonical* id may not see the substitute. Note anything that misbehaves.
* **Repeated `-sub` spam** during a live flow should always answer "already being decided."
* **Multiboard**: confirm the leaver/substitute rows render sanely.
