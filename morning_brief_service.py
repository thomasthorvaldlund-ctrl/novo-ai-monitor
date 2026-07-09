from market_score_service import get_market_score
from portfolio_summary_service import get_portfolio_summary
from top_picks_service import get_top_picks
from system_health_service import get_system_health
from ai_alerts_service import get_ai_alerts
from combined_score_service import combined_stock_score
from openai_service import client


def get_morning_brief():
    ranking = combined_stock_score(client)["combined_ranking"]

    market = get_market_score()
    portfolio = get_portfolio_summary()
    top_picks = get_top_picks(ranking)
    alerts = get_ai_alerts()
    health = get_system_health()

    top = top_picks[0] if top_picks else None

    return {
        "market": market,
        "portfolio": portfolio,
        "top_pick": top,
        "alerts": alerts,
        "health": health,
    }