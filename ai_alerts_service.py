from combined_score_service import combined_stock_score
from openai_service import client
from earnings_risk_service import get_earnings_risks


def get_ai_alerts():
    data = combined_stock_score(client)
    ranking = data.get("combined_ranking", [])

    alerts = []

    earnings_risks = get_earnings_risks()

    priority_earnings_stocks = {
        item["stock"]: item
        for item in earnings_risks
        if item["alert_level"] in ["HIGH", "ALERT"]
    }

    for stock in ranking:
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
                    f"Regnskab om {item['days_left']} dage. "
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