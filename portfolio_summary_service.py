from combined_score_service import combined_stock_score
from openai_service import client
from ai_decision_service import get_ai_decision
from portfolio import get_portfolio_summary as get_real_portfolio_summary


def portfolio_score(profit_pct):
    if profit_pct >= 8:
        return 80
    elif profit_pct >= 5:
        return 70
    elif profit_pct >= 0:
        return 60
    elif profit_pct >= -5:
        return 50
    return 40


def get_portfolio_summary():
    data = get_real_portfolio_summary()

    total_value = data.get("total_value", 0)
    total_profit = data.get("total_profit", 0)
    total_profit_pct = data.get("total_profit_pct", 0)
    positions = data.get("positions", [])
    
    combined = combined_stock_score(client)

    score_lookup = {
    s["stock"]: s["combined_score"]
    for s in combined["combined_ranking"]
    }

    position_details = []
    
    for p in positions:
        profit_pct = p.get("profit_pct", 0)

        score = score_lookup.get(
            p.get("stock"),
            portfolio_score(profit_pct)   # fallback hvis aktien ikke findes
        )

        decision = get_ai_decision(score)

        target_weight = 100 / len(positions) if positions else 0
        weight_difference = round(target_weight - p.get("weight_pct", 0), 1)
        rebalance_amount = round(total_value * weight_difference / 100, 2)

        position_details.append({
            "stock": p.get("stock"),
            "ticker": p.get("ticker"),
            "value": f'{p.get("value_dkk", 0):,.2f} DKK',
            "profit": f'{p.get("profit_dkk", 0):,.2f} DKK',
            "profit_pct": f'{profit_pct:.2f}%',
            "weight_pct": f'{p.get("weight_pct", 0):.2f}%',
            "target_weight": f"{target_weight:.2f}%",
            "weight_difference": weight_difference,
            "rebalance_amount": rebalance_amount,
            "score": score,
            "signal": decision["signal"],
            "stars": decision["stars"],
            "trend": decision["trend"],
            "confidence": decision["confidence"],
            "risk": decision["risk"],
            "comment": decision["comment"],
        })

    portfolio_scores = [
        p["score"]
        for p in position_details
    ]

    portfolio_score_value = (
        round(sum(portfolio_scores) / len(portfolio_scores), 1)
        if portfolio_scores
        else 0
    )

    best_position = max(
        position_details,
        key=lambda x: x["score"],
        default={}
    )

    weakest_position = min(
        position_details,
        key=lambda x: x["score"],
        default={}
    )

    if portfolio_score_value >= 75:
        portfolio_risk = "Low"
    elif portfolio_score_value >= 60:
        portfolio_risk = "Medium"
    else:
        portfolio_risk = "High"

    if best_position and weakest_position:
        portfolio_comment = (
            f"Porteføljen har en {portfolio_risk.lower()} risiko med en "
            f"samlet AI-score på {portfolio_score_value}. "
            f"{best_position.get('stock')} er stærkeste position med score "
            f"{best_position.get('score')}, mens "
            f"{weakest_position.get('stock')} bør overvåges med score "
            f"{weakest_position.get('score')}."
        )
    else:
        portfolio_comment = "Ingen tilstrækkelige data til AI-porteføljevurdering."

    increase = [
        p["stock"]
        for p in position_details
        if p["score"] >= 70
    ]

    hold = [
        p["stock"]
        for p in position_details
        if 55 <= p["score"] < 70
    ]

    reduce = [
        p["stock"]
        for p in position_details
        if p["score"] < 55
    ]

    reduce_details = [
        p
        for p in position_details
        if p["score"] < 55
    ]

    high_weight_positions = [
        p["stock"]
        for p in position_details
        if float(p["weight_pct"].replace("%", "")) >= 30
    ]

    if high_weight_positions:
        diversification = (
            "Høj koncentration i: "
            + ", ".join(high_weight_positions)
            + ". Overvej bedre spredning."
        )
    else:
        diversification = "Porteføljen har en fornuftig vægtfordeling."

    return {
        "value": f"{total_value:,.2f} DKK",
        "total_profit": f"{total_profit:,.2f} DKK",
        "total_return": f"{total_profit_pct:.2f}%",
        "positions": len(positions),
        "position_details": position_details,

        "portfolio_score": portfolio_score_value,
        "portfolio_risk": portfolio_risk,
        "best_position": best_position.get("stock", ""),
        "best_position_score": best_position.get("score", 0),
        "weakest_position": weakest_position.get("stock", ""),
        "weakest_position_score": weakest_position.get("score", 0),
        "portfolio_comment": portfolio_comment,
        "recommendations": {
            "increase": increase,
            "hold": hold,
            "reduce": reduce,
            "reduce_details": reduce_details,
            "diversification": diversification,
        },
    }