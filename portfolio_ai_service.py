from combined_score_service import combined_stock_score
from portfolio_stock_service import get_monitored_stock_names
from portfolio import get_portfolio_summary
from openai_service import client
from ai_explain_service import explain_stock


def get_portfolio_ai_insights():
    """
    Returnerer AI-analyse af brugerens egne porteføljeaktier.
    """

    portfolio_names = get_monitored_stock_names()

    portfolio_data = get_portfolio_summary()

    portfolio_positions = {
        position["stock"]: position
        for position in portfolio_data.get("positions", [])
    }

    combined_data = combined_stock_score(client)
    ranking = combined_data.get("combined_ranking", [])

    insights = []

    for stock in ranking:
        if stock.get("stock") in portfolio_names:
            explanation = explain_stock(stock)

            position = portfolio_positions.get(
                stock.get("stock"),
                {}
            )

            insights.append({
                "stock": stock.get("stock"),
                "ticker": position.get("ticker"),
                "qty": position.get("qty"),
                "value_dkk": position.get("value_dkk"),
                "profit_dkk": position.get("profit_dkk"),
                "profit_pct": position.get("profit_pct"),
                "weight_pct": position.get("weight_pct"),
                "combined_score": stock.get("combined_score"),
                "rating": stock.get("rating"),
                "technical_score": stock.get("technical_score"),
                "news_score": stock.get("news_score"),
                "explanation": explanation,
            })

    return insights
