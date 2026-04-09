"""
Sector-level scoring and hierarchical weighting.

Steps:
1. Compute sector_score = mean raw_score of all stocks in that sector
2. Apply hierarchical blend:
   final_score = (1 - SECTOR_WEIGHT) * raw_score + SECTOR_WEIGHT * sector_score
3. Min-max normalize final_score across all stocks → normalized_score in [0, 1]
4. Assign rank (1 = best)
"""

from config import SECTOR_WEIGHT
from scoring.stock_scorer import StockScore


def apply_sector_scores(scores: list[StockScore]) -> list[StockScore]:
    """
    Mutates each StockScore in-place to set sector_score, final_score,
    normalized_score, and rank. Returns the same list sorted by rank.
    """
    # Step 1: compute sector means
    sector_totals: dict[str, list[float]] = {}
    for s in scores:
        sector_totals.setdefault(s.sector, []).append(s.raw_score)
    sector_means: dict[str, float] = {
        sec: sum(vals) / len(vals) for sec, vals in sector_totals.items()
    }

    # Step 2: hierarchical blend
    for s in scores:
        s.sector_score = sector_means.get(s.sector, 0.5)
        s.final_score = (1 - SECTOR_WEIGHT) * s.raw_score + SECTOR_WEIGHT * s.sector_score

    # Step 3: min-max normalize
    final_vals = [s.final_score for s in scores]
    min_f, max_f = min(final_vals), max(final_vals)
    spread = max_f - min_f if max_f != min_f else 1.0
    for s in scores:
        s.normalized_score = (s.final_score - min_f) / spread

    # Step 4: rank (1 = highest normalized score)
    scores.sort(key=lambda s: s.normalized_score, reverse=True)
    for i, s in enumerate(scores):
        s.rank = i + 1

    return scores
