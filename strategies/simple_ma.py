"""
Simple Moving Average Crossover Strategy.

Signal logic:
  - BUY  when short MA crosses above long MA (golden cross)
  - SELL when short MA crosses below long MA (death cross)
  - HOLD otherwise
"""

from dataclasses import dataclass
from enum import Enum


class Signal(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass
class MAConfig:
    short_period: int = 9
    long_period: int = 21


def _moving_average(prices: list[float], period: int) -> float:
    if len(prices) < period:
        raise ValueError(f"Need at least {period} prices, got {len(prices)}")
    return sum(prices[-period:]) / period


def compute_ma_values(
    bars: list[dict], cfg: MAConfig
) -> tuple[float | None, float | None]:
    """Return (short_ma, long_ma) for the latest bar, or (None, None) if insufficient data."""
    closes = [bar["c"] for bar in bars]
    if len(closes) < cfg.long_period:
        return None, None
    return _moving_average(closes, cfg.short_period), _moving_average(closes, cfg.long_period)


def compute_signal(bars: list[dict], cfg: MAConfig) -> Signal:
    """Compute a trading signal from a list of OHLCV bar dicts.

    Each bar dict must contain a 'c' (close) key.
    Requires at least long_period + 1 bars to detect a crossover.
    """
    closes = [bar["c"] for bar in bars]
    needed = cfg.long_period + 1

    if len(closes) < needed:
        return Signal.HOLD

    # Current MAs
    short_now = _moving_average(closes, cfg.short_period)
    long_now = _moving_average(closes, cfg.long_period)

    # Previous MAs (shift by one bar)
    prev_closes = closes[:-1]
    short_prev = _moving_average(prev_closes, cfg.short_period)
    long_prev = _moving_average(prev_closes, cfg.long_period)

    if short_prev <= long_prev and short_now > long_now:
        return Signal.BUY
    if short_prev >= long_prev and short_now < long_now:
        return Signal.SELL
    return Signal.HOLD
