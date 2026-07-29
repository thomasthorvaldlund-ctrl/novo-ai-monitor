from portfolio_summary_service import get_portfolio_summary


def get_rebalancing_analysis():
    """
    Analyserer porteføljens koncentration
    og foreslår mulige rebalanceringer.
    """

    portfolio = get_portfolio_summary()

    positions = portfolio.get("position_details", [])

    if not positions:
        return {
            "risk_level": "Ukendt",
            "message": "Ingen porteføljedata tilgængelig.",
            "largest_positions": [],
            "suggestions": [],
        }

    sorted_positions = sorted(
        positions,
        key=lambda x: float(
            str(x.get("weight_pct", "0"))
            .replace("%", "")
        ),
        reverse=True
    )

    largest_positions = sorted_positions[:3]

    top_weight = sum(
        float(
            str(p.get("weight_pct", "0"))
            .replace("%", "")
        )
        for p in largest_positions
    )

    if top_weight >= 80:
        risk_level = "Høj koncentration"
        message = (
            "Porteføljen er meget koncentreret "
            "i få positioner."
        )

    elif top_weight >= 60:
        risk_level = "Moderat koncentration"
        message = (
            "Porteføljen er koncentreret "
            "i få positioner."
        )

    else:
        risk_level = "Lav koncentration"
        message = (
            "Porteføljen har en god spredning."
        )

    suggestions = []

    if risk_level != "Lav koncentration":
        suggestions.append(
            "Overvej større diversificering over tid."
        )

    for position in largest_positions:
        if float(
            str(position.get("weight_pct", "0"))
            .replace("%", "")
        ) > 40:
            suggestions.append(
                f"{position['stock']} fylder meget i porteføljen."
            )

    suggestions.append(
        "Vurder nye køb ud fra samlet porteføljerisiko."
    )


    if risk_level == "Høj koncentration":
        ai_summary = (
            "Din portefølje har høj koncentration. "
            "AI vurderer, at en stor del af risikoen ligger i få positioner. "
            "Overvej at bruge fremtidige køb til at forbedre spredningen."
        )

    elif risk_level == "Moderat koncentration":
        ai_summary = (
            "Din portefølje har en moderat koncentration. "
            "AI anbefaler løbende overvågning af vægtningen "
            "og gradvis diversificering."
        )

    else:
        ai_summary = (
            "Din portefølje har en god spredning. "
            "AI vurderer ikke en væsentlig koncentrationsrisiko."
        )


    return {
        "risk_level": risk_level,
        "message": message,
        "largest_positions": largest_positions,
        "suggestions": suggestions,
        "portfolio_risk": portfolio.get("portfolio_risk"),
        "portfolio_comment": portfolio.get("portfolio_comment"),
        "ai_summary": ai_summary,
    }
