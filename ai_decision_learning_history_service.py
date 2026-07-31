import json
from pathlib import Path
from datetime import datetime


HISTORY_FILE = Path("ai_decision_learning_history.json")


def load_learning_history():
    if not HISTORY_FILE.exists():
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception:
        return []


def save_learning_snapshot(data):

    history = load_learning_history()

    snapshot = {
        "date": datetime.now().strftime("%d-%m-%Y %H:%M"),
        **data
    }

    history.append(snapshot)

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(
            history,
            f,
            indent=2,
            ensure_ascii=False
        )

    return snapshot