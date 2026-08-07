from ai_copilot_engine_service import get_ai_copilot
from market_intelligence_service import get_market_intelligence
from global_market_score_service import get_global_market_score


def get_copilot_decision():
    """
    Omsætter AI Copilot vurderingen til en struktureret beslutning.
    """

    copilot = get_ai_copilot()

    market_intelligence = get_market_intelligence()

    global_market_score = get_global_market_score(
        market_intelligence
    )

    strategy = copilot["strategy"]
    confidence = copilot["confidence"]

    if strategy == "Aggressiv" and confidence == "High":
        action = "BUY"
        priority = "High"
        risk = "Lavere"

    elif strategy == "Defensiv":
        action = "HOLD"
        priority = "Medium"
        risk = "Moderat"

    else:
        action = "WATCH"
        priority = "Low"
        risk = "Moderat"


    market_score = global_market_score.get(
        "score",
        50
    )

    decision_reason = []

    if action == "BUY" and market_score < 40:
        decision_reason.append(
            "BUY nedjusteret på grund af svag global markedstilstand."
        )

        action = "WATCH"
        priority = "Medium"
        risk = "Høj"

    elif action == "BUY" and market_score < 60:
        decision_reason.append(
            "BUY nedjusteret på grund af neutral global markedstilstand."
        )

        action = "HOLD"
        priority = "Medium"
        risk = "Moderat"


    reason = copilot["summary"]

    if decision_reason:
        reason += " " + " ".join(
            decision_reason
        )

    return {
        "headline": "AI Copilot Decision",
        "action": action,
        "priority": priority,
        "risk": risk,
        "reason": reason,
    }
