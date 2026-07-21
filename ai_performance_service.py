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

def get_signal_statistics():
    """
    Beregner performance opdelt efter AI signal.
    """

    data = get_ai_performance()

    statistics = {}

    grouped = defaultdict(list)

    for row in data["signals"]:
        grouped[row["signal"]].append(
            row["change_pct"]
        )

    for signal, returns in grouped.items():

        positive = [
            r for r in returns
            if r > 0
        ]

        statistics[signal] = {
            "count": len(returns),
            "average_return": round(
                sum(returns) / len(returns),
                2
            ),
            "positive": len(positive),
            "negative": len(returns) - len(positive),
            "success_rate": round(
                len(positive) / len(returns) * 100,
                1
            ),
        }

    return statistics

def get_time_based_performance():
    """
    Beregner performance efter 1, 3 og 5 dage
    efter et AI signal.
    """

    signals = load_signals()
    prices = load_prices()

    periods = {
        "1d": 1,
        "3d": 3,
        "5d": 5,
    }

    results = []

    for signal in signals:

        stock = signal["stock"]

        if stock not in prices:
            continue

        signal_date = datetime.strptime(
            signal["datetime"][:10],
            "%Y-%m-%d"
        )

        stock_prices = prices[stock]

        start_price = stock_prices.get(
            signal_date.strftime("%Y-%m-%d")
        )

        if start_price is None:
            continue

        row = {
            "stock": stock,
            "date": signal_date.strftime("%Y-%m-%d"),
            "signal": signal["signal"],
            "score": float(signal["score"]),
            "returns": {}
        }

        for label, days in periods.items():

            target_date = (
                signal_date
                .date()
                .toordinal()
                + days
            )

            future_dates = [
                datetime.strptime(d, "%Y-%m-%d").date()
                for d in stock_prices.keys()
                if datetime.strptime(d, "%Y-%m-%d").date().toordinal()
                >= target_date
            ]

            if future_dates:
                closest = min(future_dates)

                price = stock_prices[
                    closest.strftime("%Y-%m-%d")
                ]

                row["returns"][label] = round(
                    ((price - start_price) / start_price) * 100,
                    2
                )

        results.append(row)

    return results

def get_time_based_statistics():
    """
    Samler tidsbaseret performance efter signaltype.
    """

    data = get_time_based_performance()

    statistics = {}

    for row in data:

        signal = row["signal"]

        if signal not in statistics:
            statistics[signal] = {
                "1d": [],
                "3d": [],
                "5d": []
            }

        for period, value in row["returns"].items():
            statistics[signal][period].append(value)

    result = {}

    for signal, periods in statistics.items():

        result[signal] = {}

        for period, values in periods.items():

            if not values:
                continue

            positive = [
                x for x in values
                if x > 0
            ]

            result[signal][period] = {
                "count": len(values),
                "average_return": round(
                    sum(values) / len(values),
                    2
                ),
                "positive": len(positive),
                "negative": len(values) - len(positive),
                "success_rate": round(
                    len(positive) / len(values) * 100,
                    1
                )
            }

    return result

def get_ai_performance_summary():
    """
    Laver en samlet oversigt til dashboard.
    """

    statistics = get_time_based_statistics()

    best_signal = None
    best_period = None
    best_return = None

    for signal, periods in statistics.items():

        for period, data in periods.items():

            avg = data.get(
                "average_return",
                0
            )

            if (
                best_return is None
                or avg > best_return
            ):
                best_return = avg
                best_signal = signal
                best_period = period

    tested_signals = len(
        get_time_based_performance()
    )

    data_quality = "God"
    
    if tested_signals < 100:
        data_quality = "Lav - få evaluerede signaler"

    return {
        "tested_signals": tested_signals,
        "best_signal": best_signal,
        "best_period": best_period,
        "best_return": best_return,
        "data_quality": data_quality,
    }

