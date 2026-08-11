import json
from pathlib import Path
from collections import Counter


HISTORY_FILE = Path("ai_decision_history.json")


def load_decision_history():
    """
    Henter AI beslutningshistorik.
    """

    if not HISTORY_FILE.exists():
        return []

    with open(
        HISTORY_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)



def get_decision_performance():
    """
    Beregner grundlæggende AI Decision statistik.
    """

    history = load_decision_history()

    actions = Counter(
        item.get("action", "UNKNOWN")
        for item in history
    )

    # Legacy confidence-felt.
    # Beholdes midlertidigt for bagudkompatibilitet.
    confidence = Counter(
        item.get("confidence", "UNKNOWN")
        for item in history
    )

    decision_confidence = Counter()
    context_confidence = Counter()

    for item in history:
        explicit_decision = item.get("decision_confidence")
        explicit_context = item.get("context_confidence")
        legacy_confidence = item.get("confidence")

        # Nye snapshots har eksplicit Decision Confidence.
        if explicit_decision is not None:
            decision_confidence[explicit_decision] += 1

        # Ældre numeriske confidence-værdier repræsenterer
        # Decision Confidence.
        elif isinstance(legacy_confidence, (int, float)):
            decision_confidence[legacy_confidence] += 1

        # Nye snapshots har eksplicit Context Confidence.
        if explicit_context is not None:
            context_confidence[explicit_context] += 1

        # Ældre tekstbaserede confidence-værdier repræsenterer
        # Context Confidence.
        elif isinstance(legacy_confidence, str):
            context_confidence[legacy_confidence] += 1

    return {
        "total_decisions": len(history),
        "buy": actions["BUY"],
        "hold": actions["HOLD"],
        "reduce": actions["REDUCE"],
        "confidence_levels": dict(confidence),
        "decision_confidence_levels": dict(decision_confidence),
        "context_confidence_levels": dict(context_confidence),
        "status": (
            "For lidt data"
            if len(history) < 10
            else "Klar til analyse"
        ),
    }
