import os
from dotenv import load_dotenv

load_dotenv()

ALPACA_BASE_URL = "https://paper-api.alpaca.markets/v2"
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")

SYMBOLS = [s.strip() for s in os.getenv("SYMBOLS", "AAPL,TSLA,MSFT").split(",")]
SHORT_MA_PERIOD = int(os.getenv("SHORT_MA_PERIOD", "9"))
LONG_MA_PERIOD = int(os.getenv("LONG_MA_PERIOD", "21"))
TRADE_QTY = int(os.getenv("TRADE_QTY", "1"))
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))
