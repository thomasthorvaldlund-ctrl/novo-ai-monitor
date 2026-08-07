import json
from pathlib import Path


ADAPTIVE_HISTORY_FILE = Path(
    "adaptive_decision_history.json"
)


def load_adaptive_history():
    """
    Henter adaptive simulationer.
    """

    if not ADAPTIVE_HISTORY_FILE.exists():
        return []

    try:
        with open(
            ADAPTIVE_HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)

    except Exception:
        return []


def get_adaptive_performance():
    """
    Evaluerer historisk kvalitet af adaptive AI-justeringer.
    """

    history = load_adaptive_history()

    total_simulations = len(history)

    changed_decisions = sum(
        1
        for item in history
        if item.get(
            "learning_changed_signal"
        )
    )

    unchanged_decisions = (
        total_simulations
        -
        changed_decisions
    )

    change_rate = (
        round(
            changed_decisions / total_simulations * 100,
            1
        )
        if total_simulations
        else 0
    )

    return {
        "total_simulations": total_simulations,
        "changed_decisions": changed_decisions,
        "unchanged_decisions": unchanged_decisions,
        "change_rate": change_rate,
        "status": (
            "Collecting learning data"
            if total_simulations < 50
            else "Learning evaluation active"
        ),
    }