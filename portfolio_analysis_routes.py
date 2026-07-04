from flask import Blueprint

portfolio_analysis_bp = Blueprint("portfolio_analysis", __name__)


@portfolio_analysis_bp.route("/portfolio-analysis-page")
def portfolio_analysis_page():
    return "Portfolio Analysis blueprint works"