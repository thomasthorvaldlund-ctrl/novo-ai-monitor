import json
from pathlib import Path


HISTORY_FILE = Path("ai_maturity_history.json")


def load_maturity_history():
    """
    Henter AI Maturity historik.
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


def get_ai_maturity_trend():
    """
    Beregner udviklingen i AI Maturity.
    """

    history = load_maturity_history()

    if not history:
        return {
            "current_score": 0,
            "previous_score": 0,
            "change": 0,
            "trend": "No data"
        }

    current = history[-1]

    previous = (
        history[-2]
        if len(history) > 1
        else history[-1]
    )

    current_score = current.get(
        "score",
        0
    )

    previous_score = previous.get(
        "score",
        0
    )

    change = current_score - previous_score

    if change > 0:
        trend = "Improving"
    elif change < 0:
        trend = "Declining"
    else:
        trend = "Stable"


    components = current.get(
        "components",
        {}
    )

    if components:
        strongest_component = max(
            components,
            key=components.get
        )

        weakest_component = min(
            components,
            key=components.get
        )
    else:
        strongest_component = None
        weakest_component = None


    return {
        "current_score": current_score,
        "previous_score": previous_score,
        "change": change,
        "trend": trend,
        "strongest_component": strongest_component,
        "weakest_component": weakest_component
    }
