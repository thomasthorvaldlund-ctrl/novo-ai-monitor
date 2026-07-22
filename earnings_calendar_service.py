from datetime import datetime, date


EARNINGS_CALENDAR = {
    "DSV": "2026-07-23",
    "NOVO": "2026-08-06",
    "GENMAB": "2026-08-07",
    "PANDORA": "2026-08-12",
    "VESTAS": "2026-08-13",
}


def get_upcoming_earnings():
    """
    Returnerer kommende regnskaber.
    """

    today = date.today()

    earnings = []

    for stock, earnings_date in EARNINGS_CALENDAR.items():

        report_date = datetime.strptime(
            earnings_date,
            "%Y-%m-%d"
        ).date()

        days_left = (report_date - today).days

        earnings.append({
            "stock": stock,
            "date": earnings_date,
            "days_left": days_left
        })

    return sorted(
        earnings,
        key=lambda x: x["days_left"]
    )