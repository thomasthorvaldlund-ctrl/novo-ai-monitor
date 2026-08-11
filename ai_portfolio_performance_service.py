from ai_decision_event_evaluation_service import (
    get_evaluated_decision_events,
)


EVALUABLE_OUTCOMES = {
    "CORRECT",
    "INCORRECT",
}


OUTCOME_LABELS = {
    "CORRECT": "Korrekt",
    "INCORRECT": "Forkert",
}


def get_portfolio_performance():
    """
    Returnerer historisk performance for lukkede
    Decision Events v2.

    Hver række beskriver perioden fra den oprindelige
    AI-beslutning til den efterfølgende beslutning,
    hvor eventet blev lukket og evalueret.
    """

    events = get_evaluated_decision_events()

    performance = []

    for event in events:
        outcome = event.get("outcome")

        if outcome not in EVALUABLE_OUTCOMES:
            continue

        performance.append({
            "stock": event.get("stock"),
            "action": event.get("action"),
            "score": event.get("score"),

            "decision_price": event.get(
                "decision_price"
            ),

            "end_price": event.get(
                "end_price"
            ),

            "performance_pct": event.get(
                "performance_pct"
            ),

            "ai_result": OUTCOME_LABELS.get(
                outcome,
                outcome,
            ),

            "outcome": outcome,

            "evaluation_explanation": event.get(
                "evaluation_explanation"
            ),

            "decision_date": event.get(
                "date"
            ),

            "end_date": event.get(
                "end_date"
            ),

            "duration_minutes": event.get(
                "duration_minutes"
            ),

            "next_action": event.get(
                "next_action"
            ),
        })

    return performance
