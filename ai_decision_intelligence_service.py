from ai_copilot_decision_service import get_copilot_decision
from ai_context_engine_service import get_ai_context


def get_decision_intelligence():
    """
    Samler Copilot beslutning og kontekst til en samlet AI vurdering.
    """

    decision = get_copilot_decision()
    context = get_ai_context()

    reasons = []

    reasons.append(
        f"AI handling: {decision['action']}."
    )

    reasons.append(
        f"AI confidence: {context['confidence']}."
    )

    reasons.append(
        f"Learning status: {context['learning_status']}."
    )

    if context["learning_samples"] < 5:
        reasons.append(
            "Datagrundlaget er begrænset og kræver flere observationer."
        )

    return {
        "headline": "AI Decision Intelligence",
        "action": decision["action"],
        "priority": decision["priority"],
        "risk": decision["risk"],
        "confidence": context["confidence"],
        "reasons": reasons,
    }
