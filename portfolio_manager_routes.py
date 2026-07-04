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

    return f"""
    <html>
    <head>
        <title>Portfolio Manager</title>
        <style>
            body {{ font-family: Arial, sans-serif; background:#eef2f7; padding:40px; }}
            .container {{ max-width:1200px; margin:auto; }}
            .card {{ background:white; padding:24px; border-radius:14px; margin-bottom:20px; box-shadow:0 10px 30px rgba(0,0,0,0.08); }}
            table {{ width:100%; border-collapse:collapse; background:white; border-radius:14px; overflow:hidden; }}
            th {{ background:#111827; color:white; padding:14px; text-align:left; }}
            td {{ padding:14px; border-bottom:1px solid #e5e7eb; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>💼 Portfolio Manager V4.2</h1>

            <div class="card">
                <p><b>Samlet værdi:</b> {total_value:.2f} DKK</p>
                <p><b>Samlet gevinst/tab:</b> <span style="color:{total_color}; font-weight:bold;">{total_profit:.2f} DKK ({total_profit_pct:.2f}%)</span></p>
                <p><b>Datakilde:</b> portfolio.py + portfolio.csv</p>
            </div>

            <table>
                <tr>
                    <th>Aktie</th>
                    <th>Ticker</th>
                    <th>Antal</th>
                    <th>Købskurs</th>
                    <th>Aktuel kurs</th>
                    <th>Værdi</th>
                    <th>Gevinst/tab</th>
                    <th>Vægt</th>
                </tr>
                {rows}
            </table>

            <p>Rediger beholdninger i: /root/novo-ai-monitor/portfolio.csv</p>
        </div>
    </body>
    </html>
    """
