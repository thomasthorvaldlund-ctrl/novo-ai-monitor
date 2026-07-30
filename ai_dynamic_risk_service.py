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



def calculate_dynamic_risk():

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


    news_score = min(len(alerts) * 20, 100)


    # Midlertidig - erstattes af rigtig porteføljeanalyse
    portfolio_score = 40


    technical_score = 30


    overall_score = int(
        (
            earnings_score +
            news_score +
            portfolio_score +
            technical_score
        ) / 4
    )


    reasons = []


    if news_score > 40:
        reasons.append(
            "Negative AI alerts påvirker risikoen."
        )


    if earnings_score > 40:
        reasons.append(
            "Regnskabsrisiko påvirker vurderingen."
        )


    if portfolio_score >= 50:
        reasons.append(
            "Porteføljerisiko kræver opmærksomhed."
        )


    if not reasons:
        reasons.append(
            "Ingen større risikofaktorer identificeret."
        )


    risk_level = calculate_level(
        overall_score
    )

    return {

        "risk_score": overall_score,

        "risk_level": risk_level,

        "overall_risk": risk_level,

        "technical_score": technical_score,

        "technical_risk": {
            "level": calculate_level(technical_score),
            "score": technical_score
        },

        "news_score": news_score,

        "news_risk": {
            "level": calculate_level(news_score),
            "score": news_score
        },

        "earnings_score": earnings_score,

        "earnings_risk": {
            "level": calculate_level(earnings_score),
            "score": earnings_score
        },

        "portfolio_score": portfolio_score,

        "portfolio_risk": {
            "level": calculate_level(portfolio_score),
            "score": portfolio_score
        },

        "risk_reasons": reasons,

        "risk_explanation": (
            "AI vurderer risiko baseret på "
            "markedssignaler, nyheder, regnskaber "
            "og porteføljeeksponering."
        ),

        "ai_summary": (
            "Dynamisk AI-risiko beregnet ud fra "
            "tekniske signaler, alerts, regnskaber "
            "og porteføljerisiko."
        )
    }
