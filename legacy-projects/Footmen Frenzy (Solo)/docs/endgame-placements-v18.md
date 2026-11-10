# End-game winner and runner-up tracking — SF_Test1.7_v18

## Scope

The Solo map has four playable competitors, represented by converted player
numbers `1`, `5`, `8`, and `12`. The legacy script keeps three slots per team,
but only those four representatives are placed in `udg_team[1..4]` and marked
active at startup.

This pass adds deterministic first- and second-place tracking to that four-way
Solo mode. The dormant `udg_mode_6v6` path is left unchanged; this map never
sets that flag to true.

## Previous problems

- The END trigger inferred a winning team but did not retain the winning player.
- There was no runner-up result or MMD value.
- The six victory branches were independent and did not require the alleged
  winner to still be active. If all competitors became inactive, multiple teams
  could satisfy the old “all opponents inactive” predicates.
- The trigger contains long sleeps but had no one-shot guard, allowing another
  END execution to begin while the first finale was still running.
- A leave-triggered finale still tried to read a killing unit and announce a
  “final strike,” even though no killing unit exists for a player-leave event.

## New state

- `SoloFoots_WinnerPlayerNumber` — converted player number of first place.
- `SoloFoots_SecondPlacePlayerNumber` — converted player number of second place.
- `SoloFoots_LastEliminatedPlayerNumber` — locally captured player number from
  the leave/base-death event that caused the latest active-to-inactive change.
- `SoloFoots_EndGameRecorded` — one-shot lock set before the existing victory
  sequence reaches its first sleep.

`SoloFootsTeamRepresentative` maps the legacy team ranges to the four actual
competitors: `1..3 -> 1`, `4..6 -> 5`, `7..9 -> 8`, and `10..12 -> 12`.

`SoloFootsFindWinner` returns a player only when exactly one of the four
competitors remains active. Ordinary eliminations and a zero-survivor state do
not begin the finale.

`SoloFootsRecordFinalPlacements` records the sole survivor as first and the last
distinct eliminated team representative as second. It runs once, before the
existing team victory branch and before any trigger sleep.

## Result outputs

The existing `MMD_FLAG_WINNER` and `MMD_FLAG_LOSER` calls remain unchanged for
compatibility. Since MMD has no runner-up flag, the pass additionally defines:

`Placement`: integer, low-is-better, leaderboard suggested

It writes `1` for the winner and `2` for the runner-up. Definition occurs at
end-game immediately before the updates, when the deferred MMD initializer is
known to have completed. The one-shot guard prevents redefinition.

Two `PLACEMENT` custom records mirror the standard values with converted slot
and player name, and all players see explicit Winner and Second place messages.

The final team announcement now distinguishes the cause: a base kill retains
the final-strike player, a leave names the runner-up who left, and an
environmental kill safely falls back to the winning team without dereferencing
a nonexistent killing unit.

## Preserved behavior

- Existing team-specific victory/defeat strings and sounds.
- Existing final-strike and team-win announcements for base kills, with a safe
  leave/environment fallback.
- Existing `PLAYER_STATE_GAME_RESULT` writes.
- Existing MMD winner/loser flags and their pacing.
- Existing Warcraft victory/defeat calls.
- The v17 five-tick inactive-unit removal grace period.
- Player-leave, base-death, KOTH, visibility, and resource handling outside the
  added placement capture.

## Static verification

- Four competitor slots checked exactly once each: `1`, `5`, `8`, `12`.
- One sole-survivor finder.
- One one-shot end-game lock.
- One MMD `Placement` definition.
- Exactly two MMD placement updates: values `1` and `2`.
- JASS parser: `OK` (`8,870` top-level declarations).
- Source SHA256 before packaging:
  `2C9A719C2DBDBD74DAE35CB2B2176C27E80063748578A67BB6D398CD47A863C6`.

## Required in-game tests

1. Destroy players in a fixed order; verify the sole survivor is announced as
   Winner and the penultimate survivor as Second place.
2. Repeat with each of the four slots as winner.
3. With three competitors alive, eliminate one; verify no finale starts.
4. Have the penultimate competitor leave; verify the leaver is recorded second
   and the survivor first.
5. Lose a base to neutral/environmental damage; verify placement still uses
   survivor/elimination order rather than the killing player.
6. Cause the final two bases to die as close together as possible; verify only
   one finale runs and the first sole survivor remains the recorded winner.
7. Inspect the MMD output for one `DefVarP Placement`, winner value `1`, runner-up
   value `2`, and the original winner/loser flags.
8. Re-test Transmute in flight during the penultimate base loss; verify the map
   records placements and does not crash.

Live Warcraft III execution was not available during source validation.
