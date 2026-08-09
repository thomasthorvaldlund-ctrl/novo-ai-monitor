def get_ai_maturity_explanation(trend_data):
    """
    Forklarer AI Maturity udviklingen.
    """

    score = trend_data.get(
        "current_score",
        0
    )

    trend = trend_data.get(
        "trend",
        "Unknown"
    )

    strongest = trend_data.get(
        "strongest_component"
    )

    weakest = trend_data.get(
        "weakest_component"
    )


    if score >= 80:
        headline = (
            "AI systemet er i Advanced Learning Phase."
        )
    elif score >= 60:
        headline = (
            "AI systemet er i Developing Learning Phase."
        )
    else:
        headline = (
            "AI systemet er i Early Learning Phase."
        )


    strength = (
        f"Stærkeste område: {strongest}."
        if strongest
        else "Ingen styrke identificeret endnu."
    )


    weakness = (
        f"Forbedringsområde: {weakest}."
        if weakest
        else "Ingen forbedringsområde identificeret endnu."
    )


    if trend == "Improving":
        recommendation = (
            "AI systemets kvalitet udvikler sig positivt."
        )
    elif trend == "Declining":
        recommendation = (
            "AI bør fokusere på at forbedre de svageste områder."
        )
    else:
        recommendation = (
            "AI systemet holder et stabilt niveau."
        )


    return {
        "score": score,
        "trend": trend,
        "headline": headline,
        "strength": strength,
        "weakness": weakness,
        "recommendation": recommendation,
    }
