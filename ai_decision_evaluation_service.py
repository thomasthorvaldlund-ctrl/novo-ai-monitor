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

            valid = abs(change_pct) <= 50

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
                "valid": valid,
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

def get_decision_quality():

    results = evaluate_decisions()

    if not results:
        return {
            "total_decisions": 0,
            "valid_decisions": 0,
            "filtered_out": 0,
            "raw_accuracy": 0,
            "good_decisions": 0,
            "bad_decisions": 0,
            "quality_accuracy": 0,
        }

    total_decisions = len(results)

    valid_results = [
        item
        for item in results
        if item.get("valid")
    ]

    valid_decisions = len(valid_results)

    filtered_out = (
        total_decisions
        - valid_decisions
    )

    correct_raw = sum(
        1
        for item in results
        if item.get("correct")
    )

    raw_accuracy = round(
        (correct_raw / total_decisions) * 100,
        2
    )

    good_decisions = sum(
        1
        for item in valid_results
        if item.get("correct")
    )

    bad_decisions = (
        valid_decisions
        - good_decisions
    )

    if valid_decisions:
        quality_accuracy = round(
            (good_decisions / valid_decisions) * 100,
            2
        )
    else:
        quality_accuracy = 0

    return {
        "total_decisions": total_decisions,
        "valid_decisions": valid_decisions,
        "filtered_out": filtered_out,
        "raw_accuracy": raw_accuracy,
        "good_decisions": good_decisions,
        "bad_decisions": bad_decisions,
        "quality_accuracy": quality_accuracy,
    }

