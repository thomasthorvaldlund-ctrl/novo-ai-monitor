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

    FEEDBACK_FILE.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8",
    )

    return data
