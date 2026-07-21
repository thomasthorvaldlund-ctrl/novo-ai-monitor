import csv
from datetime import datetime
from collections import defaultdict


SIGNAL_FILE = "signal_history.csv"
PRICE_FILE = "history.csv"


def load_signals():
    with open(
        SIGNAL_FILE,
        newline="",
        encoding="utf-8"
    ) as f:
        return list(csv.DictReader(f))


def load_prices():
    prices = defaultdict(dict)

    with open(
        PRICE_FILE,
        newline="",
        encoding="utf-8"
    ) as f:
        for row in csv.DictReader(f):
            prices[row["stock"]][row["date"]] = float(row["price"])

    return prices


def get_ai_performance():
    """
    Evaluerer AI signaler mod seneste tilgængelige kursdata.
    """

    signals = load_signals()
    prices = load_prices()

    results = []

    for signal in signals:

        stock = signal["stock"]

        if stock not in prices:
            continue

        signal_date = signal["datetime"][:10]

        stock_prices = prices[stock]

        if signal_date not in stock_prices:
            continue

        start_price = stock_prices[signal_date]

        latest_date = max(stock_prices.keys())
        latest_price = stock_prices[latest_date]

        change_pct = (
            (latest_price - start_price)
            / start_price
        ) * 100

        results.append({
            "stock": stock,
            "date": signal_date,
            "signal": signal["signal"],
            "score": float(signal["score"]),
            "confidence": int(signal["confidence"]),
            "start_price": start_price,
            "latest_price": latest_price,
            "change_pct": round(change_pct, 2),
        })


    summary = {
        "total_signals": len(signals),
        "evaluated_signals": len(results),
        "stocks": sorted(
            list(
                set(
                    r["stock"]
                    for r in results
                )
            )
        ),
        "signals": results,
    }

    return summary