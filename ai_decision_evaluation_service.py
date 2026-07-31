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
            ticker = item.get("ticker")

            if not ticker:
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

            decision = item.get("action")

            if decision == "BUY":
                correct = change_pct > 0

            elif decision == "HOLD":
                correct = change_pct >= -2

            elif decision == "REDUCE":
                correct = change_pct <= 0

            else:
                correct = False

            results.append({
                "date": item.get("date"),
                "stock": stock,
                "decision": decision,
                "start_price": start_price,
                "current_price": current_price,
                "change_pct": round(change_pct, 2),
                "correct": correct,
                "performance": (
                    "God"
                    if correct
                    else "Dårlig"
                ),
            })

        except Exception:
            continue

    return results

def get_decision_accuracy():

    results = evaluate_decisions()

    if not results:
        return {
            "total_decisions": 0,
            "correct": 0,
            "wrong": 0,
            "accuracy": 0,
            "by_decision": {},
        }

    total = len(results)

    correct = sum(
        1
        for item in results
        if item.get("correct")
    )

    wrong = total - correct

    accuracy = round(
        (correct / total) * 100,
        2
    )

    by_decision = {}

    for item in results:
        decision = item.get("decision", "UNKNOWN")

        if decision not in by_decision:
            by_decision[decision] = {
                "total": 0,
                "correct": 0,
            }

        by_decision[decision]["total"] += 1

        if item.get("correct"):
            by_decision[decision]["correct"] += 1

    for decision, data in by_decision.items():
        data["accuracy"] = round(
            (data["correct"] / data["total"]) * 100,
            2
        )

    return {
        "total_decisions": total,
        "correct": correct,
        "wrong": wrong,
        "accuracy": accuracy,
        "by_decision": by_decision,
    }

