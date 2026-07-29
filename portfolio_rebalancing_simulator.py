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

    candidates = filter_ai_candidates(
        get_ai_candidates()
    )

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

        candidate = {
            "stock": stock["stock"],
            "score": stock.get("combined_score"),
            "technical_score": stock.get("technical_score", 0),
            "news_score": stock.get("news_score", 0),
            "rating": stock.get("rating"),
            "reason": (
                f"AI score {stock.get('combined_score')} "
                f"med rating {stock.get('rating')}."
            )
        }

        candidate["confidence"] = calculate_confidence_score(
            candidate
        )

        candidates.append(candidate)

        if len(candidates) >= 3:
            break

    return candidates


def filter_ai_candidates(candidates):
    """
    Filtrerer AI kandidater baseret på minimum score.
    """

    filtered = []

    for candidate in candidates:

        score = candidate.get("score", 0)

        if score < 60:
            continue

        candidate["reason"] += (
            " Kandidaten opfylder AI minimumscore "
            "for nye investeringer."
        )

        filtered.append(candidate)

    return filtered


def calculate_confidence_score(candidate):
    """
    Beregner AI confidence baseret på score,
    nyheder og teknisk styrke.
    """

    score = candidate.get("score", 0)

    news_score = candidate.get(
        "news_score",
        0
    )

    technical_score = candidate.get(
        "technical_score",
        0
    )

    confidence = score

    if news_score >= 70:
        confidence += 5

    if technical_score >= 70:
        confidence += 5

    return round(confidence, 1)


def calculate_ai_weights(candidates):
    """
    Beregner vægte baseret på adjusted AI confidence.
    """

    if not candidates:
        return []

    total_confidence = sum(
        c.get("adjusted_confidence", c.get("confidence", 0))
        for c in candidates
    )

    weighted = []

    for candidate in candidates:

        confidence = candidate.get(
            "adjusted_confidence",
            candidate.get("confidence", 0)
        )

        weight = round(
            (confidence / total_confidence) * 100,
            1
        )

        weighted.append({
            "stock": candidate["stock"],
            "score": candidate.get("score"),
            "confidence": candidate.get("confidence", 0),
            "adjusted_confidence": confidence,
            "weight": weight,
            "reason": candidate.get("reason", "")
        })

    return weighted
def calculate_risk_adjustments(candidates):
    """
    Justerer AI kandidater baseret på eksisterende
    porteføljekoncentration.
    """

    portfolio = get_portfolio_summary()

    positions = portfolio.get("position_details", [])

    owned_weights = {}

    for position in positions:

        weight = float(
            str(position.get("weight_pct", "0"))
            .replace("%", "")
        )

        owned_weights[position["stock"]] = weight

    adjusted = []

    for candidate in candidates:

        stock = candidate["stock"]

        current_weight = owned_weights.get(stock, 0)

        adjustment = 0

        if current_weight >= 40:
            adjustment = -30
            reason = "Reduceret pga. høj eksisterende vægt."

        elif current_weight >= 20:
            adjustment = -15
            reason = "Let reduceret pga. eksisterende eksponering."

        else:
            reason = "Ingen væsentlig eksisterende eksponering."

        adjusted.append({
            **candidate,
            "risk_adjustment": adjustment,
            "risk_reason": reason
        })

    return adjusted

def apply_risk_adjustments(candidates):
    """
    Kombinerer AI confidence med porteføljerisiko.
    """

    adjusted = []

    for candidate in candidates:

        confidence = candidate.get(
            "confidence",
            0
        )

        adjustment = candidate.get(
            "risk_adjustment",
            0
        )

        adjusted_confidence = max(
            confidence + adjustment,
            0
        )

        adjusted.append({
            **candidate,
            "adjusted_confidence": adjusted_confidence
        })

    return adjusted

