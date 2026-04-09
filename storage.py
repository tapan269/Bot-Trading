"""
Local SQLite storage for bot activity.

Tables:
  signals            — every signal computed per poll cycle
  orders             — every order placed
  portfolio_snapshots — account state captured at startup and each cycle
"""

import sqlite3
from datetime import datetime, timezone

from config import DB_PATH


class LocalStorage:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    # ------------------------------------------------------------------ #
    # Setup
    # ------------------------------------------------------------------ #

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS signals (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts        TEXT    NOT NULL,
                    symbol    TEXT    NOT NULL,
                    signal    TEXT    NOT NULL,
                    short_ma  REAL,
                    long_ma   REAL
                );
                CREATE TABLE IF NOT EXISTS orders (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts        TEXT    NOT NULL,
                    symbol    TEXT    NOT NULL,
                    side      TEXT    NOT NULL,
                    qty       INTEGER NOT NULL,
                    order_id  TEXT
                );
                CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts              TEXT    NOT NULL,
                    buying_power    REAL,
                    portfolio_value REAL
                );
            """)

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    # ------------------------------------------------------------------ #
    # Writers
    # ------------------------------------------------------------------ #

    def save_signal(
        self,
        symbol: str,
        signal: str,
        short_ma: float | None = None,
        long_ma: float | None = None,
    ) -> None:
        ts = _now()
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO signals (ts, symbol, signal, short_ma, long_ma)"
                " VALUES (?, ?, ?, ?, ?)",
                (ts, symbol, signal, short_ma, long_ma),
            )

    def save_order(
        self,
        symbol: str,
        side: str,
        qty: int,
        order_id: str | None = None,
    ) -> None:
        ts = _now()
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO orders (ts, symbol, side, qty, order_id)"
                " VALUES (?, ?, ?, ?, ?)",
                (ts, symbol, side, qty, order_id),
            )

    def save_portfolio_snapshot(
        self,
        buying_power: float,
        portfolio_value: float,
    ) -> None:
        ts = _now()
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO portfolio_snapshots (ts, buying_power, portfolio_value)"
                " VALUES (?, ?, ?)",
                (ts, buying_power, portfolio_value),
            )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
