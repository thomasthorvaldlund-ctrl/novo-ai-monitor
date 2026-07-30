from ai_portfolio_decision_service import load_portfolio_decisions
from combined_score_service import combined_stock_score
from openai_service import client


def evaluate_ai_result(action, performance_pct):

    if performance_pct is None:
        return "Afventer"

    if action == "BUY":
        if performance_pct > 0:
            return "God beslutning"
        return "Negativ udvikling"

    if action == "REDUCE":
        if performance_pct <= 0:
            return "God risikostyring"
        return "Forkert timing"

    if action == "HOLD":
        if abs(performance_pct) < 5:
            return "Stabil vurdering"
        elif performance_pct > 0:
            return "Positiv udvikling"
        else:
            return "Negativ udvikling"

    return "Ikke vurderet"


def get_portfolio_performance():

    history = load_portfolio_decisions()

    if not history:
        return []

    latest = history[-1]

    decisions = latest.get(
        "decisions",
        []
    )

    combined = combined_stock_score(client)

    price_map = {
        item["stock"]: item.get("price")
        for item in combined.get(
            "combined_ranking",
            []
        )
    }

    performance = []

    for item in decisions:

        stock = item.get("stock")

        decision_price = item.get(
            "decision_price"
        )

        current_price = price_map.get(
            stock
        )

        if (
            decision_price
            and current_price
        ):
            change_pct = (
                (
                    current_price
                    -
                    decision_price
                )
                /
                decision_price
            ) * 100

        else:
            change_pct = None


        performance.append({

            "stock": stock,

            "action": item.get(
                "action"
            ),

            "score": item.get(
                "score"
            ),

            "decision_price": decision_price,

            "current_price": current_price,

            "performance_pct": round(
                change_pct,
                2
            ) if change_pct is not None else None,

              "ai_result": evaluate_ai_result(
                  item.get("action"),
                  change_pct
              ),

        })


    return performance
