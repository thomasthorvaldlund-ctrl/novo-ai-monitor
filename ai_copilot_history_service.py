import json
from datetime import datetime
from pathlib import Path


HISTORY_FILE = Path("ai_copilot_history.json")


def load_copilot_history():
    """
    Henter tidligere AI Copilot vurderinger.
    """

    if not HISTORY_FILE.exists():
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception:
        return []


def save_copilot_snapshot(copilot_data):
    """
    Gemmer dagens AI Copilot vurdering.
    """

    history = load_copilot_history()

    snapshot = {
        "date": datetime.now().strftime("%d-%m-%Y %H:%M"),
        "headline": copilot_data.get("headline"),
        "best_opportunity": copilot_data.get(
            "best_opportunity"
        ),
        "risk_level": copilot_data.get(
            "risk_level"
        ),
        "confidence": copilot_data.get(
            "confidence"
        ),
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
