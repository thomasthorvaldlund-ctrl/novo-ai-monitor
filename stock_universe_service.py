"""
Central administration af Stock AI Monitors aktieunivers.

Denne service bliver senere udvidet til at understøtte
1.000+ aktier, markeder, sektorer og prioriteringsniveauer.
"""

STOCK_UNIVERSE = {
    "NOVO": {
        "ticker": "NOVO-B.CO",
        "country": "Denmark",
        "market": "Nasdaq Copenhagen",
        "currency": "DKK",
        "active": True,
    },
    "DSV": {
        "ticker": "DSV.CO",
        "country": "Denmark",
        "market": "Nasdaq Copenhagen",
        "currency": "DKK",
        "active": True,
    },
    "VESTAS": {
        "ticker": "VWS.CO",
        "country": "Denmark",
        "market": "Nasdaq Copenhagen",
        "currency": "DKK",
        "active": True,
    },
    "GENMAB": {
        "ticker": "GMAB.CO",
        "country": "Denmark",
        "market": "Nasdaq Copenhagen",
        "currency": "DKK",
        "active": True,
    },
    "CARLSBERG": {
        "ticker": "CARL-B.CO",
        "country": "Denmark",
        "market": "Nasdaq Copenhagen",
        "currency": "DKK",
        "active": True,
    },
    "MAERSK": {
        "ticker": "MAERSK-B.CO",
        "country": "Denmark",
        "market": "Nasdaq Copenhagen",
        "currency": "DKK",
        "active": True,
    },
    "ORSTED": {
        "ticker": "ORSTED.CO",
        "country": "Denmark",
        "market": "Nasdaq Copenhagen",
        "currency": "DKK",
        "active": True,
    },
    "PANDORA": {
        "ticker": "PNDORA.CO",
        "country": "Denmark",
        "market": "Nasdaq Copenhagen",
        "currency": "DKK",
        "active": True,
    },
    "APPLE": {
        "ticker": "AAPL",
        "country": "United States",
        "market": "NASDAQ",
        "currency": "USD",
        "active": True,
    },
    "MICROSOFT": {
        "ticker": "MSFT",
        "country": "United States",
        "market": "NASDAQ",
        "currency": "USD",
        "active": True,
    },
    "NVIDIA": {
        "ticker": "NVDA",
        "country": "United States",
        "market": "NASDAQ",
        "currency": "USD",
        "active": True,
    },
    "ASML": {
        "ticker": "ASML.AS",
        "country": "Netherlands",
        "market": "Euronext Amsterdam",
        "currency": "EUR",
        "active": True,
    },
    "TESLA": {
        "ticker": "TSLA",
        "country": "United States",
        "market": "NASDAQ",
        "currency": "USD",
        "active": True,
    },
    "AMAZON": {
        "ticker": "AMZN",
        "country": "United States",
        "market": "NASDAQ",
        "currency": "USD",
        "active": True,
    },
    "META": {
        "ticker": "META",
        "country": "United States",
        "market": "NASDAQ",
        "currency": "USD",
        "active": True,
    },
    "GOOGLE": {
        "ticker": "GOOGL",
        "country": "United States",
        "market": "NASDAQ",
        "currency": "USD",
        "active": True,
    },
}


def get_active_stocks():
    """
    Returnerer aktive aktier som:

    {
        "NOVO": "NOVO-B.CO",
        "APPLE": "AAPL",
        ...
    }
    """
    return {
        name: data["ticker"]
        for name, data in STOCK_UNIVERSE.items()
        if data.get("active", False)
    }


def get_stock_metadata(name):
    """
    Returnerer metadata for én aktie.
    """
    return STOCK_UNIVERSE.get(name.upper())


def get_stock_count():
    """
    Returnerer antal aktive aktier.
    """
    return len(get_active_stocks())


def get_all_stocks():
    """
    Returnerer en kopi af hele aktieuniverset.
    """
    return {
        name: data.copy()
        for name, data in STOCK_UNIVERSE.items()
    }


def filter_stocks(country=None, market=None, active=None):
    """
    Filtrerer aktieuniverset efter land, marked og aktiv-status.

    Parametre:
        country: eksempelvis "Denmark"
        market: eksempelvis "NASDAQ"
        active: True, False eller None
    """
    results = {}

    for name, data in STOCK_UNIVERSE.items():
        if country and data.get("country", "").lower() != country.lower():
            continue

        if market and data.get("market", "").lower() != market.lower():
            continue

        if active is not None and data.get("active", False) != active:
            continue

        results[name] = data.copy()

    return results


def get_stock_universe_statistics():
    """
    Returnerer grundlæggende statistik for aktieuniverset.
    """
    countries = {}
    markets = {}
    active_count = 0
    inactive_count = 0

    for data in STOCK_UNIVERSE.values():
        country = data.get("country", "Unknown")
        market = data.get("market", "Unknown")

        countries[country] = countries.get(country, 0) + 1
        markets[market] = markets.get(market, 0) + 1

        if data.get("active", False):
            active_count += 1
        else:
            inactive_count += 1

    return {
        "total": len(STOCK_UNIVERSE),
        "active": active_count,
        "inactive": inactive_count,
        "countries": countries,
        "markets": markets,
    }
