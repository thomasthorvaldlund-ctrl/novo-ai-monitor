import fcntl
import json
import os
from datetime import datetime

from aureum_paths import data_path


HISTORY_FILE = data_path(
    "ai_copilot_history.json"
)

COPILOT_HISTORY_LOCK_FILE = data_path(
    "ai_copilot_history.lock"
)


def _open_copilot_history_lock_file():
    """
    Åbner den persistente lock-fil for AI Copilot History.

    Lock-filen indeholder ingen data. Den bruges kun til
    proces- og thread-sikker koordinering af writes.
    """
    COPILOT_HISTORY_LOCK_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fd = os.open(
        COPILOT_HISTORY_LOCK_FILE,
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


def load_copilot_history():
    """
    Henter tidligere AI Copilot vurderinger defensivt.
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


def save_copilot_snapshot(copilot_data, changes=None):
    """
    Gemmer dagens AI Copilot vurdering.
    """

    with _open_copilot_history_lock_file() as lock:
        fcntl.flock(
            lock.fileno(),
            fcntl.LOCK_EX,
        )

        try:
            history = load_copilot_history()

            snapshot = {
                "date": datetime.now().strftime("%d-%m-%Y %H:%M"),
                "headline": copilot_data.get("headline"),
                "best_opportunity": copilot_data.get(
                    "best_opportunity"
                ),
                "risk_level": copilot_data.get(
                    "risk_level"
                ),
                "confidence": copilot_data.get(
                    "confidence"
                ),
                "risk_score": copilot_data.get(
                    "risk_score",
                    0
                ),
                "overall_risk": copilot_data.get(
                    "overall_risk"
                ),
                "risk_reasons": copilot_data.get(
                    "risk_reasons",
                    []
                ),
                "status": (
                    changes.get("status")
                    if changes
                    else "neutral"
                ),
                "changes": (
                    changes.get("changes", [])
                    if changes
                    else []
                ),
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
