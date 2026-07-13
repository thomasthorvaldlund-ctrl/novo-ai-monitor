import json
from datetime import datetime

from ai_analyst_service import get_ai_analyst
from combined_score_service import combined_stock_score
from top_picks_service import get_top_picks
from openai_service import client
from market_score_service import get_market_score
from market_summary_service import get_market_summary
from ai_alerts_service import get_ai_alerts
from portfolio_summary_service import get_portfolio_summary
from system_health_service import get_system_health
from morning_brief_service import get_morning_brief
from performance_service import get_signal_statistics
from dashboard_cache_service import save_dashboard_cache
from news_sentiment_service import get_ai_news_sentiment
from market_score_history_service import save_market_score
from ai_explain_service import explain_stock

def build_dashboard_cache():

    combined_data = combined_stock_score(client)
    ranking = combined_data.get("combined_ranking", [])
    
    stock_explanations = [
        explain_stock(stock)
        for stock in ranking
    ]

    market = get_market_score(ranking)

    save_market_score(
        market.get("score", 50),
        market.get("status", "Neutral"),
    )
    
    data = {
    "updated_at": datetime.now().strftime("%d-%m-%Y %H:%M"),
    "market": get_market_score(ranking),
    "summary": get_market_summary(),
    "alerts": get_ai_alerts(),
    "portfolio": get_portfolio_summary(),
    "system_health": get_system_health(),
    "top_picks": get_top_picks(ranking),
    "analyst": get_ai_analyst(),
    "morning_brief": get_morning_brief(),
    "performance": get_signal_statistics(),
    "ai_news": get_ai_news_sentiment(),
    "stock_explanations": stock_explanations,
}

    save_dashboard_cache(data)

    return data

if __name__ == "__main__":
    build_dashboard_cache()
    print("Dashboard cache updated.")