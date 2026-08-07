import json
from pathlib import Path
from collections import Counter


HISTORY_FILE = Path(
    "adaptive_decision_history.json"
)


def load_adaptive_history():
    if not HISTORY_FILE.exists():
        return []

    with open(
        HISTORY_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


def get_adaptive_behavior():

    history = load_adaptive_history()

    if not history:
        return {
            "status": "No adaptive history"
        }

    changes = []

    regimes = Counter()
    modes = Counter()

    for item in history:

        before = item.get(
            "calculated_signal_before_learning"
        )

        after = item.get(
            "calculated_signal_after_learning"
        )

        if before and after:
            if before != after:
                changes.append(
                    f"{before}_to_{after}"
                )

        regime = item.get(
            "market_regime"
        )

        if regime:
            regimes[regime] += 1

        mode = item.get(
            "decision_mode"
        )

        if mode:
            modes[mode] += 1


    total = len(history)

    change_rate = round(
        len(changes) / total * 100,
        1
    ) if total else 0


    most_common_change = (
        Counter(changes).most_common(1)[0][0]
        if changes
        else "None"
    )


    style = (
        modes.most_common(1)[0][0]
        if modes
        else "Unknown"
    )


    return {
        "total_records": total,

        "change_behavior": {
            "total_changes": len(changes),
            "most_common_change": most_common_change,
            "change_rate": change_rate,
        },

        "decision_style": {
            "style": style,
        },

        "regime_behavior": dict(regimes),

        "summary":
            f"AI ændrer primært signaler via {most_common_change}."
    }
