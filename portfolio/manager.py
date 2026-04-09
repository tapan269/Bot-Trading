"""
Portfolio manager: select top-N stocks, place notional orders, handle sells and rebalancing.

Buy logic:
  - Select top TOP_N stocks by normalized_score
  - Equal-weight notional: target = portfolio_value * (1 - CASH_BUFFER) / TOP_N
  - Buy only stocks not already held

Sell logic:
  - Close if rank > SELL_RANK_THRESHOLD (fallen out of top buffer)
  - Close if ma_score < MA_REVERSAL_THRESHOLD (hard trend reversal signal)

Rebalance:
  - Cancel all open orders first
  - Then evaluate sells, then buys
"""

import logging

from config import (
    MA_REVERSAL_THRESHOLD,
    PORTFOLIO_CASH_BUFFER,
    SELL_RANK_THRESHOLD,
    TOP_N,
)
from scoring.stock_scorer import StockScore

log = logging.getLogger(__name__)


def rebalance(client, scores: list[StockScore]) -> None:
    """
    Execute a full rebalance cycle:
    1. Cancel stale open orders
    2. Sell positions that no longer qualify
    3. Buy top-N positions not yet held
    """
    # ── Step 1: cancel open orders ────────────────────────────────────────
    try:
        client.cancel_all_orders()
        log.info("Cancelled all open orders")
    except Exception as exc:
        log.warning("Could not cancel orders: %s", exc)

    # ── Step 2: fetch current positions ───────────────────────────────────
    try:
        positions = {p["symbol"]: p for p in client.get_positions()}
    except Exception as exc:
        log.error("Could not fetch positions: %s", exc)
        return

    # ── Step 3: fetch account for buying power ────────────────────────────
    try:
        account = client.get_account()
        portfolio_value = float(account.get("portfolio_value", 0))
    except Exception as exc:
        log.error("Could not fetch account: %s", exc)
        return

    # Build rank + score lookup
    score_by_symbol = {s.symbol: s for s in scores}

    # ── Step 4: sell ──────────────────────────────────────────────────────
    for symbol, pos in positions.items():
        stock = score_by_symbol.get(symbol)
        sell_reason = None

        if stock is None:
            sell_reason = "not in universe"
        elif stock.rank > SELL_RANK_THRESHOLD:
            sell_reason = f"rank {stock.rank} > threshold {SELL_RANK_THRESHOLD}"
        elif stock.ma_score < MA_REVERSAL_THRESHOLD:
            sell_reason = f"MA reversal (ma_score={stock.ma_score:.2f})"

        if sell_reason:
            try:
                client.close_position(symbol)
                log.info("SELL %s — %s", symbol, sell_reason)
            except Exception as exc:
                log.error("Failed to close %s: %s", symbol, exc)

    # ── Step 5: buy ───────────────────────────────────────────────────────
    # Refresh positions after sells
    try:
        positions = {p["symbol"]: p for p in client.get_positions()}
    except Exception as exc:
        log.error("Could not refresh positions: %s", exc)
        return

    target_notional = portfolio_value * (1 - PORTFOLIO_CASH_BUFFER) / TOP_N
    top_stocks = [s for s in scores if s.rank <= TOP_N]

    bought, skipped = 0, 0
    for stock in top_stocks:
        if stock.symbol in positions:
            skipped += 1
            continue
        try:
            order = client.place_notional_order(stock.symbol, target_notional, "buy")
            log.info(
                "BUY %s | rank=%d | score=%.3f | notional=$%.2f | order_id=%s",
                stock.symbol,
                stock.rank,
                stock.normalized_score,
                target_notional,
                order.get("id"),
            )
            bought += 1
        except Exception as exc:
            log.error("Failed to buy %s: %s", stock.symbol, exc)

    log.info(
        "Rebalance complete | portfolio_value=$%.2f | bought=%d | skipped=%d | held=%d",
        portfolio_value,
        bought,
        skipped,
        len(positions),
    )


def log_rankings(scores: list[StockScore], top_n: int = 30) -> None:
    """Log the top-N ranked stocks in a readable table."""
    log.info("=" * 70)
    log.info("%-5s %-8s %-28s %-6s %-6s %-6s %-6s", "Rank", "Symbol", "Sector", "MA", "Sent", "Vol", "Score")
    log.info("-" * 70)
    for s in scores[:top_n]:
        log.info(
            "%-5d %-8s %-28s %-6.2f %-6.2f %-6.2f %-6.3f",
            s.rank,
            s.symbol,
            s.sector[:27],
            s.ma_score,
            s.sentiment_score,
            s.volume_score,
            s.normalized_score,
        )
    log.info("=" * 70)
