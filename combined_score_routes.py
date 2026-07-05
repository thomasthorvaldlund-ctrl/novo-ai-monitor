from flask import Blueprint

combined_score_bp = Blueprint("combined_score", __name__)

@combined_score_bp.route("/combined-stock-score")
def combined_stock_score():
    return "Combined Score blueprint works"