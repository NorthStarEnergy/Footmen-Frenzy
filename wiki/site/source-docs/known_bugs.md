# Known Bugs

Use this file to track reproducible issues while editing and testing the map.

## Template

```text
Date:
Build:
Area:
Steps:
Expected:
Actual:
Notes:
```

## Current Notes

- Do not use recode pass 10 for testing. Its SD wildcard injection joined two JASS statements on one line; pass 11 corrects this and passes the bundled `pjass` syntax parser.
- Pass 21 has not yet been launched in Warcraft III, so setup, all three retained options, tavern rendering, AR repick, shop boundaries, Scroll of Beast, Mass Start, timed tier unlocks, repaired spells, Guardian Force Field levels 1-6, allied upgrades, and player-lifecycle behavior still require an in-game test.
- Guardian Force Field now passes parser, ownership, and archive checks, but its 1/1/3/3/5/5 wall layout, collision pathing, stun, natural expiry, Detonate, and overlapping-caster behavior need runtime confirmation.
- Pass 21's Cripple Wave, Mirror Image, Purge the Dead, Invisibility/Inner Fire scrolls, Frostbolt tower upgrade, and player-lifecycle behavior pass static checks but need runtime confirmation.
- Specifically test a departed player's surviving base after the connected ally loses their own base, then defeat a different team and confirm the control remains. Also test vision persistence, stale votekick/autopool dialogs, admin-kick idempotency, gold remainders, and one-time final victory.
- Saving an injected recode build in World Editor will regenerate `war3map.j` from the old GUI trigger data and remove the injected systems.
- Previous debug text was found in the original generated script around the hero setup area.
- The archive starts directly with MPQ data and has no optional 512-byte HM3W lobby header. Warcraft loads this format, but compatibility with third-party hosting bots has not been tested.
