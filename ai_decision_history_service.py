import json
from pathlib import Path
from datetime import datetime


HISTORY_FILE = Path("ai_decision_history.json")


def load_decision_history():
    """
    Henter tidligere AI Decision snapshots.
    """

    if not HISTORY_FILE.exists():
        return []

    with open(
        HISTORY_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)



def save_decision_snapshot(decision):
    """
    Gemmer en ny AI Decision snapshot.
    """

    history = load_decision_history()

    snapshot = {
        "date": datetime.now().strftime(
            "%d-%m-%Y %H:%M"
        ),
        "action": decision.get("action"),
        "priority": decision.get("priority"),
        "risk": decision.get("risk"),
        "confidence": decision.get("confidence"),
        "recommendation": decision.get("recommendation"),
        "best_opportunity": decision.get("best_opportunity"),
        "reasons": decision.get("reasons", []),
    }

    history.append(snapshot)

    with open(
        HISTORY_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            history,
            f,
            indent=2,
            ensure_ascii=False
        )

    return snapshot
