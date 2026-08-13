from collections import Counter

from signal_history_service import get_latest_signals
from stock_universe_service import get_active_stocks


def get_signal_statistics():
    """
    Returnerer den aktuelle signalfordeling.

    Hver aktie medregnes kun én gang ud fra dens seneste
    registrerede signal.
    """
    active_stocks = set(get_active_stocks())

    latest_signals = {
        stock: row
        for stock, row in get_latest_signals().items()
        if stock in active_stocks
    }

    rows = list(latest_signals.values())

    signals = Counter(
        row.get("signal")
        for row in rows
        if row.get("signal")
    )

    stocks_by_signal = {
        "BUY": [],
        "HOLD": [],
        "WATCH": [],
        "SELL": [],
    }

    for stock, row in latest_signals.items():
        signal = row.get("signal")

        if signal in stocks_by_signal:
            stocks_by_signal[signal].append(stock)

    for stocks in stocks_by_signal.values():
        stocks.sort()

    return {
        "total": len(rows),
        "buy": signals["BUY"],
        "hold": signals["HOLD"],
        "watch": signals["WATCH"],
        "sell": signals["SELL"],
        "buy_stocks": stocks_by_signal["BUY"],
        "hold_stocks": stocks_by_signal["HOLD"],
        "watch_stocks": stocks_by_signal["WATCH"],
        "sell_stocks": stocks_by_signal["SELL"],
    }
