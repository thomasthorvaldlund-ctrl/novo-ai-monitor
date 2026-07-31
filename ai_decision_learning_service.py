from collections import Counter

from ai_decision_performance_service import get_decision_performance
from ai_decision_evaluation_service import get_decision_quality


def get_decision_learning():

    performance = get_decision_performance()
    quality = get_decision_quality()

    insights = []

    signal_distribution = {
        "BUY": performance["buy"],
        "HOLD": performance["hold"],
        "REDUCE": performance["reduce"],
    }

    active_signals = [
        key
        for key, value in signal_distribution.items()
        if value > 0
    ]

    if quality["valid_decisions"] < 20:
        insights.append(
            "AI har endnu begrænset historik og kræver flere observationer."
        )

    if quality["quality_accuracy"] >= 80:
        insights.append(
            "Validerede beslutninger viser høj historisk kvalitet."
        )
    else:
        insights.append(
            "AI bør fortsat kalibreres baseret på nye resultater."
        )

    if len(active_signals) == 1:
        learning_warning = (
            "Historikken indeholder kun "
            f"{active_signals[0]}-beslutninger. "
            "Andre beslutningstyper kan endnu ikke vurderes."
        )

        insights.append(learning_warning)

    else:
        learning_warning = (
            "AI har historik på flere beslutningstyper."
        )

    return {
        "total_decisions": quality["total_decisions"],
        "validated_decisions": quality["valid_decisions"],
        "accuracy": quality["quality_accuracy"],
        "good_decisions": quality["good_decisions"],
        "bad_decisions": quality["bad_decisions"],

        "buy_signals": performance["buy"],
        "hold_signals": performance["hold"],
        "reduce_signals": performance["reduce"],

        "signal_distribution": signal_distribution,
        "learning_warning": learning_warning,

        "status": performance["status"],
        "insights": insights,
    }