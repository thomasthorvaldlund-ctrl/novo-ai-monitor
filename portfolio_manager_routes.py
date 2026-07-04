from flask import Blueprint
from portfolio import get_portfolio_summary

portfolio_manager_bp = Blueprint("portfolio_manager", __name__)

@portfolio_manager_bp.route("/portfolio-manager-page")
def portfolio_manager_page():
    data = get_portfolio_summary()
    holdings = data["positions"]

    total_value = data["total_value"]
    total_profit = data["total_profit"]
    total_profit_pct = data["total_profit_pct"]
    total_color = "green" if total_profit >= 0 else "red"

    rows = ""

    for h in holdings:
        color = "green" if h["profit_dkk"] >= 0 else "red"

        rows += f"""
        <tr>
            <td><b>{h['stock']}</b></td>
            <td>{h['ticker']}</td>
            <td>{h['qty']}</td>
            <td>{h['buy_price']:.2f} {h['currency']}<br><small>{h['buy_price_dkk']:.2f} DKK</small></td>
            <td>{h['latest']:.2f} {h['currency']}<br><small>{h['latest_dkk']:.2f} DKK</small></td>
            <td>{h['value_dkk']:.2f} DKK</td>
            <td style="color:{color}; font-weight:bold;">{h['profit_dkk']:.2f} DKK ({h['profit_pct']:.2f}%)</td>
            <td>{h['weight_pct']:.1f}%</td>
        </tr>
        """

    return "OK"
