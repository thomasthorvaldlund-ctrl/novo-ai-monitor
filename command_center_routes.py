from top_picks_service import get_top_picks
from market_score_service import get_market_score

from flask import Blueprint

command_center_bp = Blueprint("command_center", __name__)

@command_center_bp.route("/command-center")

def command_center():
    market = get_market_score()
    top_picks = get_top_picks()

    output = f"""AI COMMAND CENTER

Market Score: {market['score']}/100
Status: {market['status']}

Top Picks:
"""

    for item in top_picks:
        output += f"{item['rank']}. {item['stock']} ({item['score']})\n"

    return output
