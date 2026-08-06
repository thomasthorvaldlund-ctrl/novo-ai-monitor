from flask import Blueprint

from market_data_provider import get_latest_price
from stock_universe_service import get_stock_metadata

portfolio_analysis_bp = Blueprint("portfolio_analysis", __name__)

def portfolio_analysis():
    novo_qty = 23
    novo_buy_price = 301.3
    dsv_qty = 4
    dsv_buy_price = 1588.5
    
    novo_ticker = get_stock_metadata("NOVO")["ticker"]
    dsv_ticker = get_stock_metadata("DSV")["ticker"]

    novo_price = get_latest_price(novo_ticker)
    dsv_price = get_latest_price(dsv_ticker)

    if novo_price is None or dsv_price is None:
        raise RuntimeError("Kunne ikke hente aktuelle porteføljekurser.")
    
    novo_value = novo_qty * novo_price
    dsv_value = dsv_qty * dsv_price
    total_value = novo_value + dsv_value

    novo_weight = (novo_value / total_value) * 100
    dsv_weight = (dsv_value / total_value) * 100
    
    novo_profit = novo_value - (novo_qty * novo_buy_price)
    dsv_profit = dsv_value - (dsv_qty * dsv_buy_price)
    total_profit = novo_profit + dsv_profit
    
    if max(novo_weight, dsv_weight) > 65:
        concentration = "Høj"
    elif max(novo_weight, dsv_weight) > 50:
        concentration = "Moderat"
    else:
        concentration = "Lav"
        
    analysis = f"""

Porteføljeanalyse:

Samlet værdi: {total_value:.2f} DKK
Samlet gevinst/tab: {total_profit:.2f} DKK

Fordeling:
NOVO: {novo_weight:.1f}%
DSV: {dsv_weight:.1f}%

Koncentrationsrisiko: {concentration}

AI-forslag:
- Porteføljen består kun af 2 aktier.
- Diversificering er lav.
- Overvej at sprede på flere sektorer og lande.
- Mulige kategorier: teknologi, industri, energi, indeksfond/ETF.
- Dette er ikke finansiel rådgivning
"""

    return {
        "total_value": round(total_value, 2),
        "total_profit": round(total_profit, 2),
        "novo_weight": round(novo_weight, 1),
        "dsv_weight": round(dsv_weight, 1),
        "concentration_risk": concentration,
        "analysis": analysis,
    }
    
@portfolio_analysis_bp.route("/portfolio-analysis-page")
def portfolio_analysis_page():
    data = portfolio_analysis()

    return f"""
    <html>
    <head>
        <title>Porteføljeanalyse</title>
    </head>
    <body>
        <h1>Porteføljeanalyse</h1>

        <p>Samlet værdi: {data.get("total_value")} DKK</p>
        <p>Samlet gevinst/tab: {data.get("total_profit")} DKK</p>
        <p>NOVO vægt: {data.get("novo_weight")}%</p>
        <p>DSV vægt: {data.get("dsv_weight")}%</p>
        <p>Koncentrationsrisiko: {data.get("concentration_risk")}</p>
        
        <pre>{data.get("analysis")}</pre>
    </body>
    </html>
    """