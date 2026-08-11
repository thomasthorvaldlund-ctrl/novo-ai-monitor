from collections import defaultdict

from ai_decision_event_evaluation_service import (
    get_evaluated_decision_events,
)


LEVELS = (
    ("Very High", 80),
    ("High", 60),
    ("Medium", 40),
    ("Low", 0),
)


EVALUABLE_OUTCOMES = {
    "CORRECT",
    "INCORRECT",
}


def confidence_level(score):
    """
    Returnerer confidence-niveau ud fra AI-score.
    """
    score = score or 0

    for level, minimum in LEVELS:
        if score >= minimum:
            return level

    return "Low"


def get_confidence_calibration():
    """
    Beregner empirisk accuracy pr. confidence-niveau
    ud fra reelle lukkede beslutningsevents.

    Top-level formatet bevares for bagudkompatibilitet.
    Action breakdown eksponeres separat i hver bucket,
    så score-confidence ikke forveksles med action-effekt.
    """

    events = get_evaluated_decision_events()

    calibration = {
        level: {
            "total": 0,
            "correct": 0,
            "accuracy_pct": 0.0,
            "action_breakdown": {},
        }
        for level, _ in LEVELS
    }

    action_stats = {
        level: defaultdict(
            lambda: {
                "total": 0,
                "correct": 0,
            }
        )
        for level, _ in LEVELS
    }

    for event in events:
        outcome = event.get("outcome")

        if outcome not in EVALUABLE_OUTCOMES:
            continue

        score = event.get("score")
        action = event.get(
            "action",
            "UNKNOWN",
        )

        level = confidence_level(score)

        calibration[level]["total"] += 1
        action_stats[level][action]["total"] += 1

        if outcome == "CORRECT":
            calibration[level]["correct"] += 1
            action_stats[level][action]["correct"] += 1

    for level, stats in calibration.items():
        if stats["total"] > 0:
            stats["accuracy_pct"] = round(
                stats["correct"]
                / stats["total"]
                * 100,
                1,
            )

        breakdown = {}

        for action, action_data in sorted(
            action_stats[level].items()
        ):
            total = action_data["total"]
            correct = action_data["correct"]

            breakdown[action] = {
                "total": total,
                "correct": correct,
                "accuracy_pct": (
                    round(
                        correct / total * 100,
                        1,
                    )
                    if total
                    else 0.0
                ),
            }

        stats["action_breakdown"] = breakdown

    return calibration
