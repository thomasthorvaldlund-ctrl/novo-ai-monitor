"""
Aureum AI Market Dashboard Service

Forbereder markedsstatus til dashboards.
"""

from market_status_service import (
    get_market_status_summary,
)


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
