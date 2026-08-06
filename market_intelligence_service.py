"""
Aureum AI Market Intelligence Service

Samler global markedsstatus og laver
en AI-venlig fortolkning af markedstilstanden.
"""

from market_dashboard_service import (
    get_market_dashboard_status,
)

from market_freshness_service import (
    get_market_data_freshness,
)


def get_market_intelligence():
    markets = get_market_dashboard_status()

    data_quality = {}

    for market in markets:
        data_quality[market["name"]] = get_market_data_freshness(
            market
        )

    open_markets = [
        market["name"]
        for market in markets
        if market["status"] == "OPEN"
    ]

    closed_markets = [
        market["name"]
        for market in markets
        if market["status"] in [
            "CLOSED",
            "HOLIDAY",
            "WEEKEND",
        ]
    ]

    if len(open_markets) == len(markets):
        condition = "Globalt åbent"

    elif len(open_markets) == 0:
        condition = "Globalt lukket"

    else:
        condition = "Blandede markeder"


    if closed_markets:
        data_context = (
            "Nogle markeder er lukkede. "
            "Seneste officielle lukkekurser anvendes."
        )
    else:
        data_context = (
            "De overvågede markeder er aktive."
        )


    return {
        "markets": markets,
        "data_quality": data_quality,
        "open_markets": open_markets,
        "closed_markets": closed_markets,
        "market_condition": condition,
        "data_context": data_context,
    }
