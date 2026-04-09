"""
SP500 Multi-Signal Trading Bot
Endpoint : https://paper-api.alpaca.markets/v2
Strategy : MA crossover + news sentiment + volume scoring
Universe : ~150 SP500 stocks across 11 GICS sectors
Rebalance: every 2 hours during market hours
"""

import logging
import time

from alpaca_client import AlpacaClient
from config import REBALANCE_INTERVAL_SECONDS
from data.market_data import fetch_all_bars
from data.news_data import fetch_all_news
from portfolio.manager import log_rankings, rebalance
from scoring.sector_scorer import apply_sector_scores
from scoring.stock_scorer import score_stocks
from universe import STOCK_SECTOR, SYMBOLS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)


def run_cycle(client: AlpacaClient) -> None:
    """Execute one full scoring + rebalancing cycle."""
    log.info("── Starting rebalance cycle ──────────────────────────────────────")

    # 1. Fetch market data in parallel
    log.info("Fetching bars for %d symbols …", len(SYMBOLS))
    bars_map = fetch_all_bars(client, SYMBOLS)

    # 2. Fetch news in parallel
    log.info("Fetching news for %d symbols …", len(SYMBOLS))
    news_map = fetch_all_news(client, list(bars_map.keys()))

    # 3. Score each stock
    scores = score_stocks(bars_map, news_map, STOCK_SECTOR)
    if not scores:
        log.warning("No scores computed — skipping rebalance")
        return

    # 4. Apply sector hierarchy + normalize + rank
    scores = apply_sector_scores(scores)

    # 5. Log top 30 rankings
    log_rankings(scores, top_n=30)

    # 6. Execute trades
    rebalance(client, scores)


def main() -> None:
    client = AlpacaClient()

    account = client.get_account()
    log.info(
        "Connected | portfolio_value=$%s | buying_power=$%s",
        account.get("portfolio_value"),
        account.get("buying_power"),
    )
    log.info(
        "Universe: %d stocks | Rebalance interval: %ds (%dm)",
        len(SYMBOLS),
        REBALANCE_INTERVAL_SECONDS,
        REBALANCE_INTERVAL_SECONDS // 60,
    )

    while True:
        try:
            clock = client.get_clock()
            if clock.get("is_open"):
                run_cycle(client)
            else:
                next_open = clock.get("next_open", "unknown")
                log.info("Market is closed. Next open: %s", next_open)
        except Exception as exc:
            log.error("Cycle error: %s", exc, exc_info=True)

        log.info("Sleeping %d seconds until next cycle …", REBALANCE_INTERVAL_SECONDS)
        time.sleep(REBALANCE_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
