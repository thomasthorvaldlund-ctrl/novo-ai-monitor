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


command_center_bp = Blueprint("command_center", __name__)

@command_center_bp.route("/command-center")
def command_center():
    cache = load_dashboard_cache()

    system_health = cache.get("system_health", get_system_health())
    market = cache.get("market", get_market_score())
    summary = cache.get("summary", get_market_summary())
    alerts = cache.get("alerts", get_ai_alerts())
    portfolio = cache.get("portfolio", get_portfolio_summary())

    top_picks = [
        {"stock": "DSV", "score": 62.0},
        {"stock": "GENMAB", "score": 62.0},
        {"stock": "CARLSBERG", "score": 62.0},
        {"stock": "APPLE", "score": 62.0},
        {"stock": "MICROSOFT", "score": 62.0},
    ]

    analyst = "AI Analyst cache kommer i næste trin."

    return render_template(
        "command_center.html",
        system_health=system_health,
        market=market,
        top_picks=top_picks,
        summary=summary,
        alerts=alerts,
        portfolio=portfolio,
        analyst=analyst,
    )