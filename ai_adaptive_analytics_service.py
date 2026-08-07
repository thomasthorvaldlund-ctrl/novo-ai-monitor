import json
from pathlib import Path
from collections import defaultdict


ADAPTIVE_HISTORY_FILE = Path(
    "adaptive_decision_history.json"
)


def load_adaptive_history():
    """
    Henter adaptive beslutningshistorik.
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


def get_adaptive_regime_analysis():
    """
    Analyserer adaptive ændringer pr. markedsregime.
    """

    history = load_adaptive_history()

    regimes = defaultdict(
        lambda: {
            "simulations": 0,
            "changes": 0
        }
    )

    for item in history:

        regime = item.get(
            "market_regime",
            "Unknown"
        )

        regimes[regime]["simulations"] += 1

        if item.get(
            "learning_changed_signal"
        ):
            regimes[regime]["changes"] += 1


    analysis = {}

    for regime, data in regimes.items():

        simulations = data["simulations"]
        changes = data["changes"]

        change_rate = (
            round(
                changes / simulations * 100,
                1
            )
            if simulations
            else 0
        )

        analysis[regime] = {
            "simulations": simulations,
            "changes": changes,
            "change_rate": change_rate
        }


    return analysis
