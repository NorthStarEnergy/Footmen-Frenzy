# TF orbs v45c

Base: Flaming Raven v45b. Z now uses a small tintable orb with a soft halo and 0.09-second ribbon wake. Existing three-projectile fan, speed and narrow swept damage remain unchanged. X uses the same orb, displayed 330 units above the hero with scale 1.1 and no text tags. Cycling and locked colors both use the stored selection color. The ten-second locked window remains.

All three X throws have explicit unit targeting and cast range at every rank: 1000 / 1025 / 1050 / 1075 / 1100 / 1150. Reference: A054 Death Coil 900 / 950 / 1000 / 1050 / 1100 / 1150, with early bonus tapering +100 / +75 / +50 / +25 / 0 / 0. Tooltips updated.

Validation: JASS compile, 92 TF behavior checks, 18 explicit range checks, no text-tag calls in selection/display/cleanup, MDX parse/serialize roundtrip, archive payload readback, 1338 unrelated payloads preserved. Mundo, Flaming Raven, Loaded Dice and unrelated script functions preserved. In-game visual testing pending.
