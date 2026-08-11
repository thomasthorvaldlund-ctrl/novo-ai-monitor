from collections import defaultdict

from ai_adaptive_history_service import load_adaptive_history


def get_adaptive_signal_analysis():
    """
    Analyserer hvordan AI ændrer signaler.
    """

    history = load_adaptive_history()

    changes = defaultdict(int)

    total_changes = 0

    for item in history:

        if not item.get(
            "learning_changed_signal"
        ):
            continue

        before = item.get(
            "calculated_signal_before_learning",
            "Unknown"
        )

        after = item.get(
            "calculated_signal_after_learning",
            "Unknown"
        )

        key = f"{before}_to_{after}"

        changes[key] += 1

        total_changes += 1


    return {
        "signal_changes": dict(changes),
        "total_changes": total_changes,
    }
