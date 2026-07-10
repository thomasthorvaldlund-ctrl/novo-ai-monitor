from collections import Counter

from signal_history_service import load_signal_history


def get_signal_statistics():
    """
    Returnerer statistik over AI-signaler.
    """

    history = load_signal_history()
    signals = Counter(row["signal"] for row in history)

    return {
        "total": len(history),
        "buy": signals["BUY"],
        "hold": signals["HOLD"],
        "watch": signals["WATCH"],
        "sell": signals["SELL"],
    }