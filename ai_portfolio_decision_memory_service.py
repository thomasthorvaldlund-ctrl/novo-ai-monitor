import json
from pathlib import Path
from collections import Counter


DECISION_HISTORY_FILE = Path("ai_decision_history.json")
LEARNING_HISTORY_FILE = Path("ai_decision_learning_history.json")
PORTFOLIO_DECISIONS_FILE = Path("ai_portfolio_decisions.json")


def load_json(path):
    if not path.exists():
        return []
    
    with open(path) as f:
        return json.load(f)


def get_decision_memory():

    decisions = load_json(DECISION_HISTORY_FILE)
    learning = load_json(LEARNING_HISTORY_FILE)
    portfolio_decisions = load_json(PORTFOLIO_DECISIONS_FILE)

    actions = Counter(
        item.get("action")
        for item in decisions
        if item.get("action")
    )

    latest = decisions[0] if decisions else {}

    latest_learning = learning[0] if learning else {}

    stock_actions = {}

    for record in portfolio_decisions:
        for decision in record.get("decisions", []):
            stock = decision.get("stock")
            action = decision.get("action")

            if stock and action:
                if stock not in stock_actions:
                    stock_actions[stock] = Counter()

                stock_actions[stock][action] += 1


    stock_memory = {}

    for stock, counter in stock_actions.items():
        stock_memory[stock] = {
            "total_cases": sum(counter.values()),
            "actions": {
                "HOLD": counter.get("HOLD", 0),
                "WATCH": counter.get("WATCH", 0),
                "REDUCE": counter.get("REDUCE", 0),
                "BUY": counter.get("BUY", 0),
            },
            "dominant_action": (
                counter.most_common(1)[0][0]
                if counter else None
            ),

            "summary": (
                f"{stock} har historisk primært været vurderet med "
                f"{counter.most_common(1)[0][0]}-signaler."
                if counter else
                f"Ingen historiske data for {stock}."
            )
        }


    return {
        "total_memory_cases": len(decisions),

        "latest_decision": {
            "action": latest.get("action"),
            "confidence": latest.get("confidence"),
            "risk": latest.get("risk"),
        },

        "historical_patterns": {
            "HOLD": actions.get("HOLD",0),
            "BUY": actions.get("BUY",0),
            "WATCH": actions.get("WATCH",0),
            "REDUCE": actions.get("REDUCE",0),
        },

        "historical_accuracy": latest_learning.get(
            "accuracy",
            0
        ),

        "stock_memory": stock_memory,

        "most_common_action": (
            actions.most_common(1)[0][0]
            if actions else None
        ),

        "memory_summary":
            "AI har analyseret tidligere beslutninger og opbygger historisk hukommelse."
    }
