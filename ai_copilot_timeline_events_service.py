def build_timeline_events(changes):
    """
    Konverterer AI Copilot changes til strukturerede Timeline Events.
    """

    if not changes:
        return []

    neutral_messages = {
        "Ingen væsentlige ændringer siden sidste analyse.",
        "Ingen tidligere AI Copilot analyse til sammenligning.",
    }

    events = []

    for change in changes:

        text = str(change).strip()

        if text in neutral_messages:
            continue

        if "Topkandidat ændret" in text:
            events.append({
                "type": "top_pick",
                "icon": "⭐",
                "title": "Ny Top Pick",
                "description": text,
            })

        elif "AI Risk Score ændret" in text:
            events.append({
                "type": "risk_score",
                "icon": "⚠️",
                "title": "AI Risk Score ændret",
                "description": text,
            })

        elif "Samlet AI Risk ændret" in text:
            events.append({
                "type": "overall_risk",
                "icon": "🛡️",
                "title": "Samlet risiko ændret",
                "description": text,
            })

        elif "Copilot-risiko ændret" in text:
            events.append({
                "type": "copilot_risk",
                "icon": "🚨",
                "title": "Copilot risiko ændret",
                "description": text,
            })

        elif "AI confidence ændret" in text:
            events.append({
                "type": "confidence",
                "icon": "📈",
                "title": "Confidence ændret",
                "description": text,
            })

        elif "AI-vurdering ændret" in text:
            events.append({
                "type": "headline",
                "icon": "🧠",
                "title": "Ny AI vurdering",
                "description": text,
            })

        elif "Nye risikofaktorer" in text:
            events.append({
                "type": "risk_added",
                "icon": "➕",
                "title": "Nye risikofaktorer",
                "description": text,
            })

        elif "Risikofaktorer fjernet" in text:
            events.append({
                "type": "risk_removed",
                "icon": "✅",
                "title": "Risikofaktorer fjernet",
                "description": text,
            })

        else:
            events.append({
                "type": "info",
                "icon": "ℹ️",
                "title": "AI Copilot",
                "description": text,
            })

    return events
