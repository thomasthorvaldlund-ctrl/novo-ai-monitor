from flask import Blueprint, jsonify, render_template, request

from portfolio import get_portfolio_summary
from stock_search_service import search_stocks

portfolio_settings_bp = Blueprint(
    "portfolio_settings",
    __name__,
)


@portfolio_settings_bp.route("/portfolio-settings")
def portfolio_settings_page():
    data = get_portfolio_summary()

    return render_template(
        "portfolio_settings.html",
        positions=data["positions"],
        total_value=data["total_value"],
        total_cost=data["total_cost"],
        total_profit=data["total_profit"],
        total_profit_pct=data["total_profit_pct"],
    )

@portfolio_settings_bp.route("/portfolio-add")
def portfolio_add_page():
    return render_template("portfolio_add.html")

@portfolio_settings_bp.route("/api/stocks")
def stock_search_api():
    query = request.args.get("q", "")
    stocks = search_stocks(query)

    return jsonify({
        "query": query,
        "count": len(stocks),
        "stocks": stocks,
    })

