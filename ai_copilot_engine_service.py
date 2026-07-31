from ai_strategy_engine_service import get_ai_strategy
from ai_context_engine_service import get_ai_context


def get_ai_copilot():
    """
    Samler AI'ens strategi og kontekst til en samlet Copilot-vurdering.
    """

    strategy = get_ai_strategy()
    context = get_ai_context()

    key_points = []

    key_points.append(
        f"AI confidence niveau: {context['confidence']}."
    )

    key_points.append(
        f"Learning status: {context['learning_status']}."
    )

    if context["learning_samples"] < 5:
        key_points.append(
            "Datagrundlaget er stadig begrænset."
        )

    return {
        "headline": "AI Copilot",
        "strategy": strategy["strategy"],
        "confidence": context["confidence"],
        "summary": strategy["description"],
        "key_points": key_points,
    }
