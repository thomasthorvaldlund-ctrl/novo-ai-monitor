from ai_context_engine_service import get_ai_context
from ai_decision_performance_service import get_decision_performance
from ai_learning_feedback_service import get_learning_feedback


def get_confidence_calibration():

    context = get_ai_context()
    performance = get_decision_performance()
    feedback = get_learning_feedback()

    confidence = context.get("confidence", "Unknown")
    samples = feedback.get("total_samples", 0)
    decisions = performance.get("total_decisions", 0)

    if samples < 10:
        calibrated = "Low"
        status = "Konservativ"
        reason = (
            "AI har endnu for få historiske observationer "
            "til at øge confidence."
        )

    elif decisions < 50:
        calibrated = confidence
        status = "Under opbygning"
        reason = (
            "AI har begyndende historik, men datagrundlaget "
            "er stadig begrænset."
        )

    else:
        calibrated = confidence
        status = "Kalibreret"
        reason = (
            "AI confidence understøttes af et større historisk "
            "beslutningsgrundlag."
        )

    return {
        "headline": "AI Confidence Calibration",
        "current_confidence": confidence,
        "calibrated_confidence": calibrated,
        "status": status,
        "reason": reason,
        "samples": samples,
        "decisions": decisions,
    }
