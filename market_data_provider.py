"""
Aureum AI Market Data Provider

Denne fil er det centrale adgangslag til markedsdata.

I første version bruges Yahoo Finance som datakilde.
Senere kan Yahoo udskiftes med f.eks. EODHD eller Finnhub,
uden at resten af platformen skal ændres.
"""

from datetime import datetime

import yfinance as yf


# Aktiv datakilde.
# Skift senere til "eodhd", når EODHD-integrationen er implementeret.
DATA_PROVIDER = "yahoo"

PROVIDER_NAMES = {
    "yahoo": "Yahoo Finance",
    "eodhd": "EODHD",
}


def get_provider_name():
    return PROVIDER_NAMES.get(
        DATA_PROVIDER,
        DATA_PROVIDER,
    )


def get_ticker(symbol: str):
    """
    Oversætter interne symboler til markeds-tickers.
    """

    mapping = {
        "NOVO": "NOVO-B.CO",
        "DSV": "DSV.CO",
    }

    return mapping.get(symbol.upper(), symbol)


def get_history(symbol, period="1mo", interval=None):
    """
    Returnerer historiske kursdata fra den aktive datakilde.
    """

    ticker = get_ticker(symbol)

    if DATA_PROVIDER == "yahoo":
        if interval:
            return yf.Ticker(ticker).history(
                period=period,
                interval=interval,
            )

        return yf.Ticker(ticker).history(
            period=period,
        )

    if DATA_PROVIDER == "eodhd":
        raise NotImplementedError(
            "EODHD er endnu ikke implementeret."
        )

    raise RuntimeError(
        f"Ukendt Market Data Provider: {DATA_PROVIDER}"
    )


def get_latest_price(symbol):
    """
    Returnerer seneste lukkekurs.
    """

    history = get_history(symbol, period="5d")

    if history.empty:
        return None

    return float(history["Close"].iloc[-1])


def get_latest_timestamp(symbol):
    """
    Returnerer tidspunktet for seneste datapunkt.
    """

    history = get_history(
        symbol,
        period="1d",
        interval="1m",
    )

    if history.empty:
        return None

    return history.index[-1].to_pydatetime()


if __name__ == "__main__":

    print("Provider:", get_provider_name())
    print("NOVO:", get_latest_price("NOVO"))
    print("DSV :", get_latest_price("DSV"))
    print("Tid :", get_latest_timestamp("NOVO"))
