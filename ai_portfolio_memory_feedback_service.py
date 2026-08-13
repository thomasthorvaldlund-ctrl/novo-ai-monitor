import json
from pathlib import Path

from aureum_paths import data_path


DECISION_FILE = data_path(
    "ai_portfolio_decisions.json"
)


def load_decisions():

    if not DECISION_FILE.exists():
        return []

    with open(DECISION_FILE) as f:
        return json.load(f)



def evaluate_decision(action, profit_pct):

    if action == "BUY":

        if profit_pct > 5:
            return "Korrekt"

        return "Forkert"


    if action == "HOLD":

        if -5 <= profit_pct <= 5:
            return "Korrekt"

        if profit_pct < -5:
            return "Forkert"

        return "Neutral"


    if action == "WATCH":

        if profit_pct < -5:
            return "Forkert"

        if profit_pct <= 5:
            return "Neutral"

        return "Forkert"


    if action == "REDUCE":

        if profit_pct < 0:
            return "Korrekt"

        if profit_pct > 10:
            return "Forkert"

        return "Neutral"


    return "Neutral"


def get_memory_feedback():

    records = load_decisions()

    total = 0
    correct = 0
    neutral = 0
    incorrect = 0

    feedback = []

    action_stats = {}


    for record in records:

        for decision in record.get("decisions", []):

            stock = decision.get("stock")
            action = decision.get("action")
            profit = decision.get("profit_pct")


            if profit is None:
                continue

            try:
                if profit != profit:
                    continue
            except Exception:
                continue


            result = evaluate_decision(
                action,
                profit
            )

            if action not in action_stats:
                action_stats[action] = {
                    "total": 0,
                    "correct": 0,
                    "neutral": 0,
                    "incorrect": 0
                }

            action_stats[action]["total"] += 1

            if result == "Korrekt":
                action_stats[action]["correct"] += 1

            elif result == "Neutral":
                action_stats[action]["neutral"] += 1

            else:
                action_stats[action]["incorrect"] += 1       

            total += 1

            if result == "Korrekt":
                correct += 1
                status = "Korrekt"

            elif result == "Neutral":
                neutral += 1
                status = "Neutral"

            else:
                incorrect += 1
                status = "Forkert"


            feedback.append({
                "stock": stock,
                "action": action,
                "profit_pct": profit,
                "result": status
            })


    accuracy = 0

    if total:
        accuracy = round(
            correct / total * 100,
            1
        )


    neutral_rate = 0
    error_rate = 0

    if total:
        neutral_rate = round(
            neutral / total * 100,
            1
        )

        error_rate = round(
            incorrect / total * 100,
            1
        )


    return {

        "evaluated_cases": total,

        "correct_decisions": correct,

        "neutral_decisions": neutral,

        "incorrect_decisions": incorrect,

        "accuracy": accuracy,

        "neutral_rate": neutral_rate,

        "error_rate": error_rate,
        
        "action_stats": action_stats,

        "feedback": feedback[-20:]
    }
