import json
from pathlib import Path
from datetime import datetime


HISTORY_FILE = Path("ai_portfolio_learning_history.json")


def load_learning_history():

    if not HISTORY_FILE.exists():
        return []

    with open(HISTORY_FILE) as f:
        return json.load(f)

def save_learning_snapshot(learning):

    history = load_learning_history()

    snapshot = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "cases": learning.get("cases_analyzed", 0),
        "strongest_signal": learning.get("strongest_signal"),
        "confidence": learning.get("confidence"),
        "score": learning.get("strongest_signal_score")
    }


    if history:

        last = history[-1]

        if (
            last.get("cases") == snapshot["cases"]
            and last.get("strongest_signal") == snapshot["strongest_signal"]
            and last.get("confidence") == snapshot["confidence"]
            and last.get("score") == snapshot["score"]
        ):
            return last



    history.append(snapshot)


    with open(HISTORY_FILE, "w") as f:
        json.dump(
            history,
            f,
            indent=2,
            ensure_ascii=False
        )


    return snapshot

def get_learning_history():

    return load_learning_history()
