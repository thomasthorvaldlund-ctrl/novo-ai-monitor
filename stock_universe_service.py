"""
Central administration af Aureum AI Platforms aktieunivers.

Denne service bliver senere udvidet til at understøtte
1.000+ aktier, markeder, sektorer og prioriteringsniveauer.
"""

import csv

from aureum_paths import project_path


UNIVERSE_FILE = project_path(
    "stock_universe.csv"
)

_REQUIRED_COLUMNS = {
    "symbol",
    "name",
    "ticker",
    "country",
    "market",
    "currency",
    "sector",
    "news_query",
    "active",
}


def _parse_active(value):
    normalized = str(
        value or ""
    ).strip().lower()

    if normalized in {
        "1",
        "true",
        "yes",
        "on",
    }:
        return True

    if normalized in {
        "0",
        "false",
        "no",
        "off",
    }:
        return False

    raise ValueError(
        f"Ugyldig active-værdi: {value!r}"
    )


def _load_stock_universe():
    if not UNIVERSE_FILE.exists():
        raise RuntimeError(
            "Canonical stock universe mangler: "
            f"{UNIVERSE_FILE}"
        )

    universe = {}
    seen_tickers = set()

    with UNIVERSE_FILE.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        reader = csv.DictReader(
            handle
        )

        fieldnames = set(
            reader.fieldnames
            or []
        )

        missing = (
            _REQUIRED_COLUMNS
            - fieldnames
        )

        if missing:
            raise RuntimeError(
                "Canonical stock universe mangler "
                "kolonner: "
                + ", ".join(
                    sorted(missing)
                )
            )

        for line_number, row in enumerate(
            reader,
            start=2,
        ):
            symbol = str(
                row.get(
                    "symbol",
                    ""
                )
            ).strip().upper()

            ticker = str(
                row.get(
                    "ticker",
                    ""
                )
            ).strip()

            name = str(
                row.get(
                    "name",
                    ""
                )
            ).strip()

            if not symbol:
                raise RuntimeError(
                    "Tom symbol-værdi i "
                    f"{UNIVERSE_FILE} "
                    f"på linje {line_number}."
                )

            if not ticker:
                raise RuntimeError(
                    "Tom ticker-værdi i "
                    f"{UNIVERSE_FILE} "
                    f"på linje {line_number}."
                )

            if not name:
                raise RuntimeError(
                    "Tom name-værdi i "
                    f"{UNIVERSE_FILE} "
                    f"på linje {line_number}."
                )

            if symbol in universe:
                raise RuntimeError(
                    "Duplikeret symbol i "
                    f"{UNIVERSE_FILE}: "
                    f"{symbol}"
                )

            ticker_key = (
                ticker.upper()
            )

            if ticker_key in seen_tickers:
                raise RuntimeError(
                    "Duplikeret ticker i "
                    f"{UNIVERSE_FILE}: "
                    f"{ticker}"
                )

            seen_tickers.add(
                ticker_key
            )

            universe[symbol] = {
                "name": name,
                "ticker": ticker,
                "country": str(
                    row.get(
                        "country",
                        ""
                    )
                ).strip(),
                "market": str(
                    row.get(
                        "market",
                        ""
                    )
                ).strip(),
                "currency": str(
                    row.get(
                        "currency",
                        ""
                    )
                ).strip(),
                "sector": str(
                    row.get(
                        "sector",
                        ""
                    )
                ).strip(),
                "news_query": str(
                    row.get(
                        "news_query",
                        ""
                    )
                ).strip(),
                "active": _parse_active(
                    row.get(
                        "active"
                    )
                ),
            }

    return universe


STOCK_UNIVERSE = (
    _load_stock_universe()
)



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


def get_news_query(name):
    """
    Returnerer Google News-søgestrengen for en aktie.

    Hvis aktien ikke har en specifik søgestreng,
    bruges et generisk fallback baseret på aktiens navn.
    """
    stock_name = name.upper()
    stock = get_stock_metadata(stock_name)

    if stock is None:
        return f"{stock_name} stock"

    return stock.get("news_query") or f"{stock_name} stock"
