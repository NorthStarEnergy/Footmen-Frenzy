# Veigar ultimate stacking v83

Built on verified v82. Release: release/FF799X_Rx_Veigar_Ultimate_v83_TEST.w3x.

Z killing blows grant permanent bonus damage to V: +1 per enemy unit, +5 per enemy hero (not +6). The ultimate has a separate per-Veigar counter, persists through death/revival and skill upgrades, and accrues even before the ultimate is learned. Attacks and other spells do not grant V stacks. Illusions and structures are excluded; enemy summoned units count. Z retains its v82 all-kill stacking behavior. V retains its original base damage, Intelligence scaling and hero targeting, with the new flat bonus added.

Primordial Burst now uses V. Its title and hover tooltip show the current bonus, refreshed on kills and once per second. Runtime and World Editor scripts compile; packed archive readback and unrelated member preservation pass. See verification.json and behavior-checks.json for static/mocked checks.

Engine testing remains pending: confirm Z lethal/nonlethal hits, other-spell kills, hero kills, V damage, tooltip refresh, revival and simultaneous Veigars in Warcraft. No deployment or installation performed. Original v82 preserved.

Rebuild using the bundled Python: build.py, then check.py. Legacy JASS compiler execution requires running outside the sandbox on this machine.
