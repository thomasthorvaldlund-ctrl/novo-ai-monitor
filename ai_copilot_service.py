def get_ai_copilot(
    market,
    portfolio,
    top_picks,
    alerts,
    stock_explanations,
    performance,
):
    """
    AI Copilot samler eksisterende AI-signaler
    og laver en samlet investorvurdering.
    Første version er regelbaseret.
    """

    market_score = 0

    if isinstance(market, dict):
        market_score = market.get("score", 50)

    # Markedsstatus
    if market_score >= 70:
        market_status = "Positiv markedsvurdering"
        market_text = "Markedet viser stærke signaler."
        risk_level = "Lav"
    elif market_score >= 50:
        market_status = "Neutral markedsvurdering"
        market_text = "Markedet viser blandede signaler."
        risk_level = "Moderat"
    else:
        market_status = "Forsigtig markedsvurdering"
        market_text = "Markedet viser svagere signaler."
        risk_level = "Høj"


    # Bedste mulighed
    if top_picks:
        top = top_picks[0]

        best_stock = top.get(
            "stock",
            "Ingen"
        )

        best_score = top.get(
            "score",
            "-"
        )

        best_opportunity = (
            f"{best_stock} er stærkeste kandidat "
            f"med AI Score {best_score}."
        )

    else:
        best_opportunity = (
            "Ingen klar kandidat identificeret."
        )


    # Alerts
    critical_alerts = [
        alert
        for alert in (alerts or [])
        if alert.get("level") != "green"
    ]

    if critical_alerts:
        risk_warning = (
            f"{len(critical_alerts)} aktive alerts "
            "kræver overvågning."
        )
    else:
        risk_warning = (
            "Ingen kritiske AI-alerts registreret."
        )


    # Portfolio
    if isinstance(portfolio, dict):

        positions = portfolio.get(
            "positions",
            0
        )

        portfolio_comment = (
            f"Porteføljen indeholder {positions} positioner."
        )

    else:
        portfolio_comment = (
            "Ingen porteføljedata tilgængelig."
        )


    # Performance
    buy_count = 0

    if isinstance(performance, dict):
        buy_count = performance.get(
            "buy",
            0
        )


    if buy_count > 0 and market_score >= 60:
        recommendation = (
            "Systemet understøtter selektive køb "
            "af stærke kandidater."
        )
    elif market_score < 50:
        recommendation = (
            "Afvent nye køb og overvåg markedet tæt."
        )
    else:
        recommendation = (
            "Behold kvalitetspositioner og følg signalerne."
        )


    confidence = 80

    if stock_explanations:
        first = stock_explanations[0]

        confidence = first.get(
            "confidence",
            80
        )


    # AI reasoning factors
    factors = []

    factors.append(
        f"Market Score: {market_score}"
    )

    if top_picks:
        factors.append(
            f"Top kandidat: {best_stock}"
        )

    if isinstance(performance, dict):
        factors.append(
            f"{performance.get('buy', 0)} BUY-signaler registreret"
        )

        factors.append(
            f"{performance.get('hold', 0)} HOLD-signaler registreret"
        )

    if critical_alerts:
        factors.append(
            f"{len(critical_alerts)} aktive AI-alerts"
        )
    else:
        factors.append(
            "Ingen kritiske AI-alerts"
        )

    if isinstance(portfolio, dict):
        factors.append(
            f"Portfolio: {positions} positioner"
        )


    return {
        "headline": market_status,
        "market_status": market_text,
        "best_opportunity": best_opportunity,
        "risk_warning": risk_warning,
        "portfolio_comment": portfolio_comment,
        "recommendation": recommendation,
        "confidence": confidence,
        "risk_level": risk_level,
        "factors": factors,
    }
