import json
from pathlib import Path
from datetime import datetime

from portfolio_recommendation_service import generate_portfolio_recommendations
from portfolio_ai_service import get_portfolio_ai_insights


DECISION_FILE = Path("ai_portfolio_decisions.json")


def load_portfolio_decisions():
    if not DECISION_FILE.exists():
        return []

    with open(
        DECISION_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)



def save_portfolio_decision():

    recommendations = generate_portfolio_recommendations()
    insights = get_portfolio_ai_insights()

    insight_map = {
        item["stock"]: item
        for item in insights
    }

    decisions = []

    for item in recommendations:

        insight = insight_map.get(
            item["stock"],
            {}
        )

        decisions.append({
            "stock": item["stock"],
            "action": item["recommendation"],
            "score": item["score"],
            "weight_pct": item["weight_pct"],
            "reason": item["reason"],
            "profit_pct": insight.get("profit_pct"),
        })


    snapshot = {
        "date": datetime.now().strftime(
            "%d-%m-%Y %H:%M"
        ),
        "decisions": decisions
    }


    history = load_portfolio_decisions()

    history.append(snapshot)


    with open(
        DECISION_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            history,
            f,
            indent=2,
            ensure_ascii=False
        )


    return snapshot
