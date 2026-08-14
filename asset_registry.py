"""
Aureum AI Asset Registry

Central registrering af alle aktiver, som Aureum AI kender.
Bruges af AI Copilot, Portfolio Manager, Market Session Engine,
AI Stock Library og fremtidige AI-services.
"""

from functools import lru_cache

from exchange_registry import EXCHANGES
from stock_universe_service import get_all_stocks


# Legacy ASSETS bevares som førstevalg, fordi de
# indeholder mere detaljeret metadata.
#
# Alle øvrige stocks adapteres fra canonical
# stock_universe.csv.


_MARKET_EXCHANGE_ALIASES = {
    "NYSE": "NYSE",
    "Oslo Stock Exchange": "OSLO_BORS",
}


def _normalize_text(value):
    return str(
        value or ""
    ).strip().casefold()


def _exchange_id_from_stock(stock):
    market = str(
        stock.get(
            "market",
            "",
        )
        or ""
    ).strip()

    if not market:
        return None

    alias = (
        _MARKET_EXCHANGE_ALIASES
        .get(
            market
        )
    )

    if (
        alias
        and alias in EXCHANGES
    ):
        return alias

    normalized_market = (
        _normalize_text(
            market
        )
    )

    for (
        exchange_id,
        exchange,
    ) in EXCHANGES.items():

        exchange_name = (
            _normalize_text(
                exchange.get(
                    "name"
                )
            )
        )

        if (
            exchange_name
            and exchange_name
            == normalized_market
        ):
            return exchange_id

    ticker = str(
        stock.get(
            "ticker",
            "",
        )
        or ""
    ).strip().upper()

    if ticker:
        matches = []

        for (
            exchange_id,
            exchange,
        ) in EXCHANGES.items():

            suffixes = (
                exchange.get(
                    "suffixes",
                    []
                )
                or []
            )

            if any(
                ticker.endswith(
                    str(suffix).upper()
                )
                for suffix
                in suffixes
                if suffix
            ):
                matches.append(
                    exchange_id
                )

        if len(matches) == 1:
            return matches[0]

    return None


@lru_cache(maxsize=1)
def _canonical_ticker_index():
    index = {}

    for stock in (
        get_all_stocks()
        .values()
    ):
        ticker = str(
            stock.get(
                "ticker",
                "",
            )
            or ""
        ).strip().upper()

        if ticker:
            index[
                ticker
            ] = stock

    return index


def _canonical_asset_by_ticker(ticker):
    normalized = str(
        ticker or ""
    ).strip().upper()

    if not normalized:
        return None

    stock = (
        _canonical_ticker_index()
        .get(
            normalized
        )
    )

    if not stock:
        return None

    exchange_id = (
        _exchange_id_from_stock(
            stock
        )
    )

    exchange = (
        EXCHANGES.get(
            exchange_id
        )
        if exchange_id
        else None
    )

    sector = stock.get(
        "sector"
    )

    if (
        not sector
        or str(
            sector
        ).strip().casefold()
        == "unknown"
    ):
        sector = None

    return {
        "ticker":
            stock.get(
                "ticker"
            ),
        "name":
            stock.get(
                "name"
            ),
        "type":
            "Stock",
        "exchange":
            exchange_id,
        "currency":
            stock.get(
                "currency"
            ),
        "country":
            stock.get(
                "country"
            ),
        "region":
            (
                exchange.get(
                    "region"
                )
                if exchange
                else None
            ),
        "sector":
            sector,
        "industry":
            None,
    }


