import json
from datetime import datetime
from pathlib import Path

from ai_portfolio_analytics_service import get_portfolio_analytics


HISTORY_FILE = Path("ai_learning_history.json")


def load_learning_history():
    """
    Indlæser historikken for AI Learning Timeline.
    """
    if not HISTORY_FILE.exists():
        return []

    try:
        data = json.loads(HISTORY_FILE.read_text())

        if isinstance(data, list):
            return data

        return []
    except (OSError, json.JSONDecodeError):
        return []


def save_learning_snapshot():
    """
    Gemmer et snapshot af den aktuelle AI-accuracy.
    """
    history = load_learning_history()
    analytics = get_portfolio_analytics()

    snapshot = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "accuracy": analytics.get("accuracy_pct", 0.0),
    }

    history.append(snapshot)

    HISTORY_FILE.write_text(
        json.dumps(history, indent=2),
        encoding="utf-8",
    )

    return history
