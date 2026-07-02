import time
import yfinance as yf

_FX_CACHE = {
    "timestamp": 0,
    "rates": None,
}

def get_fx_rates():
    now = time.time()

    if _FX_CACHE["rates"] is not None and now - _FX_CACHE["timestamp"] < 1800:
        return _FX_CACHE["rates"]

    def fx(pair, fallback):
        try:
            data = yf.Ticker(pair).history(period="5d")
            return float(data["Close"].iloc[-1])
        except Exception:
            return fallback

    rates = {
        "DKK": 1.0,
        "USD": fx("USDDKK=X", 6.95),
        "EUR": fx("EURDKK=X", 7.46),
    }

    _FX_CACHE["timestamp"] = now
    _FX_CACHE["rates"] = rates

    return rates

def get_currency(ticker):
    if ticker.endswith(".CO"):
        return "DKK"
    if ticker.endswith(".AS"):
        return "EUR"
    return "USD"

def convert_to_dkk(price, currency, fx_rates=None):
    if fx_rates is None:
        fx_rates = get_fx_rates()
    return float(price) * fx_rates.get(currency, 1.0)

def format_dkk(amount):
    return f"{amount:,.2f} DKK".replace(",", "X").replace(".", ",").replace("X", ".")
