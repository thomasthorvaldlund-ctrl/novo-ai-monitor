def compare_copilot_snapshots(previous, current):
    """
    Sammenligner to AI Copilot snapshots.
    Returnerer ændringer mellem analyser.
    """

    if not previous or not current:
        return {
            "changed": False,
            "changes": [
                "Ingen tidligere AI Copilot analyse til sammenligning."
            ],
        }

    changes = []

    if previous.get("headline") != current.get("headline"):
        changes.append(
            f"Status ændret: "
            f"{previous.get('headline')} → "
            f"{current.get('headline')}"
        )

    if previous.get("best_opportunity") != current.get("best_opportunity"):
        changes.append(
            "Top kandidat ændret."
        )

    if previous.get("risk_level") != current.get("risk_level"):
        changes.append(
            f"Risiko ændret: "
            f"{previous.get('risk_level')} → "
            f"{current.get('risk_level')}"
        )

    if previous.get("confidence") != current.get("confidence"):
        changes.append(
            f"Confidence ændret: "
            f"{previous.get('confidence')} → "
            f"{current.get('confidence')}"
        )

    return {
        "changed": len(changes) > 0,
        "changes": changes if changes else [
            "Ingen væsentlige ændringer siden sidste analyse."
        ],
    }
