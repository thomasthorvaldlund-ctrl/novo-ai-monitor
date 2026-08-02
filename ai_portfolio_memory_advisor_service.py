from ai_portfolio_memory_insight_service import get_memory_insights


def get_memory_advisor():

    insights = get_memory_insights()

    advice = []

    for item in insights.get("risk_alerts", []):

        advice.append({
            "stock": item["stock"],
            "recommendation": "Forsigtighed",
            "reason": item["message"]
        })


    for item in insights.get("stable_stocks", []):

        advice.append({
            "stock": item["stock"],
            "recommendation": "Bevar position",
            "reason": item["message"]
        })


    for item in insights.get("changed_stocks", []):

        advice.append({
            "stock": item["stock"],
            "recommendation": "Overvåg ændring",
            "reason": item["message"]
        })


    return {
        "advice": advice,

        "summary":
            f"AI Memory Advisor har genereret "
            f"{len(advice)} historiske anbefalinger."
    }
