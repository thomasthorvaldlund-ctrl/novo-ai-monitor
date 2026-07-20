from flask import Blueprint
from portfolio import get_portfolio_summary as get_raw_portfolio_summary
from portfolio_summary_service import get_portfolio_summary as get_ai_portfolio_summary
from dashboard_cache_service import load_dashboard_cache
from ai_decision_service import get_ai_decision
from portfolio_history_service import save_portfolio_history, load_portfolio_history

portfolio_manager_bp = Blueprint("portfolio_manager", __name__)

@portfolio_manager_bp.route("/portfolio-manager-page")
def portfolio_manager_page():
    data = get_raw_portfolio_summary()
    ai_data = get_ai_portfolio_summary()
    rebalancer = ai_data.get("position_details", [])
    
    holdings = data["positions"]
    recommendations = ai_data.get("recommendations", {})
    increase = recommendations.get("increase", [])
    hold = recommendations.get("hold", [])
    reduce = recommendations.get("reduce", [])
    diversification = recommendations.get("diversification", "")
    
    cache = load_dashboard_cache()
    ranking = cache.get("combined_ranking", [])

    score_map = {
        item.get("stock"): item.get("combined_score", 0)
        for item in ranking
    }

    total_value = data["total_value"]
    total_profit = data["total_profit"]
    total_profit_pct = data["total_profit_pct"]
    total_color = "green" if total_profit >= 0 else "red"
    portfolio_score = ai_data.get("portfolio_score", 0)
    portfolio_risk = ai_data.get("portfolio_risk", "Ukendt")
    best_position = ai_data.get("best_position", "-")
    best_position_score = ai_data.get("best_position_score", 0)
    weakest_position = ai_data.get("weakest_position", "-")
    weakest_position_score = ai_data.get("weakest_position_score", 0)
    portfolio_comment = ai_data.get("portfolio_comment", "Ingen AI-kommentar tilgængelig.")

    rows = ""
    rebalancer_rows = ""

    for position in rebalancer:
        color = "#16a34a" if position["rebalance_amount"] > 0 else "#dc2626"

        rebalancer_rows += f"""

        <tr>
            <td><b>{position['stock']}</b></td>
            <td>{position['weight_pct']}</td>
            <td>{position['target_weight']}</td>
            <td>{position['weight_difference']:+.2f}%</td>
            <td style="color:{color}; font-weight:bold;">
                {position['rebalance_amount']:+,.2f} DKK
            </td>
        </tr>
        """

    for h in holdings:
        color = "green" if h["profit_dkk"] >= 0 else "red"
        
        score = score_map.get(h["stock"], 0)
        decision = get_ai_decision(score)

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
            
            <td>
                <b>{decision['signal']}</b><br>
                <small>{decision['stars']} · Score: {score:.1f}</small>
            </td>
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
            .chart-grid {{ display:grid; grid-template-columns:repeat(3, 1fr); gap:20px; }}
            .chart-grid .card {{ margin-bottom:0; }}
            @media (max-width:900px) {{ .chart-grid {{ grid-template-columns:1fr; }} }}
            table {{ width:100%; border-collapse:collapse; background:white; border-radius:14px; overflow:hidden; }}
            th {{ background:#111827; color:white; padding:14px; text-align:left; }}
            td {{ padding:14px; border-bottom:1px solid #e5e7eb; }}
        </style>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    </head>
    <body>
        <div class="container">
            <h1>💼 Portfolio Manager V4.2</h1>

            <div class="card">
                <p><b>Samlet værdi:</b> {total_value:.2f} DKK</p>
                <p><b>Samlet gevinst/tab:</b> <span style="color:{total_color}; font-weight:bold;">{total_profit:.2f} DKK ({total_profit_pct:.2f}%)</span></p>
                <p><b>Datakilde:</b> portfolio.py + portfolio.csv</p>
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
                    <th>AI Signal</th>
                </tr>
                {rows}
            </table>
            </div>
    
    <div class="card">
        <h2>⚖️ AI Portfolio Rebalancer</h2>

        <table>
            <tr>
                <th>Aktie</th>
                <th>Nuværende vægt</th>
                <th>Målvægt</th>
                <th>Forskel</th>
                <th>AI forslag</th>
            </tr>

            {rebalancer_rows}

        </table>
    </div>
    
<div style="display:flex; gap:10px; margin-bottom:20px;">
    <button onclick="loadPortfolioCharts(7)">7 dage</button>
    <button onclick="loadPortfolioCharts(30)">30 dage</button>
    <button onclick="loadPortfolioCharts(90)">90 dage</button>
    <button onclick="loadPortfolioCharts(3650)">Alle</button>
</div>
    
    <div class="chart-grid">               
    <div class="card">
    <h2>📈 Porteføljeværdi</h2>
    <canvas id="portfolioValueChart" height="80"></canvas>
</div>

<div class="card">
    <h2>💰 Gevinst / tab</h2>
    <canvas id="portfolioProfitChart" height="80"></canvas>
</div>

<div class="card">
    <h2>📊 Afkast (%)</h2>
    <canvas id="portfolioReturnChart" height="80"></canvas>
</div>

</div>

<div class="card">
    <h2>🤖 AI Portfolio Overview</h2>

    <p><b>Portfolio Score:</b> {portfolio_score:.1f}/100</p>
    <p><b>Risikoniveau:</b> {portfolio_risk}</p>

    <p>
        <b>Stærkeste position:</b>
        {best_position} — Score {best_position_score:.1f}
    </p>

    <p>
        <b>Svageste position:</b>
        {weakest_position} — Score {weakest_position_score:.1f}
    </p>

    <div style="background:#f8fafc; padding:16px; border-left:4px solid #2563eb; border-radius:8px;">
        <b>AI-vurdering:</b><br>
        {portfolio_comment}
    </div>
</div>

<div class="card">
    <h2>💡 AI Recommendations</h2>

    <p><b>🟢 Overvej at øge:</b> {", ".join(increase) if increase else "-"}</p>

    <p><b>🟡 Behold:</b> {", ".join(hold) if hold else "-"}</p>

    <p><b>🔴 Overvej at reducere:</b> {", ".join(reduce) if reduce else "-"}</p>

    <div style="margin-top:16px; padding:14px; background:#fff7ed; border-left:4px solid #f59e0b; border-radius:8px;">
        <b>Diversificering</b><br>
        {diversification}
    </div>
</div>

            <p>Rediger beholdninger i: /root/novo-ai-monitor/portfolio.csv</p>
        </div>
    <script>
    let portfolioValueChart;
    let portfolioProfitChart;
    let portfolioReturnChart;
        function loadPortfolioCharts(days = 3650) {{
            fetch(`/portfolio-history?days=${{days}}`)
            .then(response => response.json())
            .then(history => {{

                // Gruppér historik til én værdi pr. dag
                const daily = {{}};

                history.forEach(row => {{
                    const day = row.datetime.slice(0, 10);
                    daily[day] = row;
                }});

                history = Object.values(daily);

                const labels = history.map(row => row.datetime.slice(5, 10));
                const values = history.map(row => Number(row.total_value));
                const profitValues = history.map(row => Number(row.total_profit));
                const profitPctValues = history.map(row => Number(row.total_profit_pct));

                if (portfolioValueChart) portfolioValueChart.destroy();
                if (portfolioProfitChart) portfolioProfitChart.destroy();
                if (portfolioReturnChart) portfolioReturnChart.destroy();

                portfolioValueChart = new Chart(document.getElementById("portfolioValueChart"), {{
                    type: "line",
                    data: {{
                        labels: labels,
                        datasets: [{{
                            label: "Samlet porteføljeværdi (DKK)",
                            data: values,
                            borderWidth: 2,
                            tension: 0.25,
                            fill: false
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        scales: {{
                            y: {{
                                beginAtZero: false
                            }}
                        }}
                    }}
                }});

                portfolioProfitChart = new Chart(document.getElementById("portfolioProfitChart"), {{
                    type: "line",
                    data: {{
                        labels: labels,
                        datasets: [{{
                            label: "Gevinst / tab (DKK)",
                            data: profitValues,
                            borderWidth: 2,
                            tension: 0.25,
                            fill: false
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        scales: {{
                            y: {{
                                beginAtZero: false
                            }}
                        }}
                    }}
                }});

                portfolioReturnChart = new Chart(document.getElementById("portfolioReturnChart"), {{
                    type: "line",
                    data: {{
                        labels: labels,
                        datasets: [{{
                            label: "Afkast (%)",
                            data: profitPctValues,
                            borderWidth: 2,
                            tension: 0.25,
                            fill: false
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        scales: {{
                            y: {{
                                beginAtZero: false
                            }}
                        }}
                    }}
                }});
              
            }});
        }}
    loadPortfolioCharts();
    </script>

    </body>
    </html>
    """

from flask import request

@portfolio_manager_bp.route("/portfolio-history")
def portfolio_history():
    days = request.args.get("days", default=3650, type=int)

    history = load_portfolio_history()
    
    from datetime import datetime, timedelta

    cutoff = datetime.now() - timedelta(days=days)

    history = [
        row for row in history
        if datetime.strptime(row["datetime"], "%Y-%m-%d %H:%M:%S") >= cutoff
    ]

    return history
