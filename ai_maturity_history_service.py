import json
from pathlib import Path
from datetime import datetime


HISTORY_FILE = Path("ai_maturity_history.json")


def load_ai_maturity_history():
    """
    Henter historik for AI Maturity.
    """

    if not HISTORY_FILE.exists():
        return []

    try:
        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)

    except Exception:
        return []


def save_ai_maturity_snapshot(maturity_data):
    """
    Gemmer et AI Maturity snapshot.
    """

    history = load_ai_maturity_history()

    snapshot = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "score": maturity_data.get("score", 0),
        "level": maturity_data.get("level", ""),
        "adaptation": maturity_data.get(
            "components",
            {}
        ).get("adaptation", 0),
        "learning_activity": maturity_data.get(
            "components",
            {}
        ).get("learning_activity", 0),
        "data_quality": maturity_data.get(
            "components",
            {}
        ).get("data_quality", 0),
        "explanation_confidence": maturity_data.get(
            "components",
            {}
        ).get("explanation_confidence", 0),

        "components": maturity_data.get(
            "components",
            {}
        ),
    }

    # Undgå flere snapshots samme dag
    if history and history[-1].get("date") == snapshot["date"]:
        history[-1] = snapshot
    else:
        history.append(snapshot)

    with open(
        HISTORY_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            history,
            f,
            indent=2,
            ensure_ascii=False
        )

    return snapshot
