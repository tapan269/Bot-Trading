"""
Sentiment Signal: score 0.0–1.0 using VADER on news headlines.

VADER compound score is in [-1, 1].
Normalized to [0, 1] via:  score = (compound + 1) / 2
Default: 0.5 (neutral) when no news is available.
"""

import logging

log = logging.getLogger(__name__)

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    _analyzer = SentimentIntensityAnalyzer()
    VADER_AVAILABLE = True
except ImportError:
    _analyzer = None
    VADER_AVAILABLE = False
    log.warning(
        "vaderSentiment not installed — sentiment scores will default to 0.5 neutral. "
        "Run: pip install vaderSentiment"
    )


def _vader_compound(text: str) -> float:
    if not VADER_AVAILABLE or not _analyzer:
        return 0.0  # neutral before normalization
    return _analyzer.polarity_scores(text)["compound"]


def compute_sentiment_score(headlines: list[str]) -> float:
    """Return sentiment score in [0, 1]. Returns 0.5 if no headlines."""
    if not headlines:
        return 0.5

    compounds = [_vader_compound(h) for h in headlines]
    avg_compound = sum(compounds) / len(compounds)
    return (avg_compound + 1.0) / 2.0  # normalize [-1,1] → [0,1]
