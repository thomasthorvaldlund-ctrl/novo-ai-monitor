import json
from pathlib import Path


HISTORY_FILE = Path("ai_decision_learning_history.json")


def load_learning_history():

    if not HISTORY_FILE.exists():
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception:
        return []


def get_learning_trend():

    history = load_learning_history()

    if not history:
        return {
            "snapshots": 0,
            "current_accuracy": 0,
            "starting_accuracy": 0,
            "change": 0,
            "trend": "No data",
        }

    first = history[0]
    latest = history[-1]

    starting_accuracy = first.get(
        "accuracy",
        0
    )

    current_accuracy = latest.get(
        "accuracy",
        0
    )

    change = round(
        current_accuracy - starting_accuracy,
        2
    )

    if change > 2:
        trend = "Improving"

    elif change < -2:
        trend = "Declining"

    else:
        trend = "Stable"

    return {
        "snapshots": len(history),
        "current_accuracy": current_accuracy,
        "starting_accuracy": starting_accuracy,
        "change": change,
        "trend": trend,
    }
