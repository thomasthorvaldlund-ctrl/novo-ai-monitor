from collections import defaultdict

from ai_decision_event_evaluation_service import (
    get_evaluated_decision_events,
)


EVALUABLE_OUTCOMES = {
    "CORRECT",
    "INCORRECT",
}


def get_signal_accuracy():
    """
    Beregner signal-accuracy ud fra reelle lukkede
    beslutningsevents i stedet for gentagne snapshots.

    Kun CORRECT og INCORRECT indgår i accuracy.
    """

    events = get_evaluated_decision_events()

    signals = defaultdict(
        lambda: {
            "total": 0,
            "correct": 0,
        }
    )

    for event in events:
        outcome = event.get("outcome")

        if outcome not in EVALUABLE_OUTCOMES:
            continue

        signal = event.get(
            "action",
            "UNKNOWN",
        )

        stats = signals[signal]
        stats["total"] += 1

        if outcome == "CORRECT":
            stats["correct"] += 1

    result = []

    for signal in sorted(signals):
        total = signals[signal]["total"]
        correct = signals[signal]["correct"]

        accuracy = (
            round(
                correct / total * 100,
                1,
            )
            if total
            else 0.0
        )

        result.append({
            "signal": signal,
            "total": total,
            "correct": correct,
            "accuracy": accuracy,
        })

    return result
