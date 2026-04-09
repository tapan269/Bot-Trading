"""
Combine MA, sentiment, and volume signals into a single weighted stock score.

raw_score = W_MA * ma_score + W_SENTIMENT * sentiment_score + W_VOLUME * volume_score
"""

from dataclasses import dataclass

from config import SIGNAL_WEIGHT_MA, SIGNAL_WEIGHT_SENTIMENT, SIGNAL_WEIGHT_VOLUME
from signals.ma_signal import compute_ma_score
from signals.sentiment_signal import compute_sentiment_score
from signals.volume_signal import compute_volume_score


@dataclass
class StockScore:
    symbol: str
    ma_score: float
    sentiment_score: float
    volume_score: float
    raw_score: float
    sector: str = ""
    sector_score: float = 0.0
    final_score: float = 0.0
    normalized_score: float = 0.0
    rank: int = 0


def score_stock(
    symbol: str,
    bars: list[dict],
    headlines: list[str],
    sector: str = "",
) -> StockScore:
    """Compute all signal scores and raw combined score for one stock."""
    ma = compute_ma_score(bars)
    sentiment = compute_sentiment_score(headlines)
    volume = compute_volume_score(bars)
    raw = SIGNAL_WEIGHT_MA * ma + SIGNAL_WEIGHT_SENTIMENT * sentiment + SIGNAL_WEIGHT_VOLUME * volume
    return StockScore(
        symbol=symbol,
        ma_score=ma,
        sentiment_score=sentiment,
        volume_score=volume,
        raw_score=raw,
        sector=sector,
    )


def score_stocks(
    bars_map: dict[str, list],
    news_map: dict[str, list[str]],
    sector_map: dict[str, str],
) -> list[StockScore]:
    """Score all symbols that have bar data."""
    scores = []
    for symbol, bars in bars_map.items():
        headlines = news_map.get(symbol, [])
        sector = sector_map.get(symbol, "Unknown")
        scores.append(score_stock(symbol, bars, headlines, sector))
    return scores
