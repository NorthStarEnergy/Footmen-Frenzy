import assert from "node:assert/strict";
import {
  calculateRatingChanges,
  expectedScore,
  kFactor,
} from "./rating-engine.mjs";

assert.equal(expectedScore(1500, 1500), 0.5);
assert.equal(kFactor({ rating: 1500, gamesPlayed: 0 }), 40);
assert.equal(kFactor({ rating: 1500, gamesPlayed: 10 }), 28);
assert.equal(kFactor({ rating: 2000, gamesPlayed: 10 }), 20);

const result = calculateRatingChanges([
  {
    teamId: 1,
    placement: 1,
    players: [
      { playerId: "a", rating: 1500, gamesPlayed: 10 },
      { playerId: "b", rating: 1500, gamesPlayed: 10 },
    ],
  },
  {
    teamId: 2,
    placement: 2,
    players: [
      { playerId: "c", rating: 1500, gamesPlayed: 10 },
      { playerId: "d", rating: 1500, gamesPlayed: 10 },
    ],
  },
]);

assert.deepEqual(result.map((row) => row.delta), [14, 14, -14, -14]);
assert.throws(
  () =>
    calculateRatingChanges([
      { teamId: 1, placement: 1, players: [{ playerId: "a", rating: 1500, gamesPlayed: 0 }] },
      { teamId: 2, placement: 2, players: [{ playerId: "a", rating: 1500, gamesPlayed: 0 }] },
    ]),
  /Duplicate/,
);

console.log("rating-engine tests passed");
