from ai_prediction_engine_service import get_prediction_engine
from ai_learning_feedback_service import get_learning_feedback


def get_ai_context():
    """
    Samler AI'ens overordnede kontekst i ét objekt.
    """

    prediction = get_prediction_engine()
    feedback = get_learning_feedback()

    samples = feedback["total_samples"]

    if samples < 5:
        confidence = "Low"
    elif samples < 20:
        confidence = "Medium"
    elif prediction["expected_accuracy"] >= 80:
        confidence = "High"
    elif prediction["expected_accuracy"] >= 60:
        confidence = "Medium"
    else:
        confidence = "Low"

    return {
        "headline": "AI Context Engine",
        "prediction_accuracy": prediction["expected_accuracy"],
        "learning_status": feedback["status"],
        "learning_samples": feedback["total_samples"],
        "confidence": confidence,
    }
