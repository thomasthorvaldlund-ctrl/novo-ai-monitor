import json
from datetime import datetime
from pathlib import Path

from ai_signal_accuracy_service import get_signal_accuracy

FEEDBACK_FILE = Path("ai_learning_feedback.json")


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
    elif total_samples < 20:
        status = "Begrænset datagrundlag"
    else:
        status = "Aktiv læring"

    data = {
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "total_samples": total_samples,
        "signal_weights": weights,
    }

    FEEDBACK_FILE.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8",
    )

    return data
