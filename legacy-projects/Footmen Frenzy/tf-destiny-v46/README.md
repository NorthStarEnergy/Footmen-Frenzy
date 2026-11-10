# Twisted Fate Destiny v46

Base: v45c; Flaming Raven and prior Mundo/Dice changes retained.

X range: 700 / 750 / 800 / 850 / 900 / 950 for all three locked throws.
Z cast and projectile range: 1450 / 1500 / 1550 / 1600 / 1650 / 1700. Each cast snapshots its rank's travel distance.
C icon: fixed the opaque frame that had completely covered the artwork. Rebuilt visible dice artwork with a narrow border, plus disabled variant, using uncompressed TGA icons.

Destiny: entire-world fog modifier plus invisible/invulnerable true-sight grid (1400 radius, 1800 spacing) for 10 / 13 / 15 seconds. Separate timer owns vision and detector cleanup. Using Gate, not using Gate, interruption, or caster death does not shorten the timer. Gate changes from Blink to point-target Channel with 2-second follow-through and spell animation. Successful finish moves TF to a walkable target, removes Gate, and restores the still-cooling-down Destiny button. Reveal remains active until its scheduled end. An interrupted channel does not teleport; blocked destinations are rejected.

Validation: JASS compilation, 110 translated-JASS TF and reveal checks with mocked natives, 18 explicit X range checks, binary object validation, icon visual inspection, archive readback and 1339 unrelated payloads preserved. Live engine visual/channel/detection testing remains pending.
