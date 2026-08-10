"""
Aureum AI Market Status Service

Samler markedsstatus for aktiver,
så dashboards og AI-services kan bruge
én fælles kilde.
"""

from market_session_service import get_market_session_for_ticker


def get_asset_market_status(ticker):
    """
    Returnerer markedsstatus for én ticker.
    """

    session = get_market_session_for_ticker(ticker)

    return {
        "ticker": ticker,
        "status": session.get("status", "UNKNOWN"),
        "label": session.get("label", "Ukendt"),
        "exchange": session.get("exchange"),
        "local_time": session.get("local_time"),
        "open": session.get("open"),
        "close": session.get("close"),
        "reason": session.get("reason"),
    }


def get_market_status_summary(tickers):
    """
    Returnerer status for flere aktiver.
    """

    return [
        get_asset_market_status(ticker)
        for ticker in tickers
    ]
