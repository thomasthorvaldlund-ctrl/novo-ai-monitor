from flask import Blueprint
import yfinance as yf

market_dashboard_bp = Blueprint("market_dashboard", __name__)

@market_dashboard_bp.route("/market-dashboard")
def market_dashboard():
    markets = {
        "S&P 500": "^GSPC",
        "Nasdaq": "^IXIC",
        "OMXC25": "^OMXC25",
        "DAX": "^GDAXI"
    }

    results = []
    positive = 0

    for name, ticker in markets.items():
        try:
            data = yf.Ticker(ticker).history(period="5d")
            latest = float(data["Close"].iloc[-1])
            previous = float(data["Close"].iloc[-2])
            change = ((latest - previous) / previous) * 100

            if change > 0:
                positive += 1

            results.append({
                "market": name,
                "price": round(latest, 2),
                "change": round(change, 2)
            })

        except Exception as e:
            results.append({
                "market": name,
                "error": str(e)
            })

    if positive >= 3:
        signal = "Bullish"
        color = "green"
    elif positive == 2:
        signal = "Neutral"
        color = "orange"
    else:
        signal = "Bearish"
        color = "red"

    return "OK"