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


def get_portfolio_analytics():
    """
    Returnerer samlet statistik over AI-porteføljebeslutninger
    baseret på reelle lukkede Decision Events v2.
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
        action = event.get("action")
        outcome = event.get("outcome")

        if action not in analytics["by_action"]:
            continue

        stats = analytics["by_action"][action]
        stats["total"] += 1

        if outcome == "CORRECT":
            analytics["correct_decisions"] += 1
            analytics["evaluated_decisions"] += 1

            stats["correct"] += 1
            stats["evaluated"] += 1

        elif outcome == "INCORRECT":
            analytics["incorrect_decisions"] += 1
            analytics["evaluated_decisions"] += 1

            stats["incorrect"] += 1
            stats["evaluated"] += 1

        else:
            analytics["pending_decisions"] += 1
            stats["pending"] += 1

    analytics["accuracy_pct"] = calculate_accuracy(
        analytics["correct_decisions"],
        analytics["evaluated_decisions"],
    )

    for stats in analytics["by_action"].values():
        stats["accuracy_pct"] = calculate_accuracy(
            stats["correct"],
            stats["evaluated"],
        )

    return analytics
