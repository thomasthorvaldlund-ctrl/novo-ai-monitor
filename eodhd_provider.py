"""
EODHD Market Data Provider

Denne provider er klargjort til en senere EODHD-integration.
Den aktiveres først, når API-understøttelsen er implementeret,
og MARKET_DATA_PROVIDER sættes til "eodhd".
"""


class EODHDNotConfiguredError(RuntimeError):
    """EODHD er valgt, men endnu ikke konfigureret."""


def get_metadata(ticker):
    """
    Returnerer selskabsmetadata fra EODHD.

    Implementeres sammen med den kommende EODHD API-integration.
    """
    raise EODHDNotConfiguredError(
        "EODHD-provider er endnu ikke konfigureret. "
        "Brug MARKET_DATA_PROVIDER=yahoo indtil videre."
    )


def get_history(ticker, period="1mo", interval=None):
    """
    Returnerer historiske kursdata fra EODHD.

    Funktionen implementeres, når Aureum AI får en EODHD API-nøgle.
    """

    raise EODHDNotConfiguredError(
        "EODHD-provider er endnu ikke konfigureret. "
        "Brug MARKET_DATA_PROVIDER=yahoo indtil videre."
    )
