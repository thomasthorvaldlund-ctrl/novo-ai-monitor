from combined_score_service import combined_stock_score
from openai_service import client


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

    if not alerts:
        alerts.append({
            "level": "green",
            "title": "Ingen kritiske AI-advarsler",
            "message": "Alle overvågede aktier ser stabile ud."
        })

    return alerts