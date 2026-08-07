import json
from pathlib import Path
from datetime import datetime


ADAPTIVE_HISTORY_FILE = Path(
    "adaptive_decision_history.json"
)


def load_adaptive_history():
    """
    Henter tidligere adaptive simulationer.
    """

    if not ADAPTIVE_HISTORY_FILE.exists():
        return []

    try:
        with open(
            ADAPTIVE_HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)

    except Exception:
        return []


def save_adaptive_decision(data):
    """
    Gemmer en adaptive simulation.
    """

    history = load_adaptive_history()

    data["timestamp"] = datetime.now().isoformat()

    history.append(data)

    with open(
        ADAPTIVE_HISTORY_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            history,
            f,
            indent=2,
            ensure_ascii=False
        )

    return data
