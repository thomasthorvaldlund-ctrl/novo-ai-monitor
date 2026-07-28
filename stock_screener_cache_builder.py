import json

import yfinance as yf

from currency_service import (
    get_fx_rates,
    get_currency,
    convert_to_dkk,
)
from stock_universe_service import get_active_stocks
from portfolio_stock_service import get_monitored_stock_map


CACHE_FILE = "/root/novo-ai-monitor/stock_screener_cache.json"


def build_stock_screener_cache():
    watchlist = get_active_stocks()

    portfolio_map = get_monitored_stock_map()

    for stock_name, ticker in portfolio_map.items():
        if ticker not in watchlist.values():
            watchlist[stock_name] = ticker

    fx_rates = get_fx_rates()
    results = []

    for name, ticker in watchlist.items():
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period="10d")
            data = data.dropna(subset=["Close"])

            if data.empty or len(data.index) < 6:
                raise ValueError("Ikke nok gyldige kursdata til beregning")

            latest = float(data["Close"].iloc[-1])
            week_ago = float(data["Close"].iloc[-6])

            currency = get_currency(ticker)
            latest_dkk = convert_to_dkk(latest, currency, fx_rates)
            weekly_change = ((latest - week_ago) / week_ago) * 100

            import math

            if not all(
                math.isfinite(value)
                for value in (latest, week_ago, latest_dkk, weekly_change)
            ):
                raise ValueError("Ugyldige kurs- eller valutadata")

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
                "score": score,
            })

        except Exception as e:
            results.append({
                "stock": name,
                "error": str(e),
            })

    results.sort(
        key=lambda item: item.get("score", 0),
        reverse=True,
    )

    cache_data = {
        "ranking": results,
    }

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(
            cache_data,
            f,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )

    return {
        "status": "ok",
        "stocks": len(results),
        "errors": sum(1 for item in results if "error" in item),
    }
