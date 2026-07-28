from flask import Blueprint, jsonify, redirect, render_template, request

from portfolio import (
    add_portfolio_position,
    delete_portfolio_position,
    get_portfolio_summary,
    update_portfolio_position,
)
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



@portfolio_settings_bp.route("/portfolio-edit/<position_id>")
def portfolio_edit_page(position_id):
    data = get_portfolio_summary()

    position = next(
        (
            p
            for p in data["positions"]
            if str(p.get("id")) == str(position_id)
        ),
        None,
    )

    if position is None:
        return "Position ikke fundet", 404

    return render_template(
        "portfolio_edit.html",
        position=position,
    )

@portfolio_settings_bp.route("/portfolio-add", methods=["POST"])
def portfolio_add_position():
    try:
        add_portfolio_position(
            stock=request.form.get("stock", ""),
            ticker=request.form.get("ticker", ""),
            qty=request.form.get("qty", ""),
            buy_price=request.form.get("buy_price", ""),
        )
    except (TypeError, ValueError) as error:
        return render_template(
            "portfolio_add.html",
            error=str(error),
            form_data=request.form,
        ), 400

    return redirect("/portfolio-settings")



@portfolio_settings_bp.route("/portfolio-update", methods=["POST"])
def portfolio_update_position():
    print("UPDATE FORM:", request.form)

    try:
        update_portfolio_position(
            position_id=request.form.get("position_id"),
            stock=request.form.get("stock", ""),
            ticker=request.form.get("ticker", ""),
            qty=request.form.get("qty", ""),
            buy_price=request.form.get("buy_price", ""),
        )

    except (TypeError, ValueError) as error:
        return str(error), 400

    return redirect("/portfolio-settings")

@portfolio_settings_bp.route("/portfolio-delete", methods=["POST"])
def portfolio_delete_position():
    position_id = request.form.get("position_id")

    try:
        delete_portfolio_position(position_id)
    except ValueError as error:
        return str(error), 400

    return redirect("/portfolio-settings")

@portfolio_settings_bp.route("/api/stocks")
def stock_search_api():
    query = request.args.get("q", "")
    stocks = search_stocks(query)

    return jsonify({
        "query": query,
        "count": len(stocks),
        "stocks": stocks,
    })

