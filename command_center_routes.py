from flask import Blueprint, render_template

from market_score_service import get_market_score
from top_picks_service import get_top_picks

command_center_bp = Blueprint("command_center", __name__)

@command_center_bp.route("/command-center")
def command_center():
    market = get_market_score()

    ranking = [
        {"stock": "NVIDIA", "combined_score": 88, "rating": "Stærk kandidat"},
        {"stock": "DSV", "combined_score": 84, "rating": "Stærk kandidat"},
        {"stock": "NOVO", "combined_score": 81, "rating": "Stærk kandidat"},
        {"stock": "MICROSOFT", "combined_score": 79, "rating": "Stærk kandidat"},
        {"stock": "ASML", "combined_score": 77, "rating": "Stærk kandidat"},
    ]

    top_picks = get_top_picks(ranking)

    return render_template(
        "command_center.html",
        market=market,
        top_picks=top_picks,
    )