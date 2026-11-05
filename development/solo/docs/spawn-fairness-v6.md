# SF Test 1.7 v6 - Roar Position Fairness

Version 5 equalized unit counts and spawn timing, but the roar caster positions were still biased.

- Team 1 cast from the upper-left as intended.
- Team 2 cast from the upper-right as intended.
- Teams 3 and 4 incorrectly also cast from the upper-left, away from their own armies.

Version 6 assigns the roar caster to the matching quadrant for every team:

- Team 1: upper-left
- Team 2: upper-right
- Team 3: lower-right
- Team 4: lower-left

All four roars continue to fire during the same timer tick.
