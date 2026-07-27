from flask import Blueprint, jsonify, request

from combined_score_service import combined_stock_score as get_combined_stock_score
from stock_screener_cache_builder import build_stock_screener_cache


combined_score_bp = Blueprint("combined_score", __name__)


@combined_score_bp.route("/combined-stock-score")
def combined_stock_score():
    return jsonify(get_combined_stock_score(None))


@combined_score_bp.route("/update-stock-screener-cache")
def update_stock_screener_cache():
    if request.remote_addr not in ("127.0.0.1", "::1"):
        return jsonify({
            "status": "error",
            "message": "Endpointet må kun kaldes lokalt"
        }), 403

    result = build_stock_screener_cache()
    return jsonify(result)
