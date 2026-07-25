from flask import Blueprint, jsonify

from stock_universe_service import (
    filter_stocks,
    get_all_stocks,
    get_stock_metadata,
    get_stock_universe_statistics,
)

stock_universe_bp = Blueprint("stock_universe", __name__)


@stock_universe_bp.route("/stock-universe")
def stock_universe():
    """
    Returnerer hele aktieuniverset og samlet statistik.
    """
    stocks = get_all_stocks()

    return jsonify({
        "status": "ok",
        "statistics": get_stock_universe_statistics(),
        "stocks": stocks,
    })


@stock_universe_bp.route("/stock-universe/<stock_name>")
def stock_universe_detail(stock_name):
    """
    Returnerer metadata for én aktie.
    """
    stock = get_stock_metadata(stock_name)

    if stock is None:
        return jsonify({
            "status": "error",
            "message": f"Aktien '{stock_name.upper()}' findes ikke.",
        }), 404

    return jsonify({
        "status": "ok",
        "name": stock_name.upper(),
        "stock": stock,
    })


@stock_universe_bp.route("/stock-universe-filter")
def stock_universe_filter():
    """
    Midlertidigt endpoint til kontrol af filtreringsfunktionen.
    """
    return jsonify({
        "status": "ok",
        "stocks": filter_stocks(active=True),
    })
