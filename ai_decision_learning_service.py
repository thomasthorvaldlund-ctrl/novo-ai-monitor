from collections import Counter

from ai_decision_performance_service import get_decision_performance
from ai_decision_evaluation_service import get_decision_quality
from ai_decision_history_service import load_decision_history




def get_market_regime(score):
    """
    Klassificerer Global Market Score.
    """

    if score >= 70:
        return "Positive"

    elif score >= 40:
        return "Neutral"

    else:
        return "Weak"

def get_decision_learning():

    performance = get_decision_performance()
    quality = get_decision_quality()
    history = load_decision_history()

    market_scores = [
        item.get("global_market_score", {}).get("score")
        for item in history
        if item.get("global_market_score")
        and item.get("global_market_score", {}).get("score") is not None
    ]

    market_context_count = len(market_scores)

    average_market_score = (
        round(
            sum(market_scores) / market_context_count,
            1
        )
        if market_context_count
        else None
    )

    regime_distribution = {
        "Positive": 0,
        "Neutral": 0,
        "Weak": 0,
    }

    for score in market_scores:
        regime = get_market_regime(score)
        regime_distribution[regime] += 1

    regime_performance = {
        "Positive": {
            "decisions": 0,
        },
        "Neutral": {
            "decisions": 0,
        },
        "Weak": {
            "decisions": 0,
        },
    }

    for item in history:
        market_score = item.get(
            "global_market_score",
            {}
        ).get(
            "score"
        )

        if market_score is not None:
            regime = get_market_regime(
                market_score
            )

            regime_performance[regime]["decisions"] += 1

    regime_signals = {
        "Positive": {
            "BUY": 0,
            "HOLD": 0,
            "REDUCE": 0,
        },
        "Neutral": {
            "BUY": 0,
            "HOLD": 0,
            "REDUCE": 0,
        },
        "Weak": {
            "BUY": 0,
            "HOLD": 0,
            "REDUCE": 0,
        },
    }

    for item in history:
        market_score = item.get(
            "global_market_score",
            {}
        ).get(
            "score"
        )

        action = item.get(
            "action"
        )

        if market_score is not None and action in [
            "BUY",
            "HOLD",
            "REDUCE",
        ]:
            regime = get_market_regime(
                market_score
            )

            regime_signals[regime][action] += 1

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

    if market_context_count > 0:
        insights.append(
            f"AI har analyseret {market_context_count} beslutninger "
            f"med Global Market Context. "
            f"Gennemsnitlig Global Market Score: "
            f"{average_market_score}/100."
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

        "market_context_count": market_context_count,
        "average_market_score": average_market_score,
        "regime_distribution": regime_distribution,
        "regime_performance": regime_performance,
        "regime_signals": regime_signals,

        "learning_warning": learning_warning,

        "status": performance["status"],
        "insights": insights,
    }