import yfinance as yf

from currency_service import (
    get_fx_rates,
    get_currency,
    convert_to_dkk,
)
from stock_universe_service import get_active_stocks


def stock_screener():
    watchlist = get_active_stocks()

    fx_rates = get_fx_rates()
    results = []

    for name, ticker in watchlist.items():
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period="10d")

            latest = float(data["Close"].iloc[-1])
            week_ago = float(data["Close"].iloc[-6])

            currency = get_currency(ticker)
            latest_dkk = convert_to_dkk(latest, currency, fx_rates)

            weekly_change = ((latest - week_ago) / week_ago) * 100

            score = 50

            if weekly_change > 5:
                score += 20
            elif weekly_change > 2:
                score += 10

            if weekly_change < -5:
                score -= 20

            results.append({
                "stock": name,
                "price": round(latest_dkk, 2),
                "original_price": round(latest, 2),
                "currency": currency,
                "weekly_change": round(weekly_change, 2),
                "score": score
            })

        except Exception as e:
            results.append({
                "stock": name,
                "error": str(e)
            })

    results = sorted(
        results,
        key=lambda x: x.get("score", 0),
        reverse=True
    )

    return {"ranking": results}