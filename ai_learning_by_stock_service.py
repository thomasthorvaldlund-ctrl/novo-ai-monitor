from collections import defaultdict

from ai_decision_event_evaluation_service import (
    get_evaluated_decision_events,
)


EVALUABLE_OUTCOMES = {
    "CORRECT",
    "INCORRECT",
}


def get_learning_by_stock():
    """
    Beregner historisk learning performance pr. aktie
    ud fra reelle lukkede beslutningsevents.
    """

    events = get_evaluated_decision_events()

    stocks = defaultdict(
        lambda: {
            "total": 0,
            "correct": 0,
            "score_sum": 0.0,
            "score_samples": 0,
        }
    )

    for event in events:
        outcome = event.get("outcome")

        if outcome not in EVALUABLE_OUTCOMES:
            continue

        stock = event.get(
            "stock",
            "Ukendt",
        )

        score = event.get("score")

        stats = stocks[stock]

        stats["total"] += 1

        if isinstance(score, (int, float)):
            stats["score_sum"] += score
            stats["score_samples"] += 1

        if outcome == "CORRECT":
            stats["correct"] += 1

    result = []

    for stock, stats in sorted(stocks.items()):
        total = stats["total"]
        correct = stats["correct"]

        accuracy = (
            round(
                correct / total * 100,
                1,
            )
            if total
            else 0.0
        )

        average_score = (
            round(
                stats["score_sum"]
                / stats["score_samples"],
                1,
            )
            if stats["score_samples"]
            else 0.0
        )

        result.append({
            "stock": stock,
            "total": total,
            "correct": correct,
            "accuracy": accuracy,
            "average_score": average_score,
        })

    return result
