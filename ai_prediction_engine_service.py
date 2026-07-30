from ai_signal_accuracy_service import get_signal_accuracy
from ai_confidence_calibration_service import get_confidence_calibration


def get_prediction_engine():
    """
    Estimerer AI'ens forventede succesrate baseret på historiske resultater.
    """

    signals = get_signal_accuracy()
    calibration = get_confidence_calibration()

    if signals:
        expected_accuracy = sum(s["accuracy"] for s in signals) / len(signals)
    else:
        expected_accuracy = 0.0

    best_signal = None
    if signals:
        best_signal = max(signals, key=lambda s: s["accuracy"])

    best_confidence = max(
        calibration.items(),
        key=lambda item: item[1]["accuracy_pct"],
        default=None,
    )

    total_predictions = sum(signal["total"] for signal in signals)

    if total_predictions < 5:
        reliability_status = "For lidt data"
        reliability_message = (
            "Prognosen er foreløbig og bygger på færre end 5 historiske beslutninger."
        )
    elif total_predictions < 20:
        reliability_status = "Begrænset datagrundlag"
        reliability_message = (
            "Prognosen bør tolkes forsigtigt, indtil der er mere historik."
        )
    else:
        reliability_status = "Tilstrækkeligt datagrundlag"
        reliability_message = (
            "Prognosen bygger på et mere robust historisk datagrundlag."
        )

    return {
        "headline": "AI Prediction Engine",
        "expected_accuracy": round(expected_accuracy, 1),
        "best_signal": best_signal,
        "best_confidence": best_confidence,
        "total_predictions": total_predictions,
        "reliability_status": reliability_status,
        "reliability_message": reliability_message,
    }
