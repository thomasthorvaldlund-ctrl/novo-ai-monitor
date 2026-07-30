from ai_context_engine_service import get_ai_context


def get_ai_strategy():
    """
    Returnerer AI'ens overordnede investeringsstrategi.
    """

    context = get_ai_context()

    confidence = context["confidence"]
    accuracy = context["prediction_accuracy"]

    if confidence == "High" and accuracy >= 80:
        strategy = "Aggressiv"
        description = "AI'en vurderer, at markedsforholdene understøtter en offensiv strategi."

    elif confidence == "Medium":
        strategy = "Neutral"
        description = "AI'en anbefaler en balanceret strategi med moderat risiko."

    else:
        strategy = "Defensiv"
        description = "AI'en anbefaler en forsigtig strategi, indtil datagrundlaget bliver stærkere."

    return {
        "strategy": strategy,
        "description": description,
        "confidence": confidence,
        "prediction_accuracy": accuracy,
    }
