"""
Aureum AI Asset Registry

Central registrering af alle aktiver, som Aureum AI kender.
Bruges af AI Copilot, Portfolio Manager, Market Session Engine,
AI Stock Library og fremtidige AI-services.
"""

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
    ticker = ticker.upper()

    for asset in ASSETS.values():
        if asset["ticker"].upper() == ticker:
            return asset

    return None
