import json
import os
from pathlib import Path
from datetime import datetime


ADAPTIVE_HISTORY_FILE = Path(
    "adaptive_decision_history.json"
)


def load_adaptive_history():
    """
    Henter tidligere adaptive simulationer defensivt.
    """

    if not ADAPTIVE_HISTORY_FILE.exists():
        return []

    try:
        with open(
            ADAPTIVE_HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            data = json.load(f)

        if isinstance(data, list):
            return data

        return []

    except (OSError, json.JSONDecodeError):
        return []


def save_adaptive_decision(data):
    """
    Gemmer en adaptive simulation.
    """

    history = load_adaptive_history()

    data["timestamp"] = datetime.now().isoformat()

    history.append(data)

    temp_file = ADAPTIVE_HISTORY_FILE.with_suffix(
        ADAPTIVE_HISTORY_FILE.suffix + ".tmp"
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
        ADAPTIVE_HISTORY_FILE
    )

    return data
