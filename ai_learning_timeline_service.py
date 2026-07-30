from ai_learning_history_service import load_learning_history


def average_accuracy(entries):
    if not entries:
        return 0.0
    return round(sum(item["accuracy"] for item in entries) / len(entries), 1)


def get_learning_timeline():
    """
    Beregner Learning Timeline ud fra historiske snapshots.
    """

    history = load_learning_history()

    last_7 = history[-7:]
    last_30 = history[-30:]
    last_90 = history[-90:]

    acc7 = average_accuracy(last_7)
    acc30 = average_accuracy(last_30)
    acc90 = average_accuracy(last_90)

    if acc7 > acc30:
        trend = "Improving"
    elif acc7 < acc30:
        trend = "Declining"
    else:
        trend = "Stable"

    chart_labels = [
        item.get("timestamp", "")[:10]
        for item in history
    ]

    chart_values = [
        item.get("accuracy", 0.0)
        for item in history
    ]

    return {
        "last_7_days": acc7,
        "last_30_days": acc30,
        "last_90_days": acc90,
        "trend": trend,
        "history": history,
        "chart_labels": chart_labels,
        "chart_values": chart_values,
    }
