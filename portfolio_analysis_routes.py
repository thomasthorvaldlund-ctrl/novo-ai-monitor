from flask import Blueprint
import yfinance as yf

portfolio_analysis_bp = Blueprint("portfolio_analysis", __name__)


@portfolio_analysis_bp.route("/portfolio-analysis-page")
def portfolio_analysis():
    novo_qty = 23
    novo_buy_price = 301.3
    dsv_qty = 4
    dsv_buy_price = 1588.5
    
    novo_price = float(yf.Ticker("NOVO-B.CO").history(period="10d")["Close"].iloc[-1])
    dsv_price = float(yf.Ticker("DSV.CO").history(period="10d")["Close"].iloc[-1])
    
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
- Dette er ikke finansiel rådgivning.
"""

    return {
        "total_value": round(total_value, 2),
        "total_profit": round(total_profit, 2),
        "novo_weight": round(novo_weight, 1),
        "dsv_weight": round(dsv_weight, 1),
        "concentration_risk": concentration,
        "analysis": analysis,
    }