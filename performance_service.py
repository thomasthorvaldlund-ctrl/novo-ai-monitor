from collections import Counter

from signal_history_service import load_signal_history


def get_signal_statistics():
    """
    Returnerer statistik over AI-signaler.
    """
    history = load_signal_history()
    signals = Counter(row["signal"] for row in history)
    
    excluded_stocks = {
        "TEST",
        "TEST2",
        "TEST_TELEGRAM",
    }

    stocks_by_signal = {
        "BUY": [],
        "HOLD": [],
        "WATCH": [],
        "SELL": [],
    }

    for row in history:
        signal = row["signal"]
        stock = row.get("stock") or row.get("ticker")

        if (
            signal in stocks_by_signal
            and stock
            and stock not in excluded_stocks
            and stock not in stocks_by_signal[signal]
        ):
            stocks_by_signal[signal].append(stock)

    return {
        "total": len(history),
        "buy": signals["BUY"],
        "hold": signals["HOLD"],
        "watch": signals["WATCH"],
        "sell": signals["SELL"],
        "buy_stocks": stocks_by_signal["BUY"],
        "hold_stocks": stocks_by_signal["HOLD"],
        "watch_stocks": stocks_by_signal["WATCH"],
        "sell_stocks": stocks_by_signal["SELL"],
    }
    