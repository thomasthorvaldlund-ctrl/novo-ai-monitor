from portfolio_summary_service import get_portfolio_summary
from combined_score_service import combined_stock_score


def simulate_rebalancing(investment_amount):
    """
    Simulerer hvordan et nyt investeringsbeløb
    kan bruges til at forbedre porteføljen.
    """

    portfolio = get_portfolio_summary()

    positions = portfolio.get("position_details", [])

    if not positions:
        return {
            "message": "Ingen porteføljedata tilgængelig."
        }

    return {
        "investment_amount": investment_amount,
        "current_risk": portfolio.get("portfolio_risk"),
        "positions": positions,
        "message": "Simulation klar."
    }


def generate_rebalancing_plan(investment_amount):
    """
    Genererer forslag til ny investering.
    """

    portfolio = get_portfolio_summary()

    positions = portfolio.get("position_details", [])

    if not positions:
        return {
            "message": "Ingen portefølje tilgængelig."
        }

    largest = sorted(
        positions,
        key=lambda x: float(
            str(x.get("weight_pct", "0")).replace("%", "")
        ),
        reverse=True
    )

    plan = []

    first = largest[0]["stock"]

    plan.append({
        "stock": first,
        "amount": round(investment_amount * 0.3),
        "reason": "Bevarer eksponering mod stærkeste position."
    })

    candidates = get_ai_candidates()

    if candidates:

        ai_weights = calculate_ai_weights(candidates)

        available_amount = investment_amount * 0.7

        for candidate in ai_weights:

            amount = round(
                available_amount *
                (candidate["weight"] / 100)
            )

            plan.append({
                "stock": candidate["stock"],
                "amount": amount,
                "reason": (
                    f"{candidate['reason']} "
                    f"AI vægt: {candidate['weight']}%."
                )
            })

    else:

        plan.append({
            "stock": "Diversificering",
            "amount": round(investment_amount * 0.7),
            "reason": "Reducerer koncentrationsrisiko."
        })

    return {
        "investment_amount": investment_amount,
        "plan": plan,
        "message": "AI investeringsplan genereret."
    }


def get_ai_candidates():
    """
    Finder AI-kandidater baseret på Combined Score.
    """

    data = combined_stock_score(None)

    ranking = data.get("combined_ranking", [])

    portfolio = get_portfolio_summary()

    owned = [
        p["stock"]
        for p in portfolio.get("position_details", [])
    ]

    candidates = []

    for stock in ranking:

        if stock["stock"] in owned:
            continue

        candidates.append({
            "stock": stock["stock"],
            "score": stock.get("combined_score"),
            "rating": stock.get("rating"),
            "reason": (
                f"AI score {stock.get('combined_score')} "
                f"med rating {stock.get('rating')}."
            )
        })

        if len(candidates) >= 3:
            break

    return candidates


def calculate_ai_weights(candidates):
    """
    Beregner vægte baseret på AI score.
    """

    if not candidates:
        return []

    total_score = sum(
        c.get("score", 0)
        for c in candidates
    )

    weighted = []

    for candidate in candidates:

        score = candidate.get("score", 0)

        weight = round(
            (score / total_score) * 100,
            1
        )

        weighted.append({
            "stock": candidate["stock"],
            "score": score,
            "weight": weight,
            "reason": candidate["reason"]
        })

    return weighted
