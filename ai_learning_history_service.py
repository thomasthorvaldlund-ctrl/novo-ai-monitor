import json
from datetime import datetime
from pathlib import Path

from ai_learning_service import get_learning_report


HISTORY_FILE = Path("ai_learning_history.json")


def load_learning_history():
    """
    Indlæser historikken for AI Learning Timeline.
    """

    if not HISTORY_FILE.exists():
        return []

    try:
        data = json.loads(
            HISTORY_FILE.read_text(
                encoding="utf-8"
            )
        )

        if isinstance(data, list):
            return data

        return []

    except (OSError, json.JSONDecodeError):
        return []


def save_learning_snapshot():
    """
    Gemmer et Decision Event Learning v2 snapshot.

    Et nyt snapshot gemmes kun, når accuracy eller antallet
    af evaluerede beslutninger har ændret sig.
    """

    history = load_learning_history()
    learning = get_learning_report()

    analytics = learning.get(
        "analytics",
        {},
    )

    accuracy = learning.get(
        "accuracy",
        0.0,
    )

    evaluated_decisions = analytics.get(
        "evaluated_decisions",
        0,
    )

    latest = (
        history[-1]
        if history
        else {}
    )

    latest_accuracy = latest.get(
        "accuracy"
    )

    latest_evaluated = latest.get(
        "evaluated_decisions"
    )

    should_save = (
        not history
        or latest_accuracy != accuracy
        or latest_evaluated != evaluated_decisions
    )

    if not should_save:
        return history

    snapshot = {
        "timestamp": datetime.now().isoformat(
            timespec="seconds"
        ),
        "accuracy": accuracy,
        "evaluated_decisions": evaluated_decisions,
        "correct_decisions": analytics.get(
            "correct_decisions",
            0,
        ),
        "incorrect_decisions": analytics.get(
            "incorrect_decisions",
            0,
        ),
        "learning_status": learning.get(
            "status"
        ),
    }

    history.append(snapshot)

    HISTORY_FILE.write_text(
        json.dumps(
            history,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return history
