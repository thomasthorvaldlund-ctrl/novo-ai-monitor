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
        "stock": decision.get("stock"),
        "ticker": decision.get("ticker"),
        "currency": decision.get("currency"),
        "price": decision.get("price"),
        "score": decision.get("score"),
        "rating": decision.get("rating"),
        "action": decision.get("action"),
        "priority": decision.get("priority"),
        "risk": decision.get("risk"),

        # Backward compatibility:
        "confidence": decision.get("confidence"),

        # Explicit confidence fields:
        "decision_confidence": decision.get(
            "decision_confidence"
        ),
        "context_confidence": decision.get(
            "context_confidence"
        ),

        "global_market_score": decision.get(
            "global_market_score"
        ),

        "global_market_status": decision.get(
            "global_market_score",
            {}
        ).get(
            "status"
        ),

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
