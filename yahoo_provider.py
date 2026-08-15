"""
Yahoo Finance Provider

Implementering af Yahoo Finance som datakilde.
Alle Yahoo-specifikke kald ligger i denne fil.
"""

import yfinance as yf


YAHOO_INSTRUMENT_SYMBOLS = {
    "FX:USD/DKK": "USDDKK=X",
    "FX:EUR/DKK": "EURDKK=X",
    "FX:SEK/DKK": "SEKDKK=X",
    "FX:NOK/DKK": "NOKDKK=X",
    "FX:GBP/DKK": "GBPDKK=X",
    "FX:CHF/DKK": "CHFDKK=X",
    "FX:PLN/DKK": "PLNDKK=X",
    "FX:CZK/DKK": "CZKDKK=X",

    "INDEX:SP500": "^GSPC",
    "INDEX:NASDAQ_COMPOSITE": "^IXIC",
    "INDEX:OMXC25": "^OMXC25",
    "INDEX:DAX": "^GDAXI",
}


def get_symbol(
    instrument_id,
    kind="equity",
):
    """
    Oversætter Aureums canonical instrument-ID
    til Yahoo Finance-symbol.
    """
    instrument_id = str(
        instrument_id
    ).strip()

    kind = str(
        kind
        or "equity"
    ).strip().lower()

    if kind == "equity":
        return instrument_id

    if kind in {
        "fx",
        "index",
    }:
        symbol = (
            YAHOO_INSTRUMENT_SYMBOLS.get(
                instrument_id
            )
        )

        if not symbol:
            raise ValueError(
                "Ukendt Aureum-instrument for Yahoo: "
                f"{instrument_id}"
            )

        return symbol

    raise ValueError(
        "Ukendt instrumenttype: "
        f"{kind}"
    )


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
