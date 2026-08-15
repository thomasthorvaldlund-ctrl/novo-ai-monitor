"""
Yahoo Finance Provider

Implementering af Yahoo Finance som datakilde.
Alle Yahoo-specifikke kald ligger i denne fil.
"""

import yfinance as yf


def get_metadata(ticker):
    """
    Returnerer rå selskabsmetadata fra Yahoo Finance.
    """
    stock = yf.Ticker(ticker)

    if hasattr(stock, "get_info"):
        return stock.get_info() or {}

    return stock.info or {}


def get_history(ticker, period="1mo", interval=None):
    """
    Returnerer historiske kursdata fra Yahoo Finance.
    """

    if interval:
        return yf.Ticker(ticker).history(
            period=period,
            interval=interval,
        )

    return yf.Ticker(ticker).history(
        period=period,
    )
