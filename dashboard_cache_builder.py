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
from news_sentiment_service import (
    get_ai_news_sentiment,
    get_news_sentiment,
)
from earnings_intelligence_service import get_earnings_summary
from earnings_ai_service import analyze_earnings_articles
from market_score_history_service import save_market_score
from ai_explain_service import explain_stock
from today_take_service import get_today_take
from ai_executive_summary_service import get_ai_executive_summary
from ai_copilot_service import get_ai_copilot
from ai_copilot_history_service import (
    save_copilot_snapshot,
    load_copilot_history,
)
from ai_copilot_change_service import compare_copilot_snapshots
from ai_copilot_timeline_service import get_copilot_timeline

def build_dashboard_cache():

    combined_data = combined_stock_score(client)
    ranking = combined_data.get("combined_ranking", [])
    
    stock_explanations = [
        explain_stock(stock)
        for stock in ranking
    ]

    market = get_market_score(ranking)
    top_picks = get_top_picks(ranking)
    performance = get_signal_statistics()

    news_data = get_news_sentiment()
    ai_news = get_ai_news_sentiment(news_data)
    earnings = get_earnings_summary(
        news_data.get("articles", [])
    )

    earnings_ai = analyze_earnings_articles(
        earnings.get("latest_company_reports", [])
    )

    top_pick = top_picks[0] if top_picks else None

    portfolio = get_portfolio_summary()
    alerts = get_ai_alerts()

    executive_summary = get_ai_executive_summary(
        market=market,
        top_picks=top_picks,
        portfolio=portfolio,
        alerts=alerts,
        stock_explanations=stock_explanations,
    )

    ai_copilot = get_ai_copilot(
        market=market,
        portfolio=portfolio,
        top_picks=top_picks,
        alerts=alerts,
        stock_explanations=stock_explanations,
        performance=performance,
    )

    history = load_copilot_history()

    previous_copilot = (
        history[-1]
        if history
        else None
    )

    ai_copilot_changes = compare_copilot_snapshots(
        previous_copilot,
        ai_copilot,
    )

    save_copilot_snapshot(
        ai_copilot,
        ai_copilot_changes,
    )

    ai_copilot_timeline = get_copilot_timeline()

    today_take = get_today_take(
        market=market,
        top_pick=top_pick,
        performance=performance,
        ai_news=ai_news,
    )

    save_market_score(
        market.get("score", 50),
        market.get("status", "Neutral"),
    )
    
    data = {
    "updated_at": datetime.now().strftime("%d-%m-%Y %H:%M"),
    "combined_ranking": ranking,
    "market": market,
    "summary": get_market_summary(),
    "alerts": alerts,
    "portfolio": portfolio,
    "system_health": get_system_health(),
    "top_picks": top_picks,
    "analyst": get_ai_analyst(),
    "morning_brief": get_morning_brief(),
    "today_take": today_take,
    "executive_summary": executive_summary,
    "ai_copilot": ai_copilot,
    "ai_copilot_changes": ai_copilot_changes,
    "ai_copilot_timeline": ai_copilot_timeline,
    "performance": performance,
    "ai_news": ai_news,
    "earnings": earnings,
    "earnings_ai": earnings_ai,
    "stock_explanations": stock_explanations,
}

    save_dashboard_cache(data)

    return data

if __name__ == "__main__":
    build_dashboard_cache()
    print("Dashboard cache updated.")