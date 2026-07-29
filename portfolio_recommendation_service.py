from portfolio_ai_service import get_portfolio_ai_insights
from portfolio_explanation_service import generate_portfolio_explanation


def generate_portfolio_recommendations():
    """
    Genererer anbefalinger for brugerens portefølje.
    """

    insights = get_portfolio_ai_insights()

    recommendations = []

    for item in insights:

        score = item.get("combined_score", 0)
        weight = item.get("weight_pct", 0)

        if score >= 75 and weight < 40:
            recommendation = "BUY"
            reason = "Stærk AI score og plads i porteføljen."

        elif weight >= 60:
            recommendation = "REDUCE"
            reason = "Positionen fylder for meget i porteføljen."

        elif score < 50:
            recommendation = "REDUCE"
            reason = "Svage AI signaler."

        elif score >= 60:
            recommendation = "HOLD"
            reason = "Stabil AI vurdering."

        else:
            recommendation = "WATCH"
            reason = "Bør overvåges."


        explanation = generate_portfolio_explanation({
            **item,
            "recommendation": recommendation,
            "score": score,
        })


        recommendations.append({
            "stock": item["stock"],
            "recommendation": recommendation,
            "reason": reason,
            "score": score,
            "weight_pct": weight,
            "profit_pct": item.get("profit_pct"),
            "technical_score": item.get("technical_score"),
            "news_score": item.get("news_score"),
            "concentration_risk": item.get("concentration_risk"),
            "explanation": explanation,
        })


    return recommendations
