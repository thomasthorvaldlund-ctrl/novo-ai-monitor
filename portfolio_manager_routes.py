from flask import Blueprint
from portfolio import get_portfolio_summary

portfolio_manager_bp = Blueprint("portfolio_manager", __name__)

@portfolio_manager_bp.route("/portfolio-manager-page")
def portfolio_manager_page():
    data = get_portfolio_summary()
    holdings = data["positions"]

    return "Portfolio Manager blueprint works"