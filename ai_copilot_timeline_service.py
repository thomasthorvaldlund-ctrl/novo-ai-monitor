from ai_copilot_history_service import load_copilot_history


def get_copilot_timeline(limit=30):
    """
    Returnerer historik til AI Copilot Timeline.
    """

    history = load_copilot_history()

    if not history:
        return []

    timeline = []

    for item in history[-limit:]:

        timeline.append({
            "date": item.get("date"),
            "confidence": item.get("confidence", 0),
            "risk_level": item.get("risk_level"),
            "headline": item.get("headline"),
            "best_opportunity": item.get(
                "best_opportunity"
            ),
        })

    return timeline
