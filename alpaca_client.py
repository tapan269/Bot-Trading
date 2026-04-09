"""
Alpaca Paper Trading API client.
Base URL: https://paper-api.alpaca.markets/v2
"""

import requests
from config import ALPACA_BASE_URL, ALPACA_API_KEY, ALPACA_SECRET_KEY

DATA_URL = "https://data.alpaca.markets/v2"
NEWS_URL = "https://data.alpaca.markets/v1beta1"


class AlpacaClient:
    def __init__(self):
        self.base_url = ALPACA_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "APCA-API-KEY-ID": ALPACA_API_KEY,
            "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY,
            "Content-Type": "application/json",
        })

    def _get(self, path: str, params: dict = None) -> dict:
        resp = self.session.get(f"{self.base_url}{path}", params=params)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, payload: dict) -> dict:
        resp = self.session.post(f"{self.base_url}{path}", json=payload)
        resp.raise_for_status()
        return resp.json()

    def _delete(self, path: str) -> None:
        resp = self.session.delete(f"{self.base_url}{path}")
        resp.raise_for_status()

    # ------------------------------------------------------------------ #
    # Account & Clock
    # ------------------------------------------------------------------ #

    def get_account(self) -> dict:
        """GET /v2/account"""
        return self._get("/account")

    def get_clock(self) -> dict:
        """GET /v2/clock — returns is_open, next_open, next_close."""
        return self._get("/clock")

    def is_market_open(self) -> bool:
        return self.get_clock().get("is_open", False)

    # ------------------------------------------------------------------ #
    # Positions
    # ------------------------------------------------------------------ #

    def get_positions(self) -> list:
        """GET /v2/positions"""
        return self._get("/positions")

    def get_position(self, symbol: str) -> dict | None:
        """GET /v2/positions/{symbol} — returns None if no open position."""
        try:
            return self._get(f"/positions/{symbol}")
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    def close_position(self, symbol: str) -> dict:
        """DELETE /v2/positions/{symbol}"""
        resp = self.session.delete(f"{self.base_url}/positions/{symbol}")
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------ #
    # Orders
    # ------------------------------------------------------------------ #

    def get_orders(self, status: str = "open") -> list:
        """GET /v2/orders"""
        return self._get("/orders", params={"status": status})

    def place_market_order(self, symbol: str, qty: int, side: str) -> dict:
        """POST /v2/orders — share-quantity market order."""
        payload = {
            "symbol": symbol,
            "qty": str(qty),
            "side": side,
            "type": "market",
            "time_in_force": "day",
        }
        return self._post("/orders", payload)

    def place_notional_order(self, symbol: str, notional: float, side: str) -> dict:
        """POST /v2/orders — dollar-notional market order (fractional shares)."""
        payload = {
            "symbol": symbol,
            "notional": f"{notional:.2f}",
            "side": side,
            "type": "market",
            "time_in_force": "day",
        }
        return self._post("/orders", payload)

    def cancel_order(self, order_id: str) -> None:
        """DELETE /v2/orders/{order_id}"""
        self._delete(f"/orders/{order_id}")

    def cancel_all_orders(self) -> None:
        """DELETE /v2/orders"""
        resp = self.session.delete(f"{self.base_url}/orders")
        resp.raise_for_status()

    # ------------------------------------------------------------------ #
    # Market data — bars
    # ------------------------------------------------------------------ #

    def get_bars(self, symbol: str, timeframe: str = "1Day", limit: int = 50) -> list:
        """GET bars for a single symbol. Returns list sorted oldest → newest."""
        resp = self.session.get(
            f"{DATA_URL}/stocks/{symbol}/bars",
            params={
                "timeframe": timeframe,
                "limit": limit,
                "sort": "asc",
                "feed": "iex",
            },
        )
        resp.raise_for_status()
        return resp.json().get("bars", [])

    # ------------------------------------------------------------------ #
    # Market data — news
    # ------------------------------------------------------------------ #

    def get_news(self, symbol: str, limit: int = 10) -> list:
        """GET /v1beta1/news — recent news articles for a symbol."""
        resp = self.session.get(
            f"{NEWS_URL}/news",
            params={
                "symbols": symbol,
                "limit": limit,
                "sort": "desc",
            },
        )
        resp.raise_for_status()
        data = resp.json()
        # Response shape: {"news": [...]} or directly a list
        if isinstance(data, list):
            return data
        return data.get("news", [])
