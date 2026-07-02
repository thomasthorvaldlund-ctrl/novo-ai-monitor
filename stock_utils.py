import time
import yfinance as yf

_STOCK_CACHE = {}
CACHE_SECONDS = 300

def get_history(ticker, period="10d"):
    key = f"{ticker}:{period}"
    now = time.time()

    if key in _STOCK_CACHE:
        cached = _STOCK_CACHE[key]
        if now - cached["timestamp"] < CACHE_SECONDS:
            return cached["data"]

    data = yf.Ticker(ticker).history(period=period)

    _STOCK_CACHE[key] = {
        "timestamp": now,
        "data": data
    }

    return data
