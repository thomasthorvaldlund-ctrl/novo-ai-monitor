"""
Aureum AI Market Dashboard Service

Forbereder markedsstatus til dashboards.
"""

from market_status_service import (
    get_market_status_summary,
    get_asset_market_status,
)
from portfolio import load_portfolio_rows
from ticker_service import resolve_ticker


DEFAULT_MARKETS = [
    {
        "name": "Danmark",
        "ticker": "NOVO-B.CO",
        "flag": "🇩🇰",
    },
    {
        "name": "USA",
        "ticker": "NVDA",
        "flag": "🇺🇸",
    },
    {
        "name": "Europa",
        "ticker": "ASML.AS",
        "flag": "🇪🇺",
    },
    {
        "name": "Tyskland",
        "ticker": "SAP.DE",
        "flag": "🇩🇪",
    },
]


def get_market_dashboard_status():
    """
    Returnerer globale markedsstatus til UI.
    """

    tickers = [
        item["ticker"]
        for item in DEFAULT_MARKETS
    ]

    statuses = get_market_status_summary(
        tickers
    )

    result = []

    for market, status in zip(
        DEFAULT_MARKETS,
        statuses
    ):
        result.append(
            {
                "name": market["name"],
                "flag": market["flag"],
                **status,
            }
        )

    return result

def get_portfolio_market_status():
    """
    Returnerer unikke markeder for aktierne
    i den aktuelle portefølje.
    """
    positions = load_portfolio_rows()

    markets = []
    seen_exchanges = set()

    for position in positions:
        ticker = position.get("ticker")

        if not ticker:
            continue

        resolved = resolve_ticker(ticker)

        if not resolved:
            continue

        exchange_id = resolved.get("exchange_id")

        if not exchange_id:
            continue

        if exchange_id in seen_exchanges:
            continue

        seen_exchanges.add(exchange_id)

        status = get_asset_market_status(ticker)
        exchange = resolved.get("exchange", {})

        markets.append({
            "name": exchange.get("name", exchange_id),
            "ticker": ticker,
            "exchange_id": exchange_id,
            "country": exchange.get("country"),
            "city": exchange.get("city"),
            "currency": exchange.get("currency"),
            "portfolio_market": True,
            **status,
        })

    return markets

CORE_MARKETS = [
    {
        "name": "Danmark",
        "ticker": "NOVO-B.CO",
        "flag": "🇩🇰",
    },
    {
        "name": "USA Nasdaq",
        "ticker": "NVDA",
        "flag": "🇺🇸",
    },
    {
        "name": "Tyskland",
        "ticker": "SAP.DE",
        "flag": "🇩🇪",
    },
]


def get_relevant_market_status():
    """
    Kombinerer aktuelle porteføljemarkeder med
    globale kernemarkeder uden dubletter.
    """
    portfolio_markets = get_portfolio_market_status()

    result = []
    seen_exchanges = set()

    for market in portfolio_markets:
        exchange_id = market.get("exchange_id") or market.get("exchange")

        if exchange_id:
            seen_exchanges.add(exchange_id)

        market = dict(market)
        market["source"] = "portfolio"
        result.append(market)

    for core in CORE_MARKETS:
        status = get_asset_market_status(core["ticker"])
        exchange_id = status.get("exchange")

        if exchange_id in seen_exchanges:
            continue

        seen_exchanges.add(exchange_id)

        result.append({
            "name": core["name"],
            "flag": core["flag"],
            "ticker": core["ticker"],
            "exchange_id": exchange_id,
            "portfolio_market": False,
            "source": "core",
            **status,
        })

    return result

