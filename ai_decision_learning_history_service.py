import fcntl
import json
import os
from pathlib import Path
from datetime import datetime

from aureum_paths import data_path


HISTORY_FILE = data_path(
    "ai_decision_learning_history.json"
)

DECISION_LEARNING_HISTORY_LOCK_FILE = data_path(
    "ai_decision_learning_history.lock"
)


def _open_decision_learning_history_lock_file():
    """
    Åbner den persistente lock-fil for
    AI Decision Learning History.

    Lock-filen indeholder ingen data. Den bruges kun til
    proces- og thread-sikker koordinering af writes.
    """
    DECISION_LEARNING_HISTORY_LOCK_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fd = os.open(
        DECISION_LEARNING_HISTORY_LOCK_FILE,
        os.O_RDWR | os.O_CREAT,
        0o600,
    )

    os.fchmod(
        fd,
        0o600,
    )

    return os.fdopen(
        fd,
        "a+",
        encoding="utf-8",
    )


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

    with _open_decision_learning_history_lock_file() as lock:
        fcntl.flock(
            lock.fileno(),
            fcntl.LOCK_EX,
        )

        try:
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

        finally:
            fcntl.flock(
                lock.fileno(),
                fcntl.LOCK_UN,
            )
