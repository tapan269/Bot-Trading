"""
MA Signal: score 0.0–1.0 based on price position relative to short/long moving averages.

Score logic:
  1.0  — price above both MAs AND recent golden cross (short crossed above long)
  0.8  — price above both MAs, no recent crossover
  0.6  — price above long MA only (short MA below long)
  0.3  — price below short MA but above long MA (weakening)
  0.0  — price below both MAs
"""

from config import SHORT_MA_PERIOD, LONG_MA_PERIOD


def _ma(prices: list[float], period: int) -> float | None:
    if len(prices) < period:
        return None
    return sum(prices[-period:]) / period


def compute_ma_score(bars: list[dict]) -> float:
    """Return MA score in [0, 1]. Returns 0.5 (neutral) if insufficient data."""
    if len(bars) < LONG_MA_PERIOD + 2:
        return 0.5

    closes = [b["c"] for b in bars]
    price = closes[-1]

    short_now = _ma(closes, SHORT_MA_PERIOD)
    long_now = _ma(closes, LONG_MA_PERIOD)

    if short_now is None or long_now is None:
        return 0.5

    # Detect recent golden/death cross using previous bar
    prev_closes = closes[:-1]
    short_prev = _ma(prev_closes, SHORT_MA_PERIOD)
    long_prev = _ma(prev_closes, LONG_MA_PERIOD)

    golden_cross = (
        short_prev is not None
        and long_prev is not None
        and short_prev <= long_prev
        and short_now > long_now
    )

    if price > short_now and price > long_now:
        return 1.0 if golden_cross else 0.8
    if price > long_now:
        return 0.6
    if price > short_now:
        return 0.3
    return 0.0
