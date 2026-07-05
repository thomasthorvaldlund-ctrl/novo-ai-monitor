from flask import Blueprint, render_template

from market_score_service import get_market_score
from top_picks_service import get_top_picks
from combined_score_service import combined_stock_score as service_combined_score
from openai_service import client

command_center_bp = Blueprint("command_center", __name__)

@command_center_bp.route("/command-center")
def command_center():
    market = get_market_score()

    combined_data = service_combined_score(client)
    ranking = combined_data.get("combined_ranking", [])

    top_picks = get_top_picks(ranking)

    return render_template(
        "command_center.html",
        market=market,
        top_picks=top_picks,
    )