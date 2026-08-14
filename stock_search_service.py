"""
Søgeservice til Aureum AI Platforms centrale aktiebibliotek.

Alle søgeresultater bygges fra det canonical stock universe.
Search-laget ændrer ikke aktieuniverset og udfører ingen
markedsdata- eller AI-kald.
"""

from stock_universe_service import get_all_stocks


def _display_country(country):
    """
    Bevarer det eksisterende API/UI-landenavn for USA,
    mens canonical metadata fortsat bruger "United States".
    """
    if country == "United States":
        return "USA"

    return country


def _to_search_record(symbol, data):
    """
    Adapter fra canonical stock metadata til den eksisterende
    Stock Picker/API-kontrakt.
    """
    return {
        "name": data.get("name") or symbol,
        "ticker": data.get("ticker", ""),
        "currency": data.get("currency", ""),
        "exchange": data.get("market", ""),
        "country": _display_country(
            data.get("country", "")
        ),
        "sector": data.get("sector", ""),
    }


def _get_search_records():
    """
    Returnerer canonical stocks sammen med deres interne symbol.

    Hele universet er søgbart. Feltet "active" styrer analyse-
    pipeline og skal ikke begrænse hvilke aktier brugeren kan
    finde i biblioteket.
    """
    return [
        (
            symbol,
            data,
            _to_search_record(
                symbol,
                data,
            ),
        )
        for symbol, data in get_all_stocks().items()
    ]


def search_stocks(query=""):
    """
    Returnerer aktier, der matcher navn, symbol, ticker,
    børs, land eller sektor.

    En tom søgning returnerer hele det canonical aktieunivers.
    """
    normalized_query = str(
        query or ""
    ).strip().lower()

    records = _get_search_records()

    if not normalized_query:
        return [
            record.copy()
            for _, _, record in records
        ]

    matches = []

    for symbol, data, record in records:
        searchable_values = (
            symbol,
            record.get("name", ""),
            record.get("ticker", ""),
            record.get("exchange", ""),
            record.get("country", ""),
            data.get("country", ""),
            record.get("sector", ""),
        )

        if any(
            normalized_query in str(value).lower()
            for value in searchable_values
        ):
            matches.append(
                record.copy()
            )

    return matches


def get_stock_by_ticker(ticker):
    """
    Finder én aktie ud fra canonical ticker.

    Det interne Aureum-symbol accepteres også, når det matcher
    entydigt, eksempelvis "ASML" -> "ASML.AS".
    """
    normalized_ticker = str(
        ticker or ""
    ).strip().upper()

    if not normalized_ticker:
        return None

    for symbol, _, record in _get_search_records():
        if (
            record.get(
                "ticker",
                ""
            ).upper()
            == normalized_ticker
        ):
            return record.copy()

        if symbol.upper() == normalized_ticker:
            return record.copy()

    return None
