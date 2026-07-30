from ai_copilot_history_service import load_copilot_history


def get_learning_trends():
    """
    Beregner udviklingen i AI'ens historiske præcision.
    """

    history = load_copilot_history()

    if not history:
        return {
            "trend": "Ingen historik",
            "first_accuracy": 0,
            "latest_accuracy": 0,
            "change": 0,
        }

    accuracies = []

    for row in history:
        if "confidence" in row:
            try:
                accuracies.append(float(row["confidence"]))
            except (ValueError, TypeError):
                pass

    if not accuracies:
        return {
            "trend": "Ingen data",
            "first_accuracy": 0,
            "latest_accuracy": 0,
            "change": 0,
        }

    first = accuracies[0]
    latest = accuracies[-1]
    change = round(latest - first, 1)

    if change > 2:
        trend = "Forbedres"
    elif change < -2:
        trend = "Faldende"
    else:
        trend = "Stabil"

    return {
        "trend": trend,
        "first_accuracy": first,
        "latest_accuracy": latest,
        "change": change,
    }
