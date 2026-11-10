export const DEFAULT_RATING = 1500;
export const ELO_SCALE = 400;
export const MAX_MATCH_DELTA = 48;

export function kFactor(player) {
  if (player.gamesPlayed < 10) return 40;
  if (player.rating >= 2000) return 20;
  return 28;
}

export function expectedScore(rating, opposingRating) {
  return 1 / (1 + 10 ** ((opposingRating - rating) / ELO_SCALE));
}

function actualScore(placement, opposingPlacement) {
  if (placement < opposingPlacement) return 1;
  if (placement > opposingPlacement) return 0;
  return 0.5;
}

function clamp(value, low, high) {
  return Math.max(low, Math.min(high, value));
}

/**
 * Calculates a multi-team, pairwise Elo result.
 *
 * Input teams:
 * [{ teamId: 1, placement: 1,
 *    players: [{ playerId: "uuid", rating: 1500, gamesPlayed: 0 }] }]
 */
export function calculateRatingChanges(teams) {
  if (!Array.isArray(teams) || teams.length < 2 || teams.length > 4) {
    throw new Error("A ranked match must contain 2 to 4 teams.");
  }

  const seenPlayers = new Set();
  const strengths = new Map();
  for (const team of teams) {
    if (!Number.isInteger(team.placement) || team.placement < 1 || !team.players?.length) {
      throw new Error("Every team needs a valid placement and at least one player.");
    }
    let total = 0;
    for (const player of team.players) {
      if (seenPlayers.has(player.playerId)) throw new Error("Duplicate player identity.");
      if (!Number.isFinite(player.rating) || !Number.isInteger(player.gamesPlayed)) {
        throw new Error("Invalid player rating state.");
      }
      seenPlayers.add(player.playerId);
      total += player.rating;
    }
    strengths.set(team.teamId, total / team.players.length);
  }

  const changes = [];
  for (const team of teams) {
    const opponents = teams.filter((candidate) => candidate.teamId !== team.teamId);
    for (const player of team.players) {
      let residual = 0;
      for (const opponent of opponents) {
        residual +=
          actualScore(team.placement, opponent.placement) -
          expectedScore(strengths.get(team.teamId), strengths.get(opponent.teamId));
      }
      residual /= opponents.length;
      const delta = Math.round(
        clamp(kFactor(player) * residual, -MAX_MATCH_DELTA, MAX_MATCH_DELTA),
      );
      changes.push({
        playerId: player.playerId,
        teamId: team.teamId,
        ratingBefore: player.rating,
        delta,
        ratingAfter: player.rating + delta,
      });
    }
  }
  return changes;
}

