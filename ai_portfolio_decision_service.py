import json
from pathlib import Path
from datetime import datetime

from portfolio_recommendation_service import generate_portfolio_recommendations
from portfolio_ai_service import get_portfolio_ai_insights


DECISION_FILE = Path("ai_portfolio_decisions.json")


def load_portfolio_decisions():
    """
    Indlæser portfolio decision-historikken defensivt.

    Ved manglende, ugyldig eller midlertidigt ulæselig JSON
    returneres en tom historik i stedet for at vælte hele
    Decision Events / dashboard-kæden.
    """

    if not DECISION_FILE.exists():
        return []

    try:
        with open(
            DECISION_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            data = json.load(f)

        if isinstance(data, list):
            return data

        return []

    except (OSError, json.JSONDecodeError):
        return []



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
            "decision_price": insight.get("price"),
            "weight_pct": item["weight_pct"],
            "reason": item["reason"],
            "portfolio_action": item.get(
                "portfolio_action",
                "NONE"
            ),
            "portfolio_reason": item.get(
                "portfolio_reason",
                ""
            ),
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


    temp_file = DECISION_FILE.with_suffix(
        DECISION_FILE.suffix + ".tmp"
    )

    with open(
        temp_file,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            history,
            f,
            indent=2,
            ensure_ascii=False
        )

        f.flush()

        import os
        os.fsync(f.fileno())

    temp_file.replace(
        DECISION_FILE
    )


    return snapshot
