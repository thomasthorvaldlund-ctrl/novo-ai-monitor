from ai_context_engine_service import get_ai_context
from ai_portfolio_brain_service import get_ai_portfolio_brain
from ai_prediction_engine_service import get_prediction_engine
from ai_learning_feedback_service import get_learning_feedback


def get_brain_score(
    portfolio_brain=None
):
    brain = (
        portfolio_brain
        if portfolio_brain is not None
        else get_ai_portfolio_brain()
    )

    context = get_ai_context()
    prediction = get_prediction_engine()
    feedback = get_learning_feedback()

    learning_samples = feedback.get("total_samples", 0)
    prediction_accuracy = prediction.get("expected_accuracy", 0)

    score = 50

    if prediction_accuracy > 70:
        score += 20
    elif prediction_accuracy < 30:
        score -= 15

    if learning_samples >= 50:
        score += 15
    elif learning_samples < 5:
        score -= 10

    score = max(0, min(score, 100))

    if score >= 75:
        strength = "Stærk"
    elif score >= 50:
        strength = "Moderat"
    else:
        strength = "Svag"

    return {
        "score": score,
        "confidence_score": prediction_accuracy,
        "data_quality": context.get("learning_status"),
        "decision_strength": strength,
        "decision": brain.get("action"),
        "risk": brain.get("risk"),
    }
