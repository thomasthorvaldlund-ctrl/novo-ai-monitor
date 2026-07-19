def compare_copilot_snapshots(previous, current):
    """
    Sammenligner to AI Copilot snapshots.
    Returnerer ændringer mellem analyser.
    """

    if not previous or not current:
        return {
            "changed": False,
            "status": "neutral",
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

    status = "neutral"

    if changes:
        old_confidence = previous.get("confidence", 0)
        new_confidence = current.get("confidence", 0)

        old_risk = previous.get("risk_level")
        new_risk = current.get("risk_level")

        if new_confidence > old_confidence:
            status = "positive"

        if new_confidence < old_confidence:
            status = "negative"

        if old_risk == "Moderat" and new_risk == "Lav":
            status = "positive"

        if old_risk == "Lav" and new_risk in ["Moderat", "Høj"]:
            status = "negative"

    return {
        "changed": len(changes) > 0,
        "status": status,
        "changes": changes if changes else [
            "Ingen væsentlige ændringer siden sidste analyse."
        ],
    }
