import json
import os
from pathlib import Path
from datetime import datetime

from aureum_paths import data_path


HISTORY_FILE = data_path(
    "ai_maturity_history.json"
)


def load_ai_maturity_history():
    """
    Henter historik for AI Maturity defensivt.
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


def save_ai_maturity_snapshot(maturity_data):
    """
    Gemmer et AI Maturity snapshot.
    """

    history = load_ai_maturity_history()

    snapshot = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "score": maturity_data.get("score", 0),
        "level": maturity_data.get("level", ""),
        "adaptation": maturity_data.get(
            "components",
            {}
        ).get("adaptation", 0),
        "learning_activity": maturity_data.get(
            "components",
            {}
        ).get("learning_activity", 0),
        "data_quality": maturity_data.get(
            "components",
            {}
        ).get("data_quality", 0),
        "explanation_confidence": maturity_data.get(
            "components",
            {}
        ).get("explanation_confidence", 0),

        "components": maturity_data.get(
            "components",
            {}
        ),
    }

    # Undgå flere snapshots samme dag
    if history and history[-1].get("date") == snapshot["date"]:
        history[-1] = snapshot
    else:
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
