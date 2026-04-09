"""
Alpaca Paper Trading Bot
Endpoint: https://paper-api.alpaca.markets/v2
Strategy: Simple Moving Average Crossover
"""

import logging
import time

from alpaca_client import AlpacaClient
from config import (
    LONG_MA_PERIOD,
    POLL_INTERVAL_SECONDS,
    SHORT_MA_PERIOD,
    SYMBOLS,
    TRADE_QTY,
)
from storage import LocalStorage
from strategies.simple_ma import MAConfig, Signal, compute_ma_values, compute_signal

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

MA_CFG = MAConfig(short_period=SHORT_MA_PERIOD, long_period=LONG_MA_PERIOD)


def run_once(client: AlpacaClient, store: LocalStorage) -> None:
    """Evaluate signals and place orders for all configured symbols."""
    for symbol in SYMBOLS:
        try:
            bars = client.get_bars(symbol, timeframe="1Day", limit=MA_CFG.long_period + 5)
            if not bars:
                log.warning("%s: no bar data returned", symbol)
                continue

            signal = compute_signal(bars, MA_CFG)
            short_ma, long_ma = compute_ma_values(bars, MA_CFG)
            position = client.get_position(symbol)
            has_position = position is not None

            log.info(
                "%s | signal=%s | position=%s",
                symbol,
                signal.value,
                position.get("qty") if has_position else "none",
            )

            store.save_signal(symbol, signal.value, short_ma, long_ma)

            if signal == Signal.BUY and not has_position:
                order = client.place_market_order(symbol, TRADE_QTY, "buy")
                log.info("%s: BUY order placed — id=%s", symbol, order.get("id"))
                store.save_order(symbol, "buy", TRADE_QTY, order.get("id"))

            elif signal == Signal.SELL and has_position:
                order = client.place_market_order(symbol, TRADE_QTY, "sell")
                log.info("%s: SELL order placed — id=%s", symbol, order.get("id"))
                store.save_order(symbol, "sell", TRADE_QTY, order.get("id"))

        except Exception as exc:
            log.error("%s: error — %s", symbol, exc)


def main() -> None:
    client = AlpacaClient()
    store = LocalStorage()

    account = client.get_account()
    log.info(
        "Connected | account=%s | buying_power=$%s | portfolio_value=$%s",
        account.get("id"),
        account.get("buying_power"),
        account.get("portfolio_value"),
    )
    store.save_portfolio_snapshot(
        float(account.get("buying_power", 0)),
        float(account.get("portfolio_value", 0)),
    )

    log.info(
        "Starting bot | symbols=%s | MA(%d/%d) | qty=%d | interval=%ds | db=%s",
        SYMBOLS,
        SHORT_MA_PERIOD,
        LONG_MA_PERIOD,
        TRADE_QTY,
        POLL_INTERVAL_SECONDS,
        store.db_path,
    )

    while True:
        run_once(client, store)
        log.info("Sleeping %ds …", POLL_INTERVAL_SECONDS)
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
