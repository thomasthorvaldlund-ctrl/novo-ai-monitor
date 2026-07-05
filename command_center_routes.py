from market_score_service import get_market_score

from flask import Blueprint

command_center_bp = Blueprint("command_center", __name__)

@command_center_bp.route("/command-center")

def command_center():
    market = get_market_score()

    return f"""
AI COMMAND CENTER

Market Score: {market['score']}/100
Status: {market['status']}
"""
