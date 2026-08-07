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

    regime_confidence = {
        "Positive": {
            "High": 0,
            "Medium": 0,
            "Low": 0,
        },
        "Neutral": {
            "High": 0,
            "Medium": 0,
            "Low": 0,
        },
        "Weak": {
            "High": 0,
            "Medium": 0,
            "Low": 0,
        },
    }

    for item in history:
        market_score = item.get(
            "global_market_score",
            {}
        ).get(
            "score"
        )

        confidence = item.get(
            "confidence"
        )

        if market_score is not None and confidence in [
            "High",
            "Medium",
            "Low",
        ]:
            regime = get_market_regime(
                market_score
            )

            regime_confidence[regime][confidence] += 1

    regime_intelligence = {}

    for regime in [
        "Positive",
        "Neutral",
        "Weak",
    ]:
        decisions = regime_performance[regime]["decisions"]

        score = 0

        if decisions >= 5:
            score += 40
        elif decisions > 0:
            score += 20

        confidence_data = regime_confidence[regime]

        if confidence_data["High"] > 0:
            score += 30
            confidence_level = "High"

        elif confidence_data["Medium"] > 0:
            score += 20
            confidence_level = "Medium"

        elif confidence_data["Low"] > 0:
            score += 10
            confidence_level = "Low"

        else:
            confidence_level = "Unknown"

        if decisions == 0:
            explanation = (
                "Der mangler historiske beslutninger "
                "i dette markedsregime."
            )

        elif confidence_level == "Low":
            explanation = (
                "Regimet har historik, "
                "men AI confidence er fortsat lav."
            )

        elif confidence_level == "Medium":
            explanation = (
                "Regimet har moderat historik "
                "og acceptabel AI confidence."
            )

        else:
            explanation = (
                "Regimet har stærkt datagrundlag "
                "og høj AI confidence."
            )

        regime_intelligence[regime] = {
            "score": score,
            "decisions": decisions,
            "confidence": confidence_level,
            "explanation": explanation,
        }

    regime_insights = []

    for regime, data in regime_intelligence.items():
        regime_insights.append(
            f"{regime} regime: "
            f"Intelligence Score {data['score']}/100. "
            f"Historiske beslutninger: {data['decisions']}. "
            f"Confidence: {data['confidence']}. "
            f"{data['explanation']}"
        )

    regime_ranking = sorted(
        regime_intelligence.items(),
        key=lambda x: x[1]["score"],
        reverse=True
    )

    best_regime = regime_ranking[0]

    best_name = best_regime[0]
    best_data = best_regime[1]

    regime_recommendation = {
        "best_regime": best_name,
        "score": best_data["score"],
        "confidence": best_data["confidence"],
        "recommendation": "",
    }

    if best_data["score"] >= 40:
        regime_recommendation["recommendation"] = (
            f"AI har mest erfaring i {best_name}-regimet. "
            "Dette regime har det stærkeste historiske datagrundlag. "
        )

    else:
        regime_recommendation["recommendation"] = (
            "AI har endnu begrænset erfaring på tværs af regimer."
        )

    if regime_intelligence["Weak"]["decisions"] == 0:
        regime_recommendation["recommendation"] += (
            "Weak-regimer bør behandles konservativt, "
            "da historikken er begrænset."
        )

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
        "regime_confidence": regime_confidence,
        "regime_intelligence": regime_intelligence,
        "regime_insights": regime_insights,
        "regime_ranking": regime_ranking,
        "regime_recommendation": regime_recommendation,

        "learning_warning": learning_warning,

        "status": performance["status"],
        "insights": insights,
    }