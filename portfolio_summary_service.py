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

        position_details.append({
            "stock": p.get("stock"),
            "ticker": p.get("ticker"),
            "value": f'{p.get("value_dkk", 0):,.2f} DKK',
            "profit": f'{p.get("profit_dkk", 0):,.2f} DKK',
            "profit_pct": f'{profit_pct:.2f}%',
            "weight_pct": f'{p.get("weight_pct", 0):.2f}%',
            "score": score,
            "signal": decision["signal"],
            "stars": decision["stars"],
            "trend": decision["trend"],
            "confidence": decision["confidence"],
            "risk": decision["risk"],
            "comment": decision["comment"],
        })

    return {
        "value": f"{total_value:,.2f} DKK",
        "total_profit": f"{total_profit:,.2f} DKK",
        "total_return": f"{total_profit_pct:.2f}%",
        "positions": len(positions),
        "position_details": position_details,
    }