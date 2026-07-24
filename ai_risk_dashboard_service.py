from ai_alerts_service import get_ai_alerts
from earnings_risk_service import get_earnings_risks
from portfolio import get_portfolio_summary


def calculate_level(score):
    if score >= 70:
        return "Høj"
    elif score >= 40:
        return "Moderat"
    else:
        return "Lav"


def get_ai_risk_dashboard():

    alerts = get_ai_alerts()
    earnings = get_earnings_risks()
    portfolio = get_portfolio_summary()


    earnings_score = 0

    for item in earnings:
        if item["alert_level"] == "HIGH":
            earnings_score += 80
        elif item["alert_level"] == "ALERT":
            earnings_score += 60
        elif item["alert_level"] == "WATCH":
            earnings_score += 30


    earnings_score = min(earnings_score, 100)


    alert_score = min(len(alerts) * 20, 100)


    portfolio_score = 40


    overall_score = int(
        (earnings_score + alert_score + portfolio_score) / 3
    )


    risk_reasons = []

    if len(alerts) > 0:
        risk_reasons.append(
            f"{len(alerts)} aktive AI alerts kræver overvågning."
        )

    if alert_score >= 60:
        risk_reasons.append(
            "Flere negative markeds- eller nyhedssignaler."
        )

    if earnings_score >= 60:
        risk_reasons.append(
            "Regnskabsrisiko påvirker den samlede vurdering."
        )

    if not risk_reasons:
        risk_reasons.append(
            "Ingen væsentlige risikofaktorer identificeret."
        )


    risk_explanation = (
        "AI vurderer risikoen som "
        f"{calculate_level(overall_score)}. "
        + " ".join(risk_reasons)
    )


    return {
        "overall_risk": calculate_level(overall_score),
        "risk_score": overall_score,

        "technical_risk": {
            "level": "Lav",
            "score": 30
        },

        "news_risk": {
            "level": calculate_level(alert_score),
            "score": alert_score
        },

        "earnings_risk": {
            "level": calculate_level(earnings_score),
            "score": earnings_score
        },

        "portfolio_risk": {
            "level": "Moderat",
            "score": portfolio_score
        },

        "risk_reasons": risk_reasons,

        "risk_explanation": risk_explanation,

        "ai_summary": (
            "AI vurderer risiko baseret på markedssignaler, "
            "nyheder, regnskaber og porteføljeeksponering."
        )
    }
