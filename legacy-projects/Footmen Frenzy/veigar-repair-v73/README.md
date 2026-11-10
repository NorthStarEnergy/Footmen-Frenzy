# Veigar casting and cage test

Open `release/FF799X_Rx_Veigar_Cage_Range_v73_TEST.w3x`. This is built on the Soul Hook + Mundo v72 candidate and keeps its UI, Stalker and other inherited changes.

Veigar's spell object records had numeric field types inconsistent with Warcraft's installed ability metadata. This candidate corrects range, cooldown and other affected numeric field types on all four spells without changing their configured values. The intended casting ranges are Q 700, W 900, E 900 and R 650. The cage stun ability's projectile-speed field was also incorrectly typed and set to zero; it is now an integer speed of 10,000, using the map's standard spell dummy. The `STUNNED` feedback now lasts until the stun ends at all six ranks.

Event Horizon catches enemy units touching or crossing the pentagonal rim, once per unit per cage. The interior is safe. Buildings, magic-immune and invulnerable units, Locust/dummy units, and allies are excluded. Rank durations are 1.5 / 1.75 / 2 / 2.25 / 2.5 / 2.75 seconds.

Validation: runtime and World Editor source both compile. Fifty-seven checks execute the actual cage geometry, scan and feedback code with mocked natives, check all spell ranges and field types against installed game metadata, and verify all stun ranks. All unrelated archive entries are preserved. This is not an engine playtest and cannot establish whether the object type mismatch or projectile was the sole cause of the reported symptoms.

**Please test in Warcraft:** cast all four spells near their maximum ranges and beyond; place E across a moving enemy footman and test entry and exit; test all ranks, magic immunity, allies and overlapping cages. Check that the stun actually interrupts movement and that its visual disappears when the stun ends. Also test multiple clients.

SHA-256 `2b602b70eb95cd7d3b5549bf0f7b71256983c3171871642f871ed9bd60a61701`. This is a separate test build and has not been installed or deployed.
