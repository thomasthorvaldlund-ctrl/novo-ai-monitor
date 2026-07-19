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
            "status": item.get(
                "status",
                "neutral"
            ),
            "changes": item.get(
                "changes",
                []
            ),
        })

    # Fjern gentagelser og skjul passive analyser
    filtered = []

    last_signature = None
    neutral_added = False

    for item in reversed(timeline):

        changes = item.get("changes", [])

        is_neutral = (
            not changes
            or changes == [
                "Ingen væsentlige ændringer siden sidste analyse."
            ]
        )

        # Gem kun én neutral status
        if is_neutral:
            if neutral_added:
                continue

            neutral_added = True

        signature = (
            item.get("status"),
            tuple(changes),
            item.get("confidence"),
            item.get("risk_level"),
        )

        if signature != last_signature:
            filtered.append(item)
            last_signature = signature

    # Vend tilbage til kronologisk rækkefølge
    filtered.reverse()

    return filtered
