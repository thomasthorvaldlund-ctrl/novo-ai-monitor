from flask import Blueprint
import yfinance as yf

market_dashboard_bp = Blueprint("market_dashboard", __name__)

@market_dashboard_bp.route("/market-dashboard")
def market_dashboard():
    markets = {
        "S&P 500": "^GSPC",
        "Nasdaq": "^IXIC",
        "OMXC25": "^OMXC25",
        "DAX": "^GDAXI"
    }

    return "OK"