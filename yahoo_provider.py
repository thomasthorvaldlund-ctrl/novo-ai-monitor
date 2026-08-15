"""
Yahoo Finance Provider

Implementering af Yahoo Finance som datakilde.
Alle Yahoo-specifikke kald ligger i denne fil.
"""

import yfinance as yf


def _normalize_metadata(info):
    """
    Oversætter Yahoo-specifik metadata til Aureums
    provider-neutrale metadataformat.
    """
    info = info or {}

    return {
        "sector":
            info.get("sector"),

        "industry":
            info.get("industry"),

        "country":
            info.get("country"),

        "exchange":
            info.get("exchange"),

        "full_exchange":
            info.get("fullExchangeName"),

        "currency":
            info.get("currency"),

        "quote_type":
            info.get("quoteType"),

        "long_name":
            (
                info.get("longName")
                or info.get("shortName")
            ),
    }


def get_metadata(ticker):
    """
    Returnerer selskabsmetadata i Aureums
    provider-neutrale metadataformat.
    """
    stock = yf.Ticker(ticker)

    if hasattr(
        stock,
        "get_info",
    ):
        info = (
            stock.get_info()
            or {}
        )

    else:
        info = (
            stock.info
            or {}
        )

    return _normalize_metadata(
        info
    )


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
