"""
Fetch news headlines from the Alpaca News API and compute VADER sentiment scores.
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

log = logging.getLogger(__name__)

NEWS_LIMIT = 10  # headlines per symbol


def fetch_news_for_symbol(client, symbol: str) -> tuple[str, list[str]]:
    """Fetch recent news headlines for a single symbol."""
    try:
        articles = client.get_news(symbol, limit=NEWS_LIMIT)
        headlines = [a.get("headline", "") for a in articles if a.get("headline")]
        return symbol, headlines
    except Exception as exc:
        log.warning("Failed to fetch news for %s: %s", symbol, exc)
        return symbol, []


def fetch_all_news(client, symbols: list[str], max_workers: int = 20) -> dict[str, list[str]]:
    """
    Batch-fetch news headlines for all symbols in parallel.
    Returns {symbol: [headline, ...]}
    """
    results: dict[str, list[str]] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(fetch_news_for_symbol, client, sym): sym for sym in symbols}
        for future in as_completed(futures):
            symbol, headlines = future.result()
            results[symbol] = headlines
    return results
