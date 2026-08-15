"""
EODHD Market Data Provider

Denne provider er klargjort til en senere EODHD-integration.
Den aktiveres først, når API-understøttelsen er implementeret,
og MARKET_DATA_PROVIDER sættes til "eodhd".
"""


class EODHDNotConfiguredError(RuntimeError):
    """EODHD er valgt, men endnu ikke konfigureret."""


def get_symbol(
    instrument_id,
    kind="equity",
):
    """
    Oversætter Aureums canonical instrument-ID
    til EODHD-symbol.

    Implementeres sammen med den kommende
    EODHD API-integration.
    """
    raise EODHDNotConfiguredError(
        "EODHD-provider er endnu ikke konfigureret. "
        "Provider-specifik symboloversættelse mangler."
    )


def get_metadata(ticker):
    """
    Returnerer selskabsmetadata fra EODHD i Aureums
    provider-neutrale metadataformat:

    sector, industry, country, exchange, full_exchange,
    currency, quote_type og long_name.

    Implementeres sammen med den kommende EODHD API-integration.
    """
    raise EODHDNotConfiguredError(
        "EODHD-provider er endnu ikke konfigureret. "
        "Brug MARKET_DATA_PROVIDER=yahoo indtil videre."
    )


def get_history(ticker, period="1mo", interval=None):
    """
    Returnerer historiske kursdata fra EODHD.

    Provider-resultatet normaliseres centralt til Aureums
    history-kontrakt: pandas DataFrame med obligatorisk
    Close og kronologisk DatetimeIndex. Open, High, Low,
    Adj Close og Volume er valgfrie.

    Funktionen implementeres, når Aureum AI får en EODHD API-nøgle.
    """

    raise EODHDNotConfiguredError(
        "EODHD-provider er endnu ikke konfigureret. "
        "Brug MARKET_DATA_PROVIDER=yahoo indtil videre."
    )
