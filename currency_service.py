import yfinance as yf


def get_fx_rates():
    def fx(pair, fallback):
        try:
            data = yf.Ticker(pair).history(period="5d")
            return float(data["Close"].iloc[-1])
        except Exception:
            return fallback

    return {
        "DKK": 1.0,
        "USD": fx("USDDKK=X", 6.95),
        "EUR": fx("EURDKK=X", 7.46),
    }


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
