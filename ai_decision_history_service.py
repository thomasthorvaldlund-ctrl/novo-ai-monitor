import json
import os
from pathlib import Path

from aureum_paths import data_path
from datetime import datetime


HISTORY_FILE = data_path(
    "ai_decision_history.json"
)


def load_decision_history():
    """
    Henter tidligere AI Decision snapshots defensivt.
    """

    if not HISTORY_FILE.exists():
        return []

    try:
        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            data = json.load(f)

        if isinstance(data, list):
            return data

        return []

    except (OSError, json.JSONDecodeError):
        return []


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

    temp_file = HISTORY_FILE.with_suffix(
        HISTORY_FILE.suffix + ".tmp"
    )

    with open(
        temp_file,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            history,
            f,
            indent=2,
            ensure_ascii=False
        )

        f.flush()
        os.fsync(f.fileno())

    temp_file.replace(
        HISTORY_FILE
    )

    return snapshot