ASSETS = {

    "NOVO_B_CO": {
        "ticker": "NOVO-B.CO",
        "name": "Novo Nordisk",
        "type": "Stock",
        "exchange": "NASDAQ_CPH",
        "currency": "DKK",
        "country": "Denmark",
        "region": "Europe",
        "sector": "Healthcare",
        "industry": "Pharmaceuticals",
    },

    "DSV_CO": {
        "ticker": "DSV.CO",
        "name": "DSV",
        "type": "Stock",
        "exchange": "NASDAQ_CPH",
        "currency": "DKK",
        "country": "Denmark",
        "region": "Europe",
        "sector": "Industrials",
        "industry": "Logistics",
    },

    "VWS_CO": {
        "ticker": "VWS.CO",
        "name": "Vestas",
        "type": "Stock",
        "exchange": "NASDAQ_CPH",
        "currency": "DKK",
        "country": "Denmark",
        "region": "Europe",
        "sector": "Industrials",
        "industry": "Renewable Energy",
    },

    "NVDA": {
        "ticker": "NVDA",
        "name": "NVIDIA",
        "type": "Stock",
        "exchange": "NASDAQ",
        "currency": "USD",
        "country": "USA",
        "region": "North America",
        "sector": "Technology",
        "industry": "Semiconductors",
    },

    "MSFT": {
        "ticker": "MSFT",
        "name": "Microsoft",
        "type": "Stock",
        "exchange": "NASDAQ",
        "currency": "USD",
        "country": "USA",
        "region": "North America",
        "sector": "Technology",
        "industry": "Software",
    },

    "META": {
        "ticker": "META",
        "name": "Meta Platforms",
        "type": "Stock",
        "exchange": "NASDAQ",
        "currency": "USD",
        "country": "USA",
        "region": "North America",
        "sector": "Technology",
        "industry": "Internet",
    },

    "AMZN": {
        "ticker": "AMZN",
        "name": "Amazon",
        "type": "Stock",
        "exchange": "NASDAQ",
        "currency": "USD",
        "country": "USA",
        "region": "North America",
        "sector": "Consumer",
        "industry": "E-commerce",
    },

    "GOOGL": {
        "ticker": "GOOGL",
        "name": "Alphabet",
        "type": "Stock",
        "exchange": "NASDAQ",
        "currency": "USD",
        "country": "USA",
        "region": "North America",
        "sector": "Technology",
        "industry": "Internet",
    },

    "AAPL": {
        "ticker": "AAPL",
        "name": "Apple",
        "type": "Stock",
        "exchange": "NASDAQ",
        "currency": "USD",
        "country": "USA",
        "region": "North America",
        "sector": "Technology",
        "industry": "Consumer Electronics",
    },

    "TSLA": {
        "ticker": "TSLA",
        "name": "Tesla",
        "type": "Stock",
        "exchange": "NASDAQ",
        "currency": "USD",
        "country": "USA",
        "region": "North America",
        "sector": "Automotive",
        "industry": "Electric Vehicles",
    },

    "ASML_AS": {
        "ticker": "ASML.AS",
        "name": "ASML",
        "type": "Stock",
        "exchange": "EURONEXT_AMS",
        "currency": "EUR",
        "country": "Netherlands",
        "region": "Europe",
        "sector": "Technology",
        "industry": "Semiconductors",
    },

    "SAP_DE": {
        "ticker": "SAP.DE",
        "name": "SAP",
        "type": "Stock",
        "exchange": "XETRA",
        "currency": "EUR",
        "country": "Germany",
        "region": "Europe",
        "sector": "Technology",
        "industry": "Software",
    },
}


def get_asset(asset_id):
    return ASSETS.get(asset_id)


def list_assets():
    return sorted(ASSETS.keys())


def find_asset_by_ticker(ticker):
    normalized = str(
        ticker or ""
    ).strip().upper()

    if not normalized:
        return None

    # Legacy registry har førsteprioritet og
    # bevarer eksisterende beriget metadata.
    for asset in ASSETS.values():

        if (
            str(
                asset.get(
                    "ticker",
                    "",
                )
            ).strip().upper()
            == normalized
        ):
            return asset

    # Alle øvrige aktier adapteres fra det
    # canonical stock universe.
    return _canonical_asset_by_ticker(
        normalized
    )
