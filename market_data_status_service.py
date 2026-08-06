from datetime import datetime

from market_data_provider import (
    get_history,
    get_provider_name,
)


def get_market_data_status():
    """
    Returnerer status for markedsdata fra Yahoo Finance.
    """

    try:
        data = get_history(
            "NOVO",
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
            }

        last_timestamp = data.index[-1].to_pydatetime()
        now = datetime.now(last_timestamp.tzinfo)

        age_minutes = int(
            (now - last_timestamp).total_seconds() / 60
        )

        if age_minutes <= 15:
            status = "Live"
            color = "green"
        elif age_minutes <= 60:
            status = "Forsinket"
            color = "orange"
        else:
            status = "Meget forsinket"
            color = "red"

        return {
            "status": status,
            "status_color": color,
            "provider": get_provider_name(),
            "last_market_update": last_timestamp.strftime("%H:%M"),
            "age_minutes": age_minutes,
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
