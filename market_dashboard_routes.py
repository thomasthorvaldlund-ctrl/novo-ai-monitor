from flask import Blueprint

market_dashboard_bp = Blueprint("market_dashboard", __name__)

@market_dashboard_bp.route("/market-dashboard")
def market_dashboard():
    return "Market Dashboard blueprint works"