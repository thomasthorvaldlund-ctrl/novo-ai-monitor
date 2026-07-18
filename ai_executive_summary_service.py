"""
AI Executive Summary Service

Samler de vigtigste dashboard-data og genererer en kort
AI-opsummering til Executive Summary i Stock AI Monitor v2.
"""


def get_ai_executive_summary(
    market=None,
    top_picks=None,
    portfolio=None,
    alerts=None,
    stock_explanations=None,
):
    """
    Returnerer en samlet Executive Summary.

    Første version er regelbaseret.
    Senere kan den udvides med GPT.
    """

    market_score = (
        market.get("score", 0)
        if isinstance(market, dict)
        else 0
    )

    top_pick = (
        top_picks[0].get("stock", "Ingen")
        if top_picks
        else "Ingen"
    )

    portfolio_positions = (
        portfolio.get("positions", 0)
        if isinstance(portfolio, dict)
        else 0
    )

    alert_count = len(alerts) if alerts else 0

    if market_score >= 70:
        headline = "🟢 Positiv markedsvurdering"
        risk = "Lav"
    elif market_score >= 40:
        headline = "🟡 Neutral markedsvurdering"
        risk = "Moderat"
    else:
        headline = "🔴 Forsigtig markedsvurdering"
        risk = "Høj"

    if alert_count == 1:
        alert_text = "1 aktiv AI-alert"
    else:
        alert_text = f"{alert_count} aktive AI-alerts"

    if market_score >= 70:
        market_comment = (
            "Markedet viser stærke signaler med positivt momentum."
        )
    elif market_score >= 40:
        market_comment = (
            "Markedet vurderes som neutralt med blandede signaler."
        )
    else:
        market_comment = (
            "Markedet viser svagere signaler og kræver ekstra forsigtighed."
        )

    explain_text = ""

    if stock_explanations:
        first_explain = stock_explanations[0]

        if isinstance(first_explain, dict):
            score = first_explain.get("score", "")
            positives = first_explain.get("positives", [])
            negatives = first_explain.get("negatives", [])
            primary_reason = first_explain.get("primary_reason", "")
            headline = first_explain.get("headline", "")

            explain_text = (
                f"{headline} med en Combined Score på {score}. "
            )

            if primary_reason:
                explain_text += (
                    f"Primær årsag: {primary_reason}. "
                )

            if positives:
                explain_text += (
                    "Positive faktorer: "
                    + ", ".join(positives[:2])
                    + ". "
                )

            if not negatives:
                explain_text += (
                    "Ingen væsentlige negative signaler identificeret."
                )
            else:
                explain_text += (
                    "Forhold der bør overvåges: "
                    + ", ".join(negatives[:2])
                    + "."
                )

    summary = (
        f"{market_comment} "
        f"Dagens stærkeste kandidat er {top_pick} baseret på "
        f"den samlede AI-vurdering. "
        f"Porteføljen består af {portfolio_positions} positioner "
        f"og der er {alert_text}, som bør overvåges."
    )

    if explain_text:
        summary += " " + explain_text

    recommendation = (
        f"AI anbefaler fokus på {top_pick} samt løbende overvågning "
        "af markedets udvikling og aktive alerts før nye investeringer."
    )

    return {
        "headline": headline,
        "summary": summary,
        "recommendation": recommendation,
        "risk_level": risk,
        "confidence": 80,
    }
