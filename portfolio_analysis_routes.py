from flask import Blueprint
import yfinance as yf

portfolio_analysis_bp = Blueprint("portfolio_analysis", __name__)


@portfolio_analysis_bp.route("/portfolio-analysis-page")
def portfolio_analysis_page():
    novo_qty = 23
    novo_buy_price = 301.3
    dsv_qty = 4
    dsv_buy_price = 1588.5
    
    novo_price = float(yf.Ticker("NOVO-B.CO").history(period="10d")["Close"].iloc[-1])
    dsv_price = float(yf.Ticker("DSV.CO").history(period="10d")["Close"].iloc[-1])

    return "OK"