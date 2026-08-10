from ai_portfolio_memory_trend_service import get_memory_trends
from portfolio import load_portfolio_rows


def get_memory_insights():

    trends = get_memory_trends()

    current_stocks = {
        row.get("stock")
        for row in load_portfolio_rows()
        if row.get("stock")
    }

    risk_alerts = []
    stable_stocks = []
    changed_stocks = []


    for stock, data in trends.items():

        if stock not in current_stocks:
            continue

        trend = data.get("trend")
        explanation = data.get("explanation")


        if trend == "Vedvarende negativ":

            risk_alerts.append({
                "stock": stock,
                "type": trend,
                "message": explanation
            })


        elif trend == "Stabil":

            stable_stocks.append({
                "stock": stock,
                "message": explanation
            })


        elif trend == "Ændret":

            changed_stocks.append({
                "stock": stock,
                "message": explanation
            })


    return {

        "risk_alerts": risk_alerts,

        "stable_stocks": stable_stocks,

        "changed_stocks": changed_stocks,

        "summary":
            f"AI har identificeret "
            f"{len(risk_alerts)} vedvarende negative mønstre, "
            f"{len(stable_stocks)} stabile mønstre og "
            f"{len(changed_stocks)} ændringer."
    }
