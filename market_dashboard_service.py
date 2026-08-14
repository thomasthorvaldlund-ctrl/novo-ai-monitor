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



def _format_market_names(names):
    """
    Formaterer markedsnavne naturligt på dansk.
    """
    names = [
        name
        for name in names
        if name
    ]

    if not names:
        return ""

    if len(names) == 1:
        return names[0]

    if len(names) == 2:
        return f"{names[0]} og {names[1]}"

    return (
        ", ".join(names[:-1])
        + f" og {names[-1]}"
    )


def summarize_market_dashboard_status(markets):
    """
    Samler flere relevante markeders sessionsstatus
    til én overordnet dashboard-status.

    Denne status beskriver markedernes åbningstilstand
    og er bevidst adskilt fra market_data_status,
    som beskriver friskheden af markedsdata.
    """
    markets = [
        market
        for market in (markets or [])
        if isinstance(market, dict)
    ]

    if not markets:
        return {
            "status": "UNKNOWN",
            "label": "Ukendt",
            "status_color": "#64748b",
            "open_count": 0,
            "total_count": 0,
            "open_markets": [],
            "closed_markets": [],
            "unknown_markets": [],
            "message": (
                "Markedsstatus kunne ikke fastslås."
            ),
        }

    open_markets = [
        market.get("name")
        for market in markets
        if market.get("status") == "OPEN"
    ]

    closed_markets = [
        market.get("name")
        for market in markets
        if market.get("status") in {
            "CLOSED",
            "HOLIDAY",
            "WEEKEND",
        }
    ]

    unknown_markets = [
        market.get("name")
        for market in markets
        if market.get("status") not in {
            "OPEN",
            "CLOSED",
            "HOLIDAY",
            "WEEKEND",
        }
    ]

    total_count = len(markets)
    open_count = len(open_markets)

    if open_count == total_count:
        status = "OPEN"
        label = "Åbent"
        status_color = "#16a34a"

        names = _format_market_names(
            open_markets
        )

        if open_count == 1:
            message = f"{names} er åbent."
        else:
            message = f"{names} er åbne."

    elif open_count > 0:
        status = "PARTIAL"
        label = "Delvist åbent"
        status_color = "#2563eb"

        open_names = _format_market_names(
            open_markets
        )

        if open_count == 1:
            message = (
                f"{open_names} er åbent."
            )
        else:
            message = (
                f"{open_names} er åbne."
            )

        if closed_markets:
            closed_names = _format_market_names(
                closed_markets
            )

            if len(closed_markets) == 1:
                message += (
                    f" {closed_names} er lukket."
                )
            else:
                message += (
                    f" {closed_names} er lukkede."
                )

        if unknown_markets:
            unknown_names = _format_market_names(
                unknown_markets
            )

            message += (
                f" Status for {unknown_names} "
                "kunne ikke fastslås."
            )

    elif (
        len(closed_markets)
        == total_count
    ):
        status = "CLOSED"
        label = "Lukket"
        status_color = "#2563eb"

        names = _format_market_names(
            closed_markets
        )

        if len(closed_markets) == 1:
            message = f"{names} er lukket."
        else:
            message = f"{names} er lukkede."

    else:
        status = "UNKNOWN"
        label = "Ukendt"
        status_color = "#64748b"

        message = (
            "Markedsstatus kunne ikke fastslås "
            "for alle relevante markeder."
        )

    return {
        "status": status,
        "label": label,
        "status_color": status_color,
        "open_count": open_count,
        "total_count": total_count,
        "open_markets": open_markets,
        "closed_markets": closed_markets,
        "unknown_markets": unknown_markets,
        "message": message,
    }
