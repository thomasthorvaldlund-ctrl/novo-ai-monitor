from combined_score_service import combined_stock_score
from portfolio_stock_service import get_monitored_stock_names
from openai_service import client
from ai_explain_service import explain_stock


def get_portfolio_ai_insights():
    """
    Returnerer AI-analyse af brugerens egne porteføljeaktier.
    """

    portfolio_names = get_monitored_stock_names()

    combined_data = combined_stock_score(client)
    ranking = combined_data.get("combined_ranking", [])

    insights = []

    for stock in ranking:
        if stock.get("stock") in portfolio_names:
            explanation = explain_stock(stock)

            insights.append({
                "stock": stock.get("stock"),
                "combined_score": stock.get("combined_score"),
                "rating": stock.get("rating"),
                "technical_score": stock.get("technical_score"),
                "news_score": stock.get("news_score"),
                "explanation": explanation,
            })

    return insights
