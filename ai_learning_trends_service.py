from ai_learning_history_service import load_learning_history


def is_v2_snapshot(row):
    """
    Returnerer True for snapshots baseret på
    Decision Events v2 learning-data.
    """
    return (
        isinstance(row, dict)
        and "accuracy" in row
        and "evaluated_decisions" in row
        and "correct_decisions" in row
        and "incorrect_decisions" in row
    )


def get_learning_trends():
    """
    Beregner udviklingen i AI'ens historiske præcision
    ud fra Decision Events v2 learning-snapshots.

    Ældre snapshots uden Decision Events-felter
    ignoreres for at undgå at blande forskellige
    learning-metoder.
    """
    history = load_learning_history()

    v2_history = [
        row
        for row in history
        if is_v2_snapshot(row)
    ]

    accuracies = []

    for row in v2_history:
        accuracy = row.get("accuracy")

        if isinstance(accuracy, (int, float)):
            accuracies.append(float(accuracy))

    if not accuracies:
        return {
            "trend": "Ingen historik",
            "first_accuracy": 0.0,
            "latest_accuracy": 0.0,
            "change": 0.0,
        }

    first = accuracies[0]
    latest = accuracies[-1]

    if len(accuracies) < 2:
        return {
            "trend": "For lidt historik",
            "first_accuracy": first,
            "latest_accuracy": latest,
            "change": 0.0,
        }

    change = round(
        latest - first,
        1,
    )

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
