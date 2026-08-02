from ai_portfolio_memory_center_service import get_memory_center


def get_memory_intelligence():

    memory = get_memory_center()

    risk_stocks = []
    stable_stocks = []

    insights = memory["insights"]


    for item in insights.get("risk_alerts", []):

        risk_stocks.append({
            "stock": item["stock"],
            "reason": item["message"]
        })


    for item in insights.get("stable_stocks", []):

        stable_stocks.append({
            "stock": item["stock"],
            "reason": item["message"]
        })


    if len(risk_stocks) > len(stable_stocks):

        assessment = "Forhøjet risiko"

    elif len(risk_stocks) == 0:

        assessment = "Lav risiko"

    else:

        assessment = "Moderat risiko"


    return {

        "portfolio_assessment": assessment,

        "risk_stocks": risk_stocks,

        "stable_stocks": stable_stocks,

        "summary":
            (
                f"AI har identificeret "
                f"{len(risk_stocks)} historiske risikopositioner "
                f"og {len(stable_stocks)} stabile positioner."
            )
    }
