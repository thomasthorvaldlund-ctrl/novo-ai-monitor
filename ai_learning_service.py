from collections import defaultdict

from ai_decision_event_evaluation_service import (
    get_evaluated_decision_events,
)


ACTIONS = (
    "BUY",
    "HOLD",
    "WATCH",
    "REDUCE",
)


EVALUABLE_OUTCOMES = {
    "CORRECT",
    "INCORRECT",
}


def calculate_accuracy(correct, evaluated):
    """
    Beregner accuracy i procent.
    """

    if evaluated == 0:
        return 0.0

    return round(
        correct / evaluated * 100,
        1,
    )


def get_learning_report():
    """
    Decision Event Learning v2.

    Bygger AI Learning Report ud fra reelle lukkede
    beslutningsevents i stedet for seneste portfolio snapshot.
    """

    events = get_evaluated_decision_events()

    analytics = {
        "total_decisions": len(events),
        "evaluated_decisions": 0,
        "correct_decisions": 0,
        "incorrect_decisions": 0,
        "pending_decisions": 0,
        "accuracy_pct": 0.0,
        "by_action": {
            action: {
                "total": 0,
                "evaluated": 0,
                "correct": 0,
                "incorrect": 0,
                "pending": 0,
                "accuracy_pct": 0.0,
            }
            for action in ACTIONS
        },
    }

    for event in events:
        action = event.get(
            "action",
            "UNKNOWN",
        )

        outcome = event.get("outcome")

        if action not in analytics["by_action"]:
            continue

        action_stats = analytics["by_action"][action]

        action_stats["total"] += 1

        if outcome == "CORRECT":
            analytics["correct_decisions"] += 1
            analytics["evaluated_decisions"] += 1

            action_stats["correct"] += 1
            action_stats["evaluated"] += 1

        elif outcome == "INCORRECT":
            analytics["incorrect_decisions"] += 1
            analytics["evaluated_decisions"] += 1

            action_stats["incorrect"] += 1
            action_stats["evaluated"] += 1

        else:
            analytics["pending_decisions"] += 1
            action_stats["pending"] += 1

    analytics["accuracy_pct"] = calculate_accuracy(
        analytics["correct_decisions"],
        analytics["evaluated_decisions"],
    )

    for action_stats in analytics["by_action"].values():
        action_stats["accuracy_pct"] = calculate_accuracy(
            action_stats["correct"],
            action_stats["evaluated"],
        )

    accuracy = analytics["accuracy_pct"]

    if accuracy >= 80:
        status = "Excellent"
        recommendation = (
            "AI performs consistently well."
        )

    elif accuracy >= 60:
        status = "Good"
        recommendation = (
            "Continue monitoring current strategy."
        )

    elif accuracy >= 40:
        status = "Needs Improvement"
        recommendation = (
            "Review recent AI decisions for recurring mistakes."
        )

    else:
        status = "Poor"
        recommendation = (
            "Consider adjusting AI weighting and decision rules."
        )

    return {
        "accuracy": accuracy,
        "status": status,
        "recommendation": recommendation,
        "analytics": analytics,
    }
