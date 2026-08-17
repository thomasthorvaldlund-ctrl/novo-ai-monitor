from combined_score_service import combined_stock_score
from openai_service import client
from earnings_risk_service import get_earnings_risks
from portfolio_stock_service import (
    get_monitored_stocks,
    get_monitored_stock_names,
)


def get_ai_alerts(
    ranking=None,
    earnings_risks=None,
):
    if ranking is None:
        data = combined_stock_score(
            client
        )
        ranking = data.get(
            "combined_ranking",
            [],
        )
    elif not isinstance(
        ranking,
        list,
    ):
        ranking = []

    monitored_stocks = {
        str(value).strip().upper()
        for value in get_monitored_stocks()
    }

    monitored_stock_names = {
        str(value).strip().upper()
        for value in get_monitored_stock_names()
    }

    alerts = []

    if earnings_risks is None:
        earnings_risks = get_earnings_risks(
            ranking
        )

    priority_earnings_stocks = {
        item["stock"]: item
        for item in earnings_risks
        if item["alert_level"] in ["HIGH", "ALERT"]
    }

    for stock in ranking:

        ticker = str(
            stock.get(
                "ticker",
                "",
            )
        ).strip().upper()

        if ticker not in monitored_stocks:
            continue

        name = stock["stock"]
        score = stock.get("combined_score", 100)

        if score < 45:

            if name in priority_earnings_stocks:
                item = priority_earnings_stocks[name]

                alerts.append({
                    "level": "red",
                    "title": f"{name} - Høj risiko før regnskab",
                    "message": (
                        f"AI-score: {score}. "
                        f"Signal: {item['signal']}. "
                        f"Regnskab om {item['days_left']} dage. "
                        f"Lav score kombineret med kommende regnskab."
                    )
                })

            else:
                alerts.append({
                    "level": "red",
                    "title": f"{name}",
                    "message": f"Combined Score er lav ({score})."
                })

    existing_alert_stocks = [
        a["title"].split(" - ")[0]
        for a in alerts
    ]

    for item in earnings_risks:

        item_stock = str(
            item.get(
                "stock",
                "",
            )
        ).strip().upper()

        item_ticker = str(
            item.get(
                "ticker",
                "",
            )
        ).strip().upper()

        is_portfolio_stock = (
            bool(
                item.get(
                    "in_portfolio",
                    False,
                )
            )
            or item_stock in monitored_stock_names
            or item_ticker in monitored_stocks
        )

        if not is_portfolio_stock:
            continue

        if (
            item["alert_level"] in ["HIGH", "ALERT"]
            and item["stock"] not in existing_alert_stocks
        ):
            alerts.append({
                "level": "red",
                "title": f"{item['stock']} - Høj risiko før regnskab",
                "message": (
                    f"AI-score: {item['score']}. "
                    f"Signal: {item['signal']}. "
                    f"{item['date_message']}. "
                    f"{item['message']}"
                )
            })

    if not alerts:
        alerts.append({
            "level": "green",
            "title": "Ingen kritiske AI-advarsler",
            "message": "Alle overvågede aktier ser stabile ud."
        })

    return alerts

def get_active_ai_alerts(alerts=None):
    """
    Returnerer kun aktive AI-alerts.

    Grønne statusbeskeder er informative fallback-beskeder
    og skal ikke tælles som aktive eller kritiske alerts.
    """
    if alerts is None:
        alerts = get_ai_alerts()

    if not isinstance(alerts, list):
        return []

    return [
        alert
        for alert in alerts
        if isinstance(alert, dict)
        and alert.get("level") != "green"
    ]


def get_active_ai_alert_count(alerts=None):
    """
    Returnerer antal aktive AI-alerts.
    """
    return len(get_active_ai_alerts(alerts))
