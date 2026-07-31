import json
from pathlib import Path

from stock_utils import get_history
from stock_universe_service import get_stock_metadata


HISTORY_FILE = Path("ai_decision_history.json")


def load_decision_history():
    if not HISTORY_FILE.exists():
        return []

    with open(
        HISTORY_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)



def evaluate_decisions():

    history = load_decision_history()

    results = []

    for item in history:

        stock = item.get("stock")
        start_price = item.get("price")

        if not stock or not start_price:
            continue

        try:
            metadata = get_stock_metadata(stock)

            if not metadata:
                continue

            ticker = metadata.get("ticker")

            if not ticker:
                continue

            data = get_history(
                ticker,
                period="10d"
            )

            current_price = float(
                data["Close"].iloc[-1]
            )

            change_pct = (
                (current_price - start_price)
                / start_price
                * 100
            )

            results.append({
                "date": item.get("date"),
                "stock": stock,
                "decision": item.get("action"),
                "start_price": start_price,
                "current_price": current_price,
                "change_pct": round(
                    change_pct,
                    2
                ),
            })

        except Exception:
            continue

    return results
