"""
Batch-fetch OHLCV bars for multiple symbols using a thread pool.
Returns structured data ready for signal computation.
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

log = logging.getLogger(__name__)

# Number of bars needed: 21 (long MA) + 5 buffer + 20 (volume avg) = 26 minimum
BAR_LIMIT = 30


def fetch_bars_for_symbol(client, symbol: str) -> tuple[str, list]:
    """Fetch daily bars for a single symbol. Returns (symbol, bars)."""
    try:
        bars = client.get_bars(symbol, timeframe="1Day", limit=BAR_LIMIT)
        return symbol, bars
    except Exception as exc:
        log.warning("Failed to fetch bars for %s: %s", symbol, exc)
        return symbol, []


def fetch_all_bars(client, symbols: list[str], max_workers: int = 20) -> dict[str, list]:
    """
    Batch-fetch daily bars for all symbols in parallel.
    Returns {symbol: [bar, ...]} — symbols with no data are excluded.
    """
    results: dict[str, list] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(fetch_bars_for_symbol, client, sym): sym for sym in symbols}
        for future in as_completed(futures):
            symbol, bars = future.result()
            if bars:
                results[symbol] = bars
            else:
                log.debug("No bar data for %s — skipping", symbol)
    log.info("Fetched bars for %d / %d symbols", len(results), len(symbols))
    return results
