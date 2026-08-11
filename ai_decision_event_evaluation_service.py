from ai_decision_event_service import get_closed_decision_events


def evaluate_decision_event(event):
    """
    Evaluerer et lukket beslutningsevent.

    Returnerer outcome og forklaring uden at ændre
    selve eventhistorikken.
    """

    action = event.get("action")
    performance = event.get("performance_pct")
    reason = event.get("reason")

    if performance is None:
        return {
            "outcome": "NOT_EVALUABLE",
            "evaluation_explanation": "Manglende performance.",
        }

    if action == "HOLD":
        if performance < -5:
            return {
                "outcome": "INCORRECT",
                "evaluation_explanation": (
                    "HOLD blev efterfulgt af et fald større end 5%."
                ),
            }

        if performance > 5:
            return {
                "outcome": "CORRECT",
                "evaluation_explanation": (
                    "HOLD bevarede eksponeringen under en stærk "
                    "positiv udvikling."
                ),
            }

        return {
            "outcome": "CORRECT",
            "evaluation_explanation": (
                "HOLD blev efterfulgt af en stabil kursudvikling."
            ),
        }

    if action == "REDUCE":
        if reason == "Svage AI signaler.":
            if performance <= 0:
                return {
                    "outcome": "CORRECT",
                    "evaluation_explanation": (
                        "Svage signaler blev efterfulgt af flad "
                        "eller negativ udvikling."
                    ),
                }

            return {
                "outcome": "INCORRECT",
                "evaluation_explanation": (
                    "REDUCE blev efterfulgt af positiv kursudvikling."
                ),
            }

        if reason == "Positionen fylder for meget i porteføljen.":
            return {
                "outcome": "RISK_MANAGEMENT",
                "evaluation_explanation": (
                    "REDUCE skyldtes koncentrationsrisiko og "
                    "vurderes separat."
                ),
            }

        return {
            "outcome": "NOT_EVALUABLE",
            "evaluation_explanation": "Ukendt REDUCE-årsag.",
        }

    if action == "WATCH":
        if -5 <= performance <= 5:
            return {
                "outcome": "CORRECT",
                "evaluation_explanation": (
                    "WATCH blev efterfulgt af en bevægelse "
                    "inden for ±5%."
                ),
            }

        if performance > 5:
            return {
                "outcome": "INCORRECT",
                "evaluation_explanation": (
                    "WATCH undervurderede en stærk positiv bevægelse."
                ),
            }

        return {
            "outcome": "INCORRECT",
            "evaluation_explanation": (
                "WATCH undervurderede en stærk negativ bevægelse."
            ),
        }

    return {
        "outcome": "NOT_EVALUABLE",
        "evaluation_explanation": "Action understøttes ikke.",
    }


def get_evaluated_decision_events():
    """
    Returnerer alle lukkede beslutningsevents med evaluering.
    """

    evaluated = []

    for event in get_closed_decision_events():
        evaluation = evaluate_decision_event(event)

        evaluated.append({
            **event,
            **evaluation,
        })

    return evaluated
