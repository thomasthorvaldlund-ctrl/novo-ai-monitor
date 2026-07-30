import json
from datetime import datetime
from pathlib import Path

from ai_learning_timeline_service import get_learning_timeline

HISTORY_FILE = Path("ai_learning_history.json")


def load_learning_history():
    """
    Indlæser historikken for AI Learning Timeline.
    """
    if not HISTORY_FILE.exists():
        return []

    try:
        return json.loads(HISTORY_FILE.read_text())
    except Exception:
        return []


def save_learning_snapshot():
    """
    Gemmer et snapshot af Learning Timeline.
    """
    history = load_learning_history()

    timeline = get_learning_timeline()

    history.append({
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "accuracy": timeline["last_7_days"],
        "trend": timeline["trend"],
    })

    HISTORY_FILE.write_text(json.dumps(history, indent=2))

    return history
