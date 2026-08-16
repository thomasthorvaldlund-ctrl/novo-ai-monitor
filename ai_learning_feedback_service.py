import fcntl
import json
import os
from datetime import datetime
from pathlib import Path

from aureum_paths import data_path
from ai_signal_accuracy_service import get_signal_accuracy

FEEDBACK_FILE = data_path(
    "ai_learning_feedback.json"
)

LEARNING_FEEDBACK_LOCK_FILE = data_path(
    "ai_learning_feedback.lock"
)


def _open_learning_feedback_lock_file():
    """
    Åbner den persistente lock-fil for Learning Feedback.

    Lock-filen indeholder ingen data. Den koordinerer kun
    samtidige atomiske writes til feedback-filen.
    """
    LEARNING_FEEDBACK_LOCK_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fd = os.open(
        LEARNING_FEEDBACK_LOCK_FILE,
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


def get_learning_feedback():
    """
    Beregner og gemmer AI'ens aktuelle læringsvægte.
    """

    weights = {}

    for signal in get_signal_accuracy():
        samples = signal["total"]
        accuracy = signal["accuracy"]

        sample_factor = min(samples / 10, 1.0)
        adjusted_weight = 50 + ((accuracy - 50) * sample_factor)

        weights[signal["signal"]] = {
            "accuracy": accuracy,
            "samples": samples,
            "adjusted_weight": round(adjusted_weight, 1),
        }

    total_samples = sum(
        item["samples"]
        for item in weights.values()
    )

    if total_samples < 5:
        status = "For lidt data"
        status_reason = (
            "AI har endnu for få historiske observationer "
            "til at identificere stabile mønstre."
        )
    elif total_samples < 20:
        status = "Begrænset datagrundlag"
        status_reason = (
            "AI har begyndende historik, men kræver flere observationer "
            "for mere robuste læringsmønstre."
        )
    else:
        status = "Aktiv læring"
        status_reason = (
            "AI har tilstrækkelig historik til at evaluere mønstre "
            "og forbedre fremtidige vurderinger."
        )

    data = {
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "status_reason": status_reason,
        "total_samples": total_samples,
        "signal_weights": weights,
    }

    with _open_learning_feedback_lock_file() as lock:
        fcntl.flock(
            lock.fileno(),
            fcntl.LOCK_EX,
        )

        try:
            temp_file = FEEDBACK_FILE.with_suffix(
                FEEDBACK_FILE.suffix + ".tmp"
            )

            with open(
                temp_file,
                "w",
                encoding="utf-8"
            ) as f:
                json.dump(
                    data,
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

                f.flush()
                os.fsync(f.fileno())

            temp_file.replace(
                FEEDBACK_FILE
            )

        finally:
            fcntl.flock(
                lock.fileno(),
                fcntl.LOCK_UN,
            )

    return data
