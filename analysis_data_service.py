from combined_score_service import combined_stock_score
from market_score_service import get_market_score
from market_summary_service import get_market_summary
from ai_alerts_service import get_ai_alerts
from portfolio_summary_service import get_portfolio_summary
from top_picks_service import get_top_picks
from openai_service import client


def build_analysis_data():
    market = get_market_score()
    summary = get_market_summary()
    alerts = get_ai_alerts()
    portfolio = get_portfolio_summary()

    combined = combined_stock_score(client)
    ranking = combined.get("combined_ranking", [])

    top_picks = get_top_picks(ranking)

    return {
        "market": market,
        "summary": summary,
        "alerts": alerts,
        "portfolio": portfolio,
        "ranking": ranking,
        "top_picks": top_picks,
    }