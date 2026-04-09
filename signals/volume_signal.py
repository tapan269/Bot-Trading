"""
Volume Signal: score 0.0–1.0 based on today's volume vs. 20-day average.

volume_ratio = today_volume / avg_20d_volume
score = min(volume_ratio / 2.0, 1.0)

Interpretation:
  ratio 0×  → score 0.0  (no volume / extremely low)
  ratio 1×  → score 0.5  (average volume)
  ratio 2×+ → score 1.0  (double average = very high interest)
"""

AVG_VOLUME_PERIOD = 20


def compute_volume_score(bars: list[dict]) -> float:
    """Return volume score in [0, 1]. Returns 0.5 (neutral) if insufficient data."""
    if len(bars) < AVG_VOLUME_PERIOD + 1:
        return 0.5

    volumes = [b["v"] for b in bars]
    today_vol = volumes[-1]
    avg_vol = sum(volumes[-(AVG_VOLUME_PERIOD + 1):-1]) / AVG_VOLUME_PERIOD

    if avg_vol == 0:
        return 0.5

    ratio = today_vol / avg_vol
    return min(ratio / 2.0, 1.0)
