import os
from dotenv import load_dotenv

load_dotenv()

# ── Alpaca API ─────────────────────────────────────────────────────────────
ALPACA_BASE_URL = "https://paper-api.alpaca.markets/v2"
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")

# ── Legacy simple-bot settings (kept for backwards compat) ─────────────────
SYMBOLS = [s.strip() for s in os.getenv("SYMBOLS", "AAPL,TSLA,MSFT").split(",")]
SHORT_MA_PERIOD = int(os.getenv("SHORT_MA_PERIOD", "9"))
LONG_MA_PERIOD = int(os.getenv("LONG_MA_PERIOD", "21"))
TRADE_QTY = int(os.getenv("TRADE_QTY", "1"))
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))

# ── SP500 strategy settings ────────────────────────────────────────────────
REBALANCE_INTERVAL_SECONDS = int(os.getenv("REBALANCE_INTERVAL_SECONDS", "7200"))  # 2 hours
TOP_N = int(os.getenv("TOP_N", "20"))
SELL_RANK_THRESHOLD = int(os.getenv("SELL_RANK_THRESHOLD", "30"))
PORTFOLIO_CASH_BUFFER = float(os.getenv("PORTFOLIO_CASH_BUFFER", "0.05"))

# ── Signal weights (must sum to 1.0) ──────────────────────────────────────
SIGNAL_WEIGHT_MA = float(os.getenv("SIGNAL_WEIGHT_MA", "0.40"))
SIGNAL_WEIGHT_SENTIMENT = float(os.getenv("SIGNAL_WEIGHT_SENTIMENT", "0.30"))
SIGNAL_WEIGHT_VOLUME = float(os.getenv("SIGNAL_WEIGHT_VOLUME", "0.30"))

# ── Hierarchy & sell thresholds ───────────────────────────────────────────
SECTOR_WEIGHT = float(os.getenv("SECTOR_WEIGHT", "0.40"))
MA_REVERSAL_THRESHOLD = float(os.getenv("MA_REVERSAL_THRESHOLD", "0.2"))
