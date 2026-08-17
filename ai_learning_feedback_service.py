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


def _calculate_learning_feedback():
    """
    Beregner de aktuelle læringsvægte uden filskrivning.
    """
    weights = {}

    for signal in get_signal_accuracy():
        samples = signal["total"]
        accuracy = signal["accuracy"]

        sample_factor = min(
            samples / 10,
            1.0,
        )

        adjusted_weight = (
            50
            + (
                accuracy - 50
            )
            * sample_factor
        )

        weights[signal["signal"]] = {
            "accuracy": accuracy,
            "samples": samples,
            "adjusted_weight": round(
                adjusted_weight,
                1,
            ),
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
            "AI har begyndende historik, men kræver flere "
            "observationer for mere robuste læringsmønstre."
        )
    else:
        status = "Aktiv læring"
        status_reason = (
            "AI har tilstrækkelig historik til at evaluere "
            "mønstre og forbedre fremtidige vurderinger."
        )

    return {
        "updated_at": datetime.now().isoformat(
            timespec="seconds"
        ),
        "status": status,
        "status_reason": status_reason,
        "total_samples": total_samples,
        "signal_weights": weights,
    }


def _write_learning_feedback(data):
    """
    Gemmer feedback atomisk under en eksklusiv fillås.
    """
    with _open_learning_feedback_lock_file() as lock:
        fcntl.flock(
            lock.fileno(),
            fcntl.LOCK_EX,
        )

        try:
            temp_file = FEEDBACK_FILE.with_suffix(
                FEEDBACK_FILE.suffix
                + ".tmp"
            )

            fd = os.open(
                temp_file,
                (
                    os.O_WRONLY
                    | os.O_CREAT
                    | os.O_TRUNC
                ),
                0o600,
            )

            os.fchmod(
                fd,
                0o600,
            )

            with os.fdopen(
                fd,
                "w",
                encoding="utf-8",
            ) as handle:
                json.dump(
                    data,
                    handle,
                    indent=2,
                    ensure_ascii=False,
                )

                handle.flush()
                os.fsync(
                    handle.fileno()
                )

            temp_file.replace(
                FEEDBACK_FILE
            )

            os.chmod(
                FEEDBACK_FILE,
                0o600,
            )

        finally:
            fcntl.flock(
                lock.fileno(),
                fcntl.LOCK_UN,
            )


def load_learning_feedback():
    """
    Henter senest gemte feedback uden at ændre runtime-data.
    """
    if not FEEDBACK_FILE.exists():
        return None

    try:
        with open(
            FEEDBACK_FILE,
            "r",
            encoding="utf-8",
        ) as handle:
            data = json.load(
                handle
            )

    except (
        OSError,
        json.JSONDecodeError,
    ):
        return None

    if not isinstance(
        data,
        dict,
    ):
        return None

    required_keys = {
        "status",
        "status_reason",
        "total_samples",
        "signal_weights",
    }

    if not required_keys.issubset(
        data
    ):
        return None

    return data


def refresh_learning_feedback():
    """
    Genberegner og gemmer feedback.

    Kaldes af det planlagte dashboard-cachejob.
    """
    data = (
        _calculate_learning_feedback()
    )

    _write_learning_feedback(
        data
    )

    return data


def get_learning_feedback():
    """
    Returnerer feedback uden filskrivning.

    Hvis cachefilen mangler eller er ugyldig, beregnes en
    sikker in-memory fallback uden at ændre runtime-data.
    """
    cached = load_learning_feedback()

    if cached is not None:
        return cached

    return _calculate_learning_feedback()
