import json
import os
from aureum_paths import data_path
from datetime import datetime


HISTORY_FILE = data_path(
    "ai_portfolio_learning_history.json"
)


def load_learning_history():
    """
    Henter Portfolio Learning History defensivt.
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


def save_learning_snapshot(learning):

    history = load_learning_history()

    snapshot = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "cases": learning.get("cases_analyzed", 0),
        "strongest_signal": learning.get("strongest_signal"),
        "confidence": learning.get("confidence"),
        "score": learning.get("strongest_signal_score")
    }


    if history:

        last = history[-1]

        if (
            last.get("cases") == snapshot["cases"]
            and last.get("strongest_signal") == snapshot["strongest_signal"]
            and last.get("confidence") == snapshot["confidence"]
            and last.get("score") == snapshot["score"]
        ):
            return last



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

def get_learning_history():

    return load_learning_history()
