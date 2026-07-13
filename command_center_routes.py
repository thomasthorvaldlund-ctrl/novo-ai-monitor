from flask import Blueprint, render_template

from dashboard_cache_service import load_dashboard_cache
from system_health_service import get_system_health
from market_score_service import get_market_score
from market_summary_service import get_market_summary
from top_picks_service import get_top_picks
from combined_score_service import combined_stock_score as service_combined_score
from openai_service import client
from ai_alerts_service import get_ai_alerts
from portfolio_summary_service import get_portfolio_summary
from ai_analyst_service import get_ai_analyst
from morning_brief_service import get_morning_brief
from market_score_history_service import load_market_score_history


command_center_bp = Blueprint("command_center", __name__)

@command_center_bp.route("/command-center")
def command_center():
    cache = load_dashboard_cache()
    updated_at = cache.get("updated_at", "Ukendt")

    system_health = cache.get("system_health", get_system_health())
    market = cache.get("market", get_market_score())
    summary = cache.get("summary", get_market_summary())
    alerts = cache.get("alerts", get_ai_alerts())
    portfolio = cache.get("portfolio", get_portfolio_summary())

    top_picks = cache.get("top_picks", [])
    analyst = cache.get("analyst", "AI Analyst er ikke tilgængelig endnu.")
    brief = cache.get("morning_brief", {})
    performance = cache.get("performance", {})
    ai_news = cache.get("ai_news", {})
    stock_explanations = cache.get("stock_explanations", [])
    today_take = cache.get("today_take", {})

    return render_template(
        "command_center.html",
        system_health=system_health,
        market=market,
        top_picks=top_picks,
        summary=summary,
        alerts=alerts,
        portfolio=portfolio,
        analyst=analyst,
        brief=brief,
        updated_at=updated_at,
        performance=performance,
        ai_news=ai_news,
        stock_explanations=stock_explanations,
        today_take=today_take,
    )
    
@command_center_bp.route("/market-score-history")
def market_score_history():
    return {
        "history": load_market_score_history()
    }    