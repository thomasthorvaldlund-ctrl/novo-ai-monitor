from ai_portfolio_performance_service import get_portfolio_performance


ACTIONS = ("BUY", "HOLD", "REDUCE")

SUCCESS_RESULTS = {
    "God beslutning",
    "God risikostyring",
    "Stabil vurdering",
    "Positiv udvikling",
}

FAILED_RESULTS = {
    "Negativ udvikling",
    "Forkert timing",
}


def classify_ai_result(ai_result):
    """
    Klassificerer AI-resultatet som korrekt, forkert eller afventende.
    """

    if ai_result in SUCCESS_RESULTS:
        return "correct"

    if ai_result in FAILED_RESULTS:
        return "incorrect"

    return "pending"


def calculate_accuracy(correct, evaluated):
    """
    Beregner accuracy i procent.
    """

    if evaluated == 0:
        return 0.0

    return round((correct / evaluated) * 100, 1)


def get_portfolio_analytics():
    """
    Returnerer samlet statistik over AI-porteføljebeslutninger.
    """

    performance = get_portfolio_performance()

    analytics = {
        "total_decisions": len(performance),
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

    for item in performance:
        action = item.get("action")
        ai_result = item.get("ai_result")
        classification = classify_ai_result(ai_result)

        if action not in analytics["by_action"]:
            continue

        action_stats = analytics["by_action"][action]
        action_stats["total"] += 1

        if classification == "correct":
            analytics["correct_decisions"] += 1
            analytics["evaluated_decisions"] += 1

            action_stats["correct"] += 1
            action_stats["evaluated"] += 1

        elif classification == "incorrect":
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

    return analytics
