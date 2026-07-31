from ai_copilot_engine_service import get_ai_copilot


def get_copilot_decision():
    """
    Omsætter AI Copilot vurderingen til en struktureret beslutning.
    """

    copilot = get_ai_copilot()

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

    reason = copilot["summary"]

    return {
        "headline": "AI Copilot Decision",
        "action": action,
        "priority": priority,
        "risk": risk,
        "reason": reason,
    }
