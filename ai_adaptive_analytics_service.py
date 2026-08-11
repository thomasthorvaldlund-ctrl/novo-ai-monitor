from collections import defaultdict

from ai_adaptive_history_service import load_adaptive_history


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
