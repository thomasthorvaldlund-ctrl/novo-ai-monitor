"""
Søgeservice til Aureum AI Platforms centrale aktiebibliotek.
"""

from stock_library import STOCK_LIBRARY


def search_stocks(query=""):
    """
    Returnerer aktier, der matcher navn, ticker, børs, land eller sektor.

    En tom søgning returnerer hele aktiebiblioteket.
    """
    normalized_query = str(query or "").strip().lower()

    if not normalized_query:
        return STOCK_LIBRARY.copy()

    matches = []

    for stock in STOCK_LIBRARY:
        searchable_values = (
            stock.get("name", ""),
            stock.get("ticker", ""),
            stock.get("exchange", ""),
            stock.get("country", ""),
            stock.get("sector", ""),
        )

        if any(
            normalized_query in str(value).lower()
            for value in searchable_values
        ):
            matches.append(stock)

    return matches


def get_stock_by_ticker(ticker):
    """
    Finder én aktie ud fra ticker.
    Returnerer None, hvis tickeren ikke findes.
    """
    normalized_ticker = str(ticker or "").strip().upper()

    for stock in STOCK_LIBRARY:
        if stock.get("ticker", "").upper() == normalized_ticker:
            return stock.copy()

    return None
