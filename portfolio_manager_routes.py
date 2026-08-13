from flask import Blueprint, render_template
from portfolio import get_portfolio_summary as get_raw_portfolio_summary
from portfolio_summary_service import get_portfolio_summary as get_ai_portfolio_summary
from dashboard_cache_service import load_dashboard_cache
from ai_decision_service import get_ai_decision
from portfolio_history_service import save_portfolio_history, load_portfolio_history
from portfolio_health_service import get_portfolio_health
from portfolio_health_history_service import load_portfolio_health_history
from portfolio_evolution_explanation_service import explain_portfolio_evolution

portfolio_manager_bp = Blueprint("portfolio_manager", __name__)

@portfolio_manager_bp.route("/portfolio-manager-old")
def portfolio_manager_page():
    data = get_raw_portfolio_summary()
    ai_data = get_ai_portfolio_summary()
    rebalancer = ai_data.get("position_details", [])
    
    holdings = data["positions"]
    recommendations = ai_data.get("recommendations", {})
    increase = recommendations.get("increase", [])
    hold = recommendations.get("hold", [])
    watch = recommendations.get("watch", [])
    reduce = recommendations.get("reduce", [])
    reduce_details = recommendations.get("reduce_details", [])
    diversification = recommendations.get("diversification", "")
    
    cache = load_dashboard_cache()
    ranking = cache.get("combined_ranking", [])
    market_data_status = cache.get("market_data_status", {})

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
    reduce_cards = ""

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

    for item in reduce_details:
        reduce_cards += f"""
        <div style="margin:12px 0; padding:14px; background:#fff7ed; border-left:4px solid #dc2626; border-radius:8px;">

            <b>{item['stock']}</b><br>

            AI-score:
            {item['score']}/100
            <br>

            Signal:
            {item['signal']}
            <br>

            Risiko:
            {item['risk']}
            <br>

            Confidence:
            {item['confidence']}%
            <br>

            Årsag:
            {item['comment']}

        </div>
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

    market_status = market_data_status.get("status", "Ukendt")
    market_provider = market_data_status.get("provider", "Ukendt")
    market_last_update = market_data_status.get("last_market_update", "-")
    market_age = market_data_status.get("age_minutes")

    if market_status == "Live":
        market_status_color = "#16a34a"
        market_status_background = "#ecfdf5"
        market_status_message = "Markedsdata opdateres normalt."
    elif market_status == "Forsinket":
        market_status_color = "#f59e0b"
        market_status_background = "#fff7ed"
        market_status_message = (
            "Aktiekurser kan være lidt forsinkede på grund af den eksterne dataleverandør."
        )
    else:
        market_status_color = "#dc2626"
        market_status_background = "#fef2f2"
        market_status_message = (
            "Aktiekurserne er forsinkede på grund af et eksternt dataproblem. "
            "Aureum AI fungerer normalt og opdaterer automatisk, når nye data modtages."
        )

    market_age_text = (
        f"{market_age} min"
        if market_age is not None
        else "Ukendt"
    )

    market_data_status_html = f"""
    <div style="
        background:{market_status_background};
        border-left:5px solid {market_status_color};
        padding:12px 16px;
        border-radius:10px;
        margin-bottom:20px;
    ">
        <b>📈 Markedsdata:</b>
        <span style="color:{market_status_color};font-weight:bold;">
            {market_status}
        </span>
        · Seneste data: {market_last_update}
        · Forsinkelse: {market_age_text}
        · Kilde: {market_provider}

        <div style="margin-top:6px;color:#475569;font-size:14px;">
            {market_status_message}
        </div>
    </div>
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

            {market_data_status_html}

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

    <p><b>🟠 Overvåg tæt:</b> {", ".join(watch) if watch else "-"}</p>

    <p><b>🔴 Reducer:</b></p>

    {reduce_cards}

    <div style="margin-top:16px; padding:14px; background:#fff7ed; border-left:4px solid #f59e0b; border-radius:8px;">
        <b>Diversificering</b><br>
        {diversification}
    </div>
</div>

            <p>Rediger beholdninger i: /root/aureum-ai-platform/portfolio.csv</p>
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

                    if (
                        row.total_value &&
                        row.total_value !== "nan" &&
                        !isNaN(Number(row.total_value))
                    ) {{
                        daily[day] = row;
                    }}

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
                            tension: 0.4,
                            fill: false,
                            borderColor: "#3b82f6",
                            backgroundColor: "#3b82f6"
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
                            tension: 0.4,
                            fill: false,
                            borderColor: function(context) {{
                                const value = context.raw;
                                return value >= 0 ? "#16a34a" : "#dc2626";
                            }},
                            backgroundColor: function(context) {{
                                const value = context.raw;
                                return value >= 0 ? "#16a34a" : "#dc2626";
                            }}
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
                            tension: 0.4,
                            fill: false,
                            borderColor: function(context) {{
                                const value = context.raw;
                                return value >= 0 ? "#16a34a" : "#dc2626";
                            }},
                            backgroundColor: function(context) {{
                                const value = context.raw;
                                return value >= 0 ? "#16a34a" : "#dc2626";
                            }}
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


@portfolio_manager_bp.route("/portfolio-manager-page")
def portfolio_manager_v2_test():
    data = get_raw_portfolio_summary()
    ai_data = get_ai_portfolio_summary()
    cache = load_dashboard_cache()
    portfolio_health = get_portfolio_health(ai_data)
    portfolio_health_history = load_portfolio_health_history()

    portfolio_evolution = None
    portfolio_evolution_explanation = None

    if len(portfolio_health_history) >= 2:
        from portfolio_evolution_service import compare_portfolio_health

        portfolio_evolution = compare_portfolio_health(
            portfolio_health_history[0],
            portfolio_health_history[-1],
        )

        portfolio_evolution_explanation = (
            explain_portfolio_evolution(portfolio_evolution)
        )

    ranking = cache.get("combined_ranking", [])

    score_map = {
        item.get("stock"): item.get("combined_score", 0)
        for item in ranking
    }

    holdings = []

    for position in data.get("positions", []):
        stock = position.get("stock")
        score = score_map.get(stock, 0)
        decision = get_ai_decision(score)

        holdings.append({
            **position,
            "score": score,
            "signal": decision.get("signal", "UNKNOWN"),
            "stars": decision.get("stars", ""),
        })

    return render_template(
        "portfolio_manager_v2.html",
        data=data,
        ai_data=ai_data,
        market_data_status=cache.get("market_data_status", {}),
        holdings=holdings,
        rebalancer=ai_data.get("position_details", []),
        portfolio_health=portfolio_health,
        portfolio_health_history=portfolio_health_history,
        portfolio_evolution=portfolio_evolution,
        portfolio_evolution_explanation=portfolio_evolution_explanation,
        total_value=data.get("total_value", 0),
        total_profit=data.get("total_profit", 0),
        total_profit_pct=data.get("total_profit_pct", 0),
        portfolio_score=ai_data.get("portfolio_score", 0),
        portfolio_risk=ai_data.get("portfolio_risk", "Ukendt"),
        best_position=ai_data.get("best_position", "-"),
        best_position_score=ai_data.get("best_position_score", 0),
        weakest_position=ai_data.get("weakest_position", "-"),
        weakest_position_score=ai_data.get("weakest_position_score", 0),
        portfolio_comment=ai_data.get(
            "portfolio_comment",
            "Ingen AI-kommentar tilgængelig.",
        ),
    )

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
