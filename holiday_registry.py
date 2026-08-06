"""
Aureum AI Holiday Registry

Central oversigt over børshelligdage.
"""

from datetime import date


HOLIDAYS = {
    "NASDAQ": [
        {
            "date": "2026-01-01",
            "name": "New Year's Day",
        },
        {
            "date": "2026-12-25",
            "name": "Christmas Day",
        },
    ],

    "NYSE": [
        {
            "date": "2026-01-01",
            "name": "New Year's Day",
        },
        {
            "date": "2026-12-25",
            "name": "Christmas Day",
        },
    ],

    "NASDAQ_CPH": [
        {
            "date": "2026-12-25",
            "name": "Christmas Day",
        },
    ],

    "XETRA": [
        {
            "date": "2026-12-25",
            "name": "Christmas Day",
        },
    ],

    "EURONEXT_AMS": [
        {
            "date": "2026-12-25",
            "name": "Christmas Day",
        },
    ],
}


def get_holidays(exchange_id):
    return HOLIDAYS.get(exchange_id, [])


def is_holiday(exchange_id, check_date=None):
    if check_date is None:
        check_date = date.today()

    if isinstance(check_date, date):
        check_date = check_date.isoformat()

    for holiday in get_holidays(exchange_id):
        if holiday["date"] == check_date:
            return holiday

    return None
