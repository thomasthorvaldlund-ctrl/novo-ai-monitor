import fcntl
import json
import os
from pathlib import Path
from datetime import datetime

from aureum_paths import data_path


HISTORY_FILE = data_path(
    "ai_maturity_history.json"
)

MATURITY_HISTORY_LOCK_FILE = data_path(
    "ai_maturity_history.lock"
)


def _open_maturity_history_lock_file():
    """
    Åbner den persistente lock-fil for AI Maturity History.

    Lock-filen indeholder ingen data. Den bruges kun til
    proces- og thread-sikker koordinering af writes.
    """
    MATURITY_HISTORY_LOCK_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fd = os.open(
        MATURITY_HISTORY_LOCK_FILE,
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

    with _open_maturity_history_lock_file() as lock:
        fcntl.flock(
            lock.fileno(),
            fcntl.LOCK_EX,
        )

        try:
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

        finally:
            fcntl.flock(
                lock.fileno(),
                fcntl.LOCK_UN,
            )
