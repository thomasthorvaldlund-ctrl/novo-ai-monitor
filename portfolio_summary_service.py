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


def _identity_key(value):
    return str(
        value or ""
    ).strip().upper()


def get_portfolio_summary(
    raw_portfolio=None,
    ranking=None,
):
    """
    Bygger AI-porteføljevurderingen.

    raw_portfolio og ranking kan leveres af en caller,
    så allerede hentede markeds- og cachedata genbruges.
    Eksisterende callers uden argumenter bevarer den
    tidligere live-adfærd.
    """
    if raw_portfolio is None:
        data = get_real_portfolio_summary()
    elif isinstance(
        raw_portfolio,
        dict,
    ):
        data = raw_portfolio
    else:
        data = {}

    total_value = data.get("total_value", 0)
    total_profit = data.get("total_profit", 0)
    total_profit_pct = data.get("total_profit_pct", 0)

    positions = data.get(
        "positions",
        [],
    )

    if not isinstance(
        positions,
        list,
    ):
        positions = []

    if ranking is None:
        combined = combined_stock_score(
            client
        )

        ranking = combined.get(
            "combined_ranking",
            [],
        )
    elif not isinstance(
        ranking,
        list,
    ):
        ranking = []

    stock_scores = {}
    ticker_scores = {}

    for item in ranking:
        if not isinstance(
            item,
            dict,
        ):
            continue

        score = item.get(
            "combined_score"
        )

        if score is None:
            continue

        stock_key = _identity_key(
            item.get("stock")
        )

        ticker_key = _identity_key(
            item.get("ticker")
        )

        if stock_key:
            stock_scores[
                stock_key
            ] = score

        if ticker_key:
            ticker_scores[
                ticker_key
            ] = score

    position_details = []
    
    for p in positions:
        profit_pct = p.get("profit_pct", 0)

        score = stock_scores.get(
            _identity_key(
                p.get("stock")
            )
        )

        if score is None:
            score = ticker_scores.get(
                _identity_key(
                    p.get("ticker")
                )
            )

        if score is None:
            score = portfolio_score(
                profit_pct
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

    risk_levels = {
        "Low": 1,
        "Medium": 2,
        "High": 3,
    }

    position_risk_levels = [
        risk_levels.get(
            p.get("risk"),
            2,
        )
        for p in position_details
    ]

    highest_risk_level = max(
        position_risk_levels,
        default=1,
    )

    if highest_risk_level >= 3:
        portfolio_risk = "High"
    elif highest_risk_level >= 2:
        portfolio_risk = "Medium"
    else:
        portfolio_risk = "Low"

    if best_position and weakest_position:

        signal = weakest_position.get("signal")

        if signal == "REDUCE":
            weakest_comment = "bør vurderes til reduktion"
        elif signal == "WATCH":
            weakest_comment = "bør overvåges tæt"
        elif signal == "HOLD":
            weakest_comment = "kan beholdes"
        elif signal == "BUY":
            weakest_comment = "viser et positivt signal"
        else:
            weakest_comment = "bør vurderes nærmere"

        portfolio_comment = (
            f"Porteføljen har en {portfolio_risk.lower()} risiko med en "
            f"samlet AI-score på {portfolio_score_value}. "
            f"{best_position.get('stock')} er stærkeste position med score "
            f"{best_position.get('score')}, mens "
            f"{weakest_position.get('stock')} {weakest_comment} "
            f"med score {weakest_position.get('score')}."
        )
    else:
        portfolio_comment = "Ingen tilstrækkelige data til AI-porteføljevurdering."

    increase = [
        p["stock"]
        for p in position_details
        if p["signal"] == "BUY"
    ]

    hold = [
        p["stock"]
        for p in position_details
        if p["signal"] == "HOLD"
    ]

    watch = [
        p["stock"]
        for p in position_details
        if p["signal"] == "WATCH"
    ]

    reduce = [
        p["stock"]
        for p in position_details
        if p["signal"] == "REDUCE"
    ]

    reduce_details = [
        p
        for p in position_details
        if p["signal"] == "REDUCE"
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
            "watch": watch,
            "reduce": reduce,
            "reduce_details": reduce_details,
            "diversification": diversification,
        },
    }