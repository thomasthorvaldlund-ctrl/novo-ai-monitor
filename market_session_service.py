"""
Aureum AI Market Session Service

Bestemmer om et marked er åbent eller lukket
baseret på børsens lokale tidszone og handelstider.
"""

from datetime import datetime, time
from zoneinfo import ZoneInfo

from exchange_registry import get_exchange
from ticker_service import get_exchange_for_ticker
from holiday_registry import is_holiday


def _parse_time(value):
    hour, minute = map(int, value.split(":"))
    return time(hour, minute)


def get_market_session(exchange_id):
    """
    Returnerer status for en børs.
    """

    exchange = get_exchange(exchange_id)

    if not exchange:
        return {
            "status": "UNKNOWN",
            "label": "Ukendt marked",
        }

    now = datetime.now(
        ZoneInfo(exchange["timezone"])
    )

    holiday = is_holiday(
        exchange_id,
        now.date()
    )

    if holiday:
        return {
            "exchange": exchange_id,
            "name": exchange["name"],
            "status": "HOLIDAY",
            "label": "Marked lukket",
            "reason": holiday["name"],
            "local_time": now.strftime("%Y-%m-%d %H:%M"),
        }

    holiday = is_holiday(
        exchange_id,
        now.date()
    )

    if holiday:
        return {
            "exchange": exchange_id,
            "name": exchange["name"],
            "status": "HOLIDAY",
            "label": "Marked lukket",
            "reason": holiday["name"],
            "local_time": now.strftime("%Y-%m-%d %H:%M"),
        }

    weekday = now.weekday()

    if weekday in exchange["weekend"]:
        return {
            "exchange": exchange_id,
            "status": "WEEKEND",
            "label": "Weekend",
            "local_time": now.strftime("%Y-%m-%d %H:%M"),
        }

    open_time = _parse_time(exchange["open"])
    close_time = _parse_time(exchange["close"])

    current_time = now.time()

    if open_time <= current_time <= close_time:
        status = "OPEN"
        label = "Åben"
    else:
        status = "CLOSED"
        label = "Marked lukket"

    return {
        "exchange": exchange_id,
        "name": exchange["name"],
        "status": status,
        "label": label,
        "local_time": now.strftime("%Y-%m-%d %H:%M"),
        "open": exchange["open"],
        "close": exchange["close"],
    }


def get_market_session_for_ticker(ticker):
    """
    Finder marked via ticker.
    """

    exchange = get_exchange_for_ticker(ticker)

    if not exchange:
        return {
            "status": "UNKNOWN",
            "label": "Ukendt ticker",
        }

    exchange_id = None

    from ticker_service import resolve_ticker

    resolved = resolve_ticker(ticker)

    if resolved:
        exchange_id = resolved["exchange_id"]

    return get_market_session(exchange_id)
