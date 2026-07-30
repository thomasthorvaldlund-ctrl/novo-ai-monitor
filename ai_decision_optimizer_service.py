from ai_signal_accuracy_service import get_signal_accuracy
from ai_prediction_engine_service import get_prediction_engine


def get_decision_optimizer():
    """
    Giver anbefalinger til, hvordan AI bør vægte fremtidige beslutninger.
    """

    prediction = get_prediction_engine()
    recommendations = []

    for signal in get_signal_accuracy():
        if signal["total"] < 3:
            recommendations.append(
                f"{signal['signal']}: For få historiske data til at ændre vægtningen."
            )
        elif signal["accuracy"] >= 80:
            recommendations.append(
                f"{signal['signal']}: Historisk stærk præcision – signalet kan prioriteres højere."
            )
        elif signal["accuracy"] < 60:
            recommendations.append(
                f"{signal['signal']}: Lav historisk præcision – anvend ekstra forsigtighed."
            )

    return {
        "headline": "AI Decision Optimizer",
        "expected_accuracy": prediction["expected_accuracy"],
        "recommendations": recommendations,
    }
