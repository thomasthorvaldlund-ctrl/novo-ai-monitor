from ai_confidence_intelligence_service import get_confidence_intelligence
from ai_portfolio_confidence_calibration_service import get_confidence_calibration


def get_ai_data_quality():

    confidence = get_confidence_intelligence()
    calibration = get_confidence_calibration()

    decisions = calibration.get(
        "decisions",
        0
    )

    samples = calibration.get(
        "samples",
        0
    )

    if samples < 10:
        quality = "Begrænset"
    elif decisions < 50:
        quality = "Under opbygning"
    else:
        quality = "God"

    return {
        "title": "AI Datagrundlag",

        "historical_decisions":
            decisions,

        "validated_samples":
            samples,

        "confidence":
            confidence.get(
                "overall_confidence",
                "Ukendt"
            ),

        "calibration_status":
            calibration.get(
                "status",
                "Ukendt"
            ),

        "data_quality":
            quality,

        "reason":
            calibration.get(
                "reason",
                ""
            )
    }