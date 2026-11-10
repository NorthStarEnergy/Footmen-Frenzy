# Veigar permanent Z stacks v82

Built on verified Veigar Visuals v81. Release: release/FF799X_Rx_Veigar_Stacks_v82_TEST.w3x.

Baleful Strike is now bound to Z. Every enemy unit killed directly by Veigar, by any attack or spell, grants +1 permanent bonus damage to Z; an enemy hero grants +5 instead. Enemy summons count; illusions, allied units and structures do not. Stacks accrue even before Z is learned, belong to each individual Veigar, and persist through death/revival and ability upgrades. This replaces the former permanent Intelligence rewards. Existing base damage and 60% Intelligence scaling remain.

The ability title and hover description show the current bonus (for example, +125 damage), using per-unit ability string fields. Refreshed on kills and every second; D remains Equilibrium. This is a tooltip counter, not an icon badge. Other heroes and Veigar spells retain their existing bindings and behavior.

Runtime and World Editor source compile successfully; archive readback and preservation checks pass. See verification.json and behavior-checks.json. No Warcraft engine or multiplayer playtest has been performed. Verify tooltip refresh, real damage/kill attribution, death/revival and two simultaneous Veigars in game.

Rebuild with the bundled Python and build.py; legacy JASS compilers require running outside the sandbox on this machine. Run check.py afterward for mocked kill-handler and damage-expression checks. Original v81 remains untouched; this candidate has not been installed or deployed.
