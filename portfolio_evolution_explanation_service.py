"""
Aureum AI Portfolio Evolution Explanation Service

Omsætter Portfolio Evolution-data til en kort, deterministisk
og forklarlig tekst. Ingen eksterne API-kald.
"""


def _format_change(value):
    value = float(value)

    if value > 0:
        return f"+{value:.1f}"
    return f"{value:.1f}"


def explain_portfolio_evolution(evolution):
    """
    Returnerer en forklaring baseret direkte på evolution-data.
    """

    evolution = evolution or {}

    health = evolution.get("health", {})
    momentum = evolution.get("momentum", {})
    confidence = evolution.get("confidence", {})
    risk = evolution.get("risk", {})
    diversification = evolution.get("diversification", {})
    positions = evolution.get("positions", {})
    portfolio = evolution.get("portfolio", {})

    health_change = float(health.get("change", 0))
    momentum_change = float(momentum.get("change", 0))
    confidence_change = float(confidence.get("change", 0))
    risk_change = float(risk.get("change", 0))
    diversification_change = float(
        diversification.get("change", 0)
    )
    position_change = int(positions.get("change", 0))

    positive_factors = []
    negative_factors = []

    if momentum_change > 0:
        positive_factors.append(
            f"Momentum steg {momentum_change:.1f} point"
        )
    elif momentum_change < 0:
        negative_factors.append(
            f"Momentum faldt {abs(momentum_change):.1f} point"
        )

    if confidence_change > 0:
        positive_factors.append(
            f"AI-confidence steg {confidence_change:.1f} point"
        )
    elif confidence_change < 0:
        negative_factors.append(
            f"AI-confidence faldt {abs(confidence_change):.1f} point"
        )

    if risk_change > 0:
        positive_factors.append(
            f"Risikoscoren steg {risk_change:.1f} point"
        )
    elif risk_change < 0:
        negative_factors.append(
            f"Risikoscoren faldt {abs(risk_change):.1f} point"
        )

    if diversification_change > 0:
        positive_factors.append(
            f"Diversifikationsscoren steg "
            f"{diversification_change:.1f} point"
        )
    elif diversification_change < 0:
        negative_factors.append(
            f"Diversifikationsscoren faldt "
            f"{abs(diversification_change):.1f} point"
        )

    if health_change > 0:
        headline = (
            f"Portfolio Health steg "
            f"{health_change:.1f} point."
        )
    elif health_change < 0:
        headline = (
            f"Portfolio Health faldt "
            f"{abs(health_change):.1f} point."
        )
    else:
        headline = "Portfolio Health var uændret."

    details = []

    if positive_factors:
        details.append(
            "Positive faktorer: "
            + ", ".join(positive_factors)
            + "."
        )

    if negative_factors:
        details.append(
            "Negative faktorer: "
            + ", ".join(negative_factors)
            + "."
        )

    added = portfolio.get("added", [])
    removed = portfolio.get("removed", [])

    if added:
        details.append(
            "Nye positioner: "
            + ", ".join(added)
            + "."
        )

    if removed:
        details.append(
            "Fjernede positioner: "
            + ", ".join(removed)
            + "."
        )

    if position_change != 0:
        direction = "faldt" if position_change < 0 else "steg"
        details.append(
            f"Antallet af positioner {direction} "
            f"med {abs(position_change)}."
        )

    if health_change > 0.5:
        overall_status = "Forbedret"
        overall_assessment = (
            f"Portfolio Health steg {health_change:.1f} point"
            + (
                f", primært understøttet af Momentum, som steg "
                f"{momentum_change:.1f} point."
                if momentum_change > 0
                else "."
            )
        )
    elif health_change < -0.5:
        overall_status = "Forværret"
        overall_assessment = (
            f"Portfolio Health faldt {abs(health_change):.1f} point"
            + (
                f", blandt andet fordi Momentum faldt "
                f"{abs(momentum_change):.1f} point."
                if momentum_change < 0
                else "."
            )
        )
    else:
        overall_status = "Uændret"
        overall_assessment = (
            "Portfolio Health er stort set uændret."
        )

    if not details:
        details.append(
            "Der blev ikke registreret væsentlige ændringer "
            "i de målte Portfolio Health-komponenter."
        )

    return {
        "headline": headline,
        "summary": " ".join(details),
        "health_change": health_change,
        "positive_factors": positive_factors,
        "negative_factors": negative_factors,
        "added_positions": added,
        "removed_positions": removed,
        "position_change": position_change,
        "overall_status": overall_status,
        "overall_assessment": overall_assessment,
    }
