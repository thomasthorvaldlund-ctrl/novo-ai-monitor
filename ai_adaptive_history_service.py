import fcntl
import json
import os
from pathlib import Path
from datetime import datetime

from aureum_paths import data_path


ADAPTIVE_HISTORY_FILE = data_path(
    "adaptive_decision_history.json"
)

ADAPTIVE_HISTORY_LOCK_FILE = data_path(
    "adaptive_decision_history.lock"
)


def _open_adaptive_history_lock_file():
    """
    Åbner den persistente lock-fil for adaptive historik.

    Lock-filen indeholder ingen data. Den bruges kun til
    proces- og thread-sikker koordinering af writes.
    """
    ADAPTIVE_HISTORY_LOCK_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fd = os.open(
        ADAPTIVE_HISTORY_LOCK_FILE,
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
    Gemmer en adaptive simulation concurrency-sikkert.
    """
    with _open_adaptive_history_lock_file() as lock:
        fcntl.flock(
            lock.fileno(),
            fcntl.LOCK_EX,
        )

        try:
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

        finally:
            fcntl.flock(
                lock.fileno(),
                fcntl.LOCK_UN,
            )
