import json
from pathlib import Path
from collections import Counter


FILE = Path("ai_portfolio_decisions.json")


def load_decisions():
    if not FILE.exists():
        return []

    with open(FILE) as f:
        return json.load(f)


def get_memory_trends():

    data = load_decisions()

    recent = data[:30]
    older = data[30:60]

    stocks = {}

    for record in data:
        for decision in record.get("decisions", []):
            stock = decision.get("stock")

            if stock:
                stocks.setdefault(stock, {
                    "recent": Counter(),
                    "older": Counter()
                })


    for record in recent:
        for decision in record.get("decisions", []):
            stock = decision.get("stock")
            action = decision.get("action")

            if stock and action:
                stocks[stock]["recent"][action] += 1


    for record in older:
        for decision in record.get("decisions", []):
            stock = decision.get("stock")
            action = decision.get("action")

            if stock and action:
                stocks[stock]["older"][action] += 1


    result = {}

    for stock, values in stocks.items():

        recent_action = (
            values["recent"].most_common(1)[0][0]
            if values["recent"]
            else None
        )

        older_action = (
            values["older"].most_common(1)[0][0]
            if values["older"]
            else None
        )

        if recent_action == older_action:

            if recent_action == "REDUCE":
                trend = "Vedvarende negativ"
                explanation = (
                    f"{stock} har fastholdt REDUCE-signaler "
                    "over flere historiske perioder."
                )

            elif recent_action == "HOLD":
                trend = "Stabil"
                explanation = (
                    f"{stock} har haft en stabil HOLD-vurdering "
                    "over de seneste perioder."
                )

            else:
                trend = "Uændret"
                explanation = (
                    f"{stock} har bevaret samme signalmønster over tid."
                )

        else:
            trend = "Ændret"
            explanation = (
                f"{stock} har ændret historisk signalmønster "
                f"fra {older_action} til {recent_action}."
            )


        result[stock] = {
            "recent_pattern": dict(values["recent"]),
            "older_pattern": dict(values["older"]),
            "recent_dominant": recent_action,
            "older_dominant": older_action,
            "trend": trend,
            "explanation": explanation,
        }

    return result
