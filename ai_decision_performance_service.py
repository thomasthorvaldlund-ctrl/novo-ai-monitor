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

    action_sequence = [
        item.get("action", "UNKNOWN")
        for item in history
    ]

    actions = Counter(action_sequence)

    action_changes = sum(
        1
        for previous, current in zip(
            action_sequence,
            action_sequence[1:]
        )
        if current != previous
    )

    transition_count = max(
        len(action_sequence) - 1,
        0
    )

    action_stability_pct = (
        round(
            (
                (transition_count - action_changes)
                / transition_count
            ) * 100,
            1,
        )
        if transition_count
        else 100.0
    )

    unique_actions = sorted(
        set(action_sequence)
    )


    top_pick_sequence = [
        item.get("stock")
        for item in history
        if item.get("stock")
    ]

    top_pick_changes = sum(
        1
        for previous, current in zip(
            top_pick_sequence,
            top_pick_sequence[1:]
        )
        if current != previous
    )

    top_pick_transition_count = max(
        len(top_pick_sequence) - 1,
        0
    )

    top_pick_stability_pct = (
        round(
            (
                (
                    top_pick_transition_count
                    - top_pick_changes
                )
                / top_pick_transition_count
            ) * 100,
            1,
        )
        if top_pick_transition_count
        else 100.0
    )

    unique_top_picks = sorted(
        set(top_pick_sequence)
    )

    top_pick_rows = [
        item
        for item in history
        if item.get("stock")
        and isinstance(
            item.get("score"),
            (int, float),
        )
    ]

    same_top_pick_score_changes = sum(
        1
        for previous, current in zip(
            top_pick_rows,
            top_pick_rows[1:]
        )
        if previous.get("stock") == current.get("stock")
        and previous.get("score") != current.get("score")
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
        # Legacy-navn: beholdes for kompatibilitet.
        "total_decisions": len(history),

        # Explicit Performance v2 metrics.
        "snapshot_count": len(history),
        "action_changes": action_changes,
        "unique_actions": unique_actions,
        "action_stability_pct": action_stability_pct,

        "top_pick_samples": len(top_pick_sequence),
        "top_pick_changes": top_pick_changes,
        "unique_top_picks": unique_top_picks,
        "top_pick_stability_pct": top_pick_stability_pct,
        "same_top_pick_score_changes": same_top_pick_score_changes,

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
