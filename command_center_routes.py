from flask import Blueprint, render_template


from market_score_service import get_market_score
from market_summary_service import get_market_summary
from top_picks_service import get_top_picks
from combined_score_service import combined_stock_score as service_combined_score
from openai_service import client
from ai_alerts_service import get_ai_alerts
from portfolio_summary_service import get_portfolio_summary

command_center_bp = Blueprint("command_center", __name__)

@command_center_bp.route("/command-center")
def command_center():
    market = get_market_score()
    summary = get_market_summary()
    alerts = get_ai_alerts()
    portfolio = get_portfolio_summary()

    combined_data = service_combined_score(client)
    ranking = combined_data.get("combined_ranking", [])

    top_picks = get_top_picks(ranking)

    return render_template(
        "command_center.html",
        market=market,
        top_picks=top_picks,
        summary=summary,
        alerts=alerts,
        portfolio=portfolio,
    )