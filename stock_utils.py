import time

from market_data_provider import get_history as provider_get_history

_STOCK_CACHE = {}
CACHE_SECONDS = 300

def get_history(ticker, period="10d"):
    key = f"{ticker}:{period}"
    now = time.time()

    if key in _STOCK_CACHE:
        cached = _STOCK_CACHE[key]
        if now - cached["timestamp"] < CACHE_SECONDS:
            return cached["data"]

    data = provider_get_history(
        ticker,
        period=period,
    )

    _STOCK_CACHE[key] = {
        "timestamp": now,
        "data": data
    }

    return data
