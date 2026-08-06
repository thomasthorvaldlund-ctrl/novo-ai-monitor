"""
Aureum AI Ticker Service

Fælles service til opslag af tickere.

Alle øvrige moduler skal bruge denne service i stedet
for direkte opslag i Asset Registry eller Exchange Registry.
"""

from asset_registry import find_asset_by_ticker
from exchange_registry import get_exchange


def resolve_ticker(ticker):
    """
    Returnerer komplette metadata om en ticker.
    """

    asset = find_asset_by_ticker(ticker)

    if not asset:
        return None

    exchange = get_exchange(asset["exchange"])

    return {
        "ticker": asset["ticker"],
        "name": asset["name"],
        "asset_type": asset["type"],
        "exchange_id": asset["exchange"],
        "exchange": exchange,
        "asset": asset,
    }


def is_supported(ticker):
    return resolve_ticker(ticker) is not None


def get_exchange_for_ticker(ticker):
    result = resolve_ticker(ticker)

    if result:
        return result["exchange"]

    return None


def get_asset(ticker):
    result = resolve_ticker(ticker)

    if result:
        return result["asset"]

    return None
