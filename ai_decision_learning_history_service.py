import json
import os
from pathlib import Path
from datetime import datetime


HISTORY_FILE = Path("ai_decision_learning_history.json")


def load_learning_history():
    """
    Henter tidligere AI Decision Learning snapshots defensivt.
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


def save_learning_snapshot(data):

    history = load_learning_history()

    snapshot = {
        "date": datetime.now().strftime("%d-%m-%Y %H:%M"),
        **data
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