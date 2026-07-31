import json
from pathlib import Path
from collections import Counter


HISTORY_FILE = Path("ai_decision_history.json")


def load_decision_history():
    """
    Henter AI beslutningshistorik.
    """

    if not HISTORY_FILE.exists():
        return []

    with open(
        HISTORY_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)



def get_decision_performance():
    """
    Beregner grundlæggende AI Decision statistik.
    """

    history = load_decision_history()

    actions = Counter(
        item.get("action", "UNKNOWN")
        for item in history
    )

    confidence = Counter(
        item.get("confidence", "UNKNOWN")
        for item in history
    )

    return {
        "total_decisions": len(history),
        "buy": actions["BUY"],
        "hold": actions["HOLD"],
        "reduce": actions["REDUCE"],
        "confidence_levels": dict(confidence),
        "status": (
            "For lidt data"
            if len(history) < 10
            else "Klar til analyse"
        ),
    }
