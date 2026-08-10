from ai_portfolio_brain_score_service import get_brain_score
from ai_prediction_engine_service import get_prediction_engine
from ai_learning_feedback_service import get_learning_feedback
from ai_context_engine_service import get_ai_context
from ai_confidence_label_service import normalize_confidence_label


def get_brain_score_explanation(
    brain_score=None
):

    score_data = (
        brain_score
        if brain_score is not None
        else get_brain_score()
    )

    prediction = get_prediction_engine()
    feedback = get_learning_feedback()
    context = get_ai_context()

    factors = []

    prediction_accuracy = prediction.get("expected_accuracy", 0)
    samples = feedback.get("total_samples", 0)
    confidence = context.get("confidence", "Unknown")

    if prediction_accuracy < 30:
        factors.append(
            "Prediction accuracy er lav og reducerer AI'ens beslutningsstyrke."
        )

    if samples < 5:
        factors.append(
            "Datagrundlaget er begrænset med få historiske observationer."
        )

    if confidence in ["Low", "VeryLow"]:
        factors.append(
            "AI confidence niveauet er lavt."
        )

    if not factors:
        factors.append(
            "AI har et stabilt datagrundlag og højere beslutningssikkerhed."
        )

    return {
    "headline": "AI Brain Score Explanation",
    "score": score_data.get("score", 0),
    "decision_strength": score_data.get("decision_strength"),

    "confidence":
        normalize_confidence_label(confidence),

    "factors": factors,
    "summary": (
        "Brain Score vurderes ud fra historiske resultater, "
        "confidence og kvaliteten af AI'ens datagrundlag."
    ),
    }
