# SF Test 1.7 v5 - Spawn Fairness

The batched auto-spawn previously gave Player 1 two additional footmen and always processed Player 1 first. Roar timing was also staggered by team.

Version 5 changes the mass spawn so that:

- every team receives exactly 85 footmen;
- matching formation batches spawn for all four teams on the same timer tick;
- all four roar effects fire on the same timer tick;
- the seven-step batching still avoids creating the entire army in one frame.
