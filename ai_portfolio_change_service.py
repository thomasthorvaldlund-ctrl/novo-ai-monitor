from ai_portfolio_decision_service import load_portfolio_decisions


SCORE_CHANGE_THRESHOLD = 5
WEIGHT_CHANGE_THRESHOLD = 3


def get_portfolio_changes():
    """
    Sammenligner seneste AI porteføljebeslutning
    med den tidligere analyse.
    Finder relevante ændringer.
    """

    history = load_portfolio_decisions()

    if len(history) < 2:
        return []

    previous = history[-2]
    latest = history[-1]

    previous_map = {
        item["stock"]: item
        for item in previous.get("decisions", [])
    }

    changes = []

    for item in latest.get("decisions", []):

        stock = item.get("stock")

        old = previous_map.get(stock)

        if not old:
            continue


        old_score = old.get("score", 0)
        new_score = item.get("score", 0)

        score_change = new_score - old_score


        old_weight = old.get("weight_pct", 0)
        new_weight = item.get("weight_pct", 0)

        weight_change = new_weight - old_weight


        action_changed = (
            old.get("action")
            !=
            item.get("action")
        )

        score_changed = (
            abs(score_change)
            >= SCORE_CHANGE_THRESHOLD
        )

        weight_changed = (
            abs(weight_change)
            >= WEIGHT_CHANGE_THRESHOLD
        )


        if (
            action_changed
            or score_changed
            or weight_changed
        ):

            changes.append({

                "stock": stock,

                "old_action": old.get("action"),
                "new_action": item.get("action"),

                "old_score": old_score,
                "new_score": new_score,

                "score_change": round(
                    score_change,
                    1
                ),

                "old_weight": round(
                    old_weight,
                    2
                ),

                "new_weight": round(
                    new_weight,
                    2
                ),

                "weight_change": round(
                    weight_change,
                    2
                ),

            })


    return changes
