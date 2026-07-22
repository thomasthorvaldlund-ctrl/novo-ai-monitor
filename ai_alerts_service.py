from combined_score_service import combined_stock_score
from openai_service import client
from earnings_risk_service import get_earnings_risks


def get_ai_alerts():
    data = combined_stock_score(client)
    ranking = data.get("combined_ranking", [])

    alerts = []

    for stock in ranking:
        score = stock.get("combined_score", 100)

        if score < 45:
            alerts.append({
                "level": "red",
                "title": f"{stock['stock']}",
                "message": f"Combined Score er lav ({score})."
            })


    earnings_risks = get_earnings_risks()

    for item in earnings_risks:
        if item["risk"] == "High":
            alerts.append({
                "level": "red",
                "title": f"{item['stock']} - Regnskab nærmer sig",
                "message": (
                    f"Regnskab om {item['days_left']} dage. "
                    f"Signal: {item['signal']}. "
                    f"AI-score: {item['score']}. "
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