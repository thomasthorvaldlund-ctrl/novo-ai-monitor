from datetime import datetime, timedelta

from ai_learning_history_service import (
    load_learning_history,
)


def average_accuracy(entries):
    """
    Beregner gennemsnitlig accuracy for historikposter.
    """

    if not entries:
        return 0.0

    values = []

    for item in entries:
        accuracy = item.get("accuracy")

        if isinstance(accuracy, (int, float)):
            values.append(float(accuracy))

    if not values:
        return 0.0

    return round(
        sum(values) / len(values),
        1,
    )


def parse_history():
    """
    Returnerer historikposter med gyldige ISO timestamps.
    """

    parsed = []

    for item in load_learning_history():
        timestamp = item.get("timestamp")

        if not timestamp:
            continue

        try:
            dt = datetime.fromisoformat(timestamp)
        except (TypeError, ValueError):
            continue

        parsed.append(
            (dt, item)
        )

    return sorted(
        parsed,
        key=lambda row: row[0],
    )


def get_window_entries(
    dated_history,
    latest_timestamp,
    days,
):
    """
    Returnerer historikposter inden for et reelt
    kalenderbaseret tidsvindue.
    """

    cutoff = latest_timestamp - timedelta(
        days=days
    )

    return [
        item
        for timestamp, item in dated_history
        if timestamp >= cutoff
    ]


def get_learning_timeline():
    """
    Beregner Learning Timeline ud fra historiske
    Decision Event Learning snapshots.

    7, 30 og 90 dage er reelle kalenderperioder
    og ikke antal snapshots.
    """

    dated_history = parse_history()

    if not dated_history:
        return {
            "last_7_days": 0.0,
            "last_30_days": 0.0,
            "last_90_days": 0.0,
            "trend": "Ingen historik",
            "history": [],
            "chart_labels": [],
            "chart_values": [],
        }

    latest_timestamp = dated_history[-1][0]

    last_7 = get_window_entries(
        dated_history,
        latest_timestamp,
        7,
    )

    last_30 = get_window_entries(
        dated_history,
        latest_timestamp,
        30,
    )

    last_90 = get_window_entries(
        dated_history,
        latest_timestamp,
        90,
    )

    acc7 = average_accuracy(last_7)
    acc30 = average_accuracy(last_30)
    acc90 = average_accuracy(last_90)

    if acc7 > acc30:
        trend = "Improving"
    elif acc7 < acc30:
        trend = "Declining"
    else:
        trend = "Stable"

    history = [
        item
        for _, item in dated_history
    ]

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
