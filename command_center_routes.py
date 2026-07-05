from flask import Blueprint, render_template

from market_score_service import get_market_score
from top_picks_service import get_top_picks

command_center_bp = Blueprint("command_center", __name__)

@command_center_bp.route("/command-center")
def command_center():
    market = get_market_score()
    top_picks = get_top_picks()

    return render_template(
        "command_center.html",
        market=market,
        top_picks=top_picks,
    )