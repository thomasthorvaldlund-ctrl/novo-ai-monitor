from datetime import datetime

from market_data_provider import (
    get_history,
    get_provider_name,
)
from market_status_service import get_asset_market_status
from portfolio import load_portfolio_rows


def get_market_data_status():
    """
    Returnerer markedsdatastatus baseret på den aktuelle portefølje.

    Hvis mindst ét marked i porteføljen er åbent, bruges en aktie
    fra et åbent marked som reference. Ellers bruges første position.
    """

    try:
        positions = load_portfolio_rows()

        market_candidates = []

        for position in positions:
            ticker = position.get("ticker")
            stock = position.get("stock")

            if not ticker:
                continue

            session = get_asset_market_status(ticker)

            market_candidates.append({
                "stock": stock,
                "ticker": ticker,
                "session": session,
            })

        # Foretræk en position fra et åbent marked.
        reference = next(
            (
                item
                for item in market_candidates
                if item["session"].get("status") == "OPEN"
            ),
            None,
        )

        # Hvis alle markeder er lukkede, brug første aktuelle position.
        if reference is None and market_candidates:
            reference = market_candidates[0]

        # Fallback hvis porteføljen er tom.
        if reference is None:
            reference = {
                "stock": "NOVO",
                "ticker": "NOVO-B.CO",
                "session": get_asset_market_status("NOVO-B.CO"),
            }

        stock = reference["stock"]
        ticker = reference["ticker"]
        market_status = reference["session"]

        data = get_history(
            ticker,
            period="1d",
            interval="1m",
        )

        if data.empty:
            return {
                "status": "Offline",
                "status_color": "red",
                "provider": get_provider_name(),
                "last_market_update": "-",
                "age_minutes": None,
                "reference_stock": stock,
                "reference_ticker": ticker,
                "market_session": market_status,
            }

        last_timestamp = data.index[-1].to_pydatetime()
        now = datetime.now(last_timestamp.tzinfo)

        age_minutes = int(
            (now - last_timestamp).total_seconds() / 60
        )

        if market_status.get("status") != "OPEN":
            status = "Marked lukket"
            color = "blue"

            # Ved lukket marked er alderen siden sidste handel
            # ikke en egentlig dataforsinkelse.
            display_age = None

        elif age_minutes <= 15:
            status = "Live"
            color = "green"
            display_age = age_minutes

        elif age_minutes <= 60:
            status = "Forsinket"
            color = "orange"
            display_age = age_minutes

        else:
            status = "Meget forsinket"
            color = "red"
            display_age = age_minutes

        return {
            "status": status,
            "status_color": color,
            "provider": get_provider_name(),
            "last_market_update": last_timestamp.strftime("%H:%M"),
            "age_minutes": display_age,
            "reference_stock": stock,
            "reference_ticker": ticker,
            "market_session": market_status,
            "portfolio_markets": market_candidates,
        }

    except Exception as exc:
        return {
            "status": "Fejl",
            "status_color": "red",
            "provider": get_provider_name(),
            "last_market_update": "-",
            "age_minutes": None,
            "error": str(exc),
        }
