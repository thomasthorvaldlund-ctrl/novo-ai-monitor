import csv
import os
from datetime import datetime

HISTORY_FILE = "signal_history.csv"


def load_signal_history():
    """Returnerer hele signalhistorikken."""
    if not os.path.exists(HISTORY_FILE):
        return []

    with open(HISTORY_FILE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def get_last_signal(stock):
    """Finder seneste signal for en aktie."""
    history = load_signal_history()

    for row in reversed(history):
        if row["stock"] == stock:
            return row

    return None


def signal_changed(stock, signal):
    """Returnerer True hvis signalet er ændret siden sidst."""
    last = get_last_signal(stock)

    if last is None:
        return True

    return last["signal"] != signal


def save_signal(stock, score, signal, confidence, risk):
    """Gemmer signal hvis det er nyt eller ændret."""

    if not signal_changed(stock, signal):
        return False

    exists = os.path.exists(HISTORY_FILE)

    with open(HISTORY_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not exists or os.path.getsize(HISTORY_FILE) == 0:
            writer.writerow([
                "datetime",
                "stock",
                "score",
                "signal",
                "confidence",
                "risk",
            ])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            stock,
            score,
            signal,
            confidence,
            risk,
        ])

    return True