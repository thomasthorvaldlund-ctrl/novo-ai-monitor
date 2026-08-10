from ai_copilot_decision_service import get_copilot_decision
from ai_context_engine_service import get_ai_context
from ai_copilot_service import get_ai_copilot
from combined_score_service import combined_stock_score
from market_score_service import get_market_score
from market_intelligence_service import get_market_intelligence
from global_market_score_service import get_global_market_score
from top_picks_service import get_top_picks
from portfolio_summary_service import get_portfolio_summary
from portfolio_health_service import get_portfolio_health
from ai_alerts_service import (
    get_ai_alerts,
    get_active_ai_alert_count,
)
from performance_service import get_signal_statistics
from ai_explain_service import explain_stock
from openai_service import client


def get_decision_intelligence():
    """
    Samler Copilot beslutning og kontekst til en samlet AI vurdering.
    """

    decision = get_copilot_decision()
    context = get_ai_context()

    ranking = combined_stock_score(client).get(
        "combined_ranking",
        []
    )

    stock_explanations = [
        explain_stock(stock)
        for stock in ranking
    ]

    market_intelligence = get_market_intelligence()

    global_market_score = get_global_market_score(
        market_intelligence
    )

    market = get_market_score(ranking)
    portfolio = get_portfolio_summary()
    portfolio_health = get_portfolio_health(portfolio)
    top_picks = get_top_picks(ranking)
    alerts = get_ai_alerts()
    active_alert_count = get_active_ai_alert_count(alerts)

    copilot = get_ai_copilot(
        market=market,
        portfolio=portfolio,
        top_picks=top_picks,
        alerts=alerts,
        stock_explanations=stock_explanations,
        performance=get_signal_statistics(),
        market_intelligence=market_intelligence,
    )

    executive_action = decision["action"]
    executive_priority = decision["priority"]
    executive_risk = decision["risk"]
    executive_adjustments = []

    if executive_action == "BUY":
        if portfolio_health.get("level") in {"medium", "weak"}:
            executive_action = "HOLD"
            executive_priority = "Medium"
            executive_risk = "Moderat"
            executive_adjustments.append(
                "BUY nedjusteret fordi Portfolio Health ikke er stærk nok."
            )

        elif active_alert_count > 0:
            executive_action = "HOLD"
            executive_priority = "Medium"
            executive_risk = "Moderat"
            executive_adjustments.append(
                "BUY nedjusteret på grund af aktive AI-alerts."
            )

        elif context["confidence"] == "Low":
            executive_action = "HOLD"
            executive_priority = "Medium"
            executive_risk = "Moderat"
            executive_adjustments.append(
                "BUY nedjusteret fordi Context Confidence er lav."
            )

    selective_opportunity = None

    if top_picks:
        top_pick = top_picks[0]

        top_signal = top_pick.get("signal")
        top_score = top_pick.get("score", 0)
        top_confidence = top_pick.get("confidence", 0)
        top_risk = top_pick.get("risk")

        if (
            executive_action == "HOLD"
            and active_alert_count == 0
            and top_signal == "BUY"
            and top_score >= 70
            and top_confidence >= 80
            and top_risk == "Low"
        ):
            selective_opportunity = {
                "stock": top_pick.get("stock"),
                "signal": top_signal,
                "score": top_score,
                "confidence": top_confidence,
                "risk": top_risk,
                "message": (
                    f"{top_pick.get('stock')} er en selektiv købsmulighed, "
                    "selv om den samlede Executive Action fortsat er HOLD."
                ),
            }

    executive_reasons = []

    if context["confidence"] == "Low":
        executive_reasons.append(
            "Context Confidence er lav, fordi datagrundlaget stadig er begrænset."
        )

    if portfolio_health.get("level") in {"medium", "weak"}:
        executive_reasons.append(
            f"Portfolio Health er {portfolio_health.get('status', 'ikke optimal').lower()} "
            "og taler for en mere selektiv tilgang."
        )

    market_score_value = market.get("score", 50)

    if market_score_value < 50:
        executive_reasons.append(
            f"Market Score er {market_score_value}/100 og viser et svagt marked."
        )
    elif market_score_value < 70:
        executive_reasons.append(
            f"Market Score er {market_score_value}/100 og viser blandede signaler."
        )

    if selective_opportunity:
        executive_reasons.append(
            f"{selective_opportunity['stock']} er samtidig identificeret "
            "som en selektiv købsmulighed."
        )

    reasons = []

    reasons.append(
        f"AI handling: {executive_action}."
    )

    reasons.append(
        f"AI confidence: {context['confidence']}."
    )

    reasons.append(
        f"Learning status: {context['learning_status']}."
    )

    if context["learning_samples"] < 5:
        reasons.append(
            "Datagrundlaget er begrænset og kræver flere observationer."
        )

    reasons.append(
        f"Markedsvurdering: {copilot['market_status'].lstrip()}"
    )

    reasons.append(
        f"Global Market Score: "
        f"{global_market_score['score']}/100. "
        f"{global_market_score['status']}."
    )

    reasons.append(
        f"Global Market Confidence: "
        f"{global_market_score['confidence']}%."
    )

    reasons.append(
        f"AI anbefaling: {copilot['recommendation']}"
    )

    reasons.append(
        f"Bedste mulighed: {copilot['best_opportunity']}"
    )

    return {
        "headline": "AI Decision Intelligence",
        "action": executive_action,
        "priority": executive_priority,
        "risk": executive_risk,
        "confidence": copilot.get("confidence"),
        "decision_confidence": copilot.get("confidence"),
        "context_confidence": context["confidence"],
        "market_status": copilot["market_status"],
        "global_market_score": global_market_score,
        "recommendation": copilot["recommendation"],
        "best_opportunity": copilot["best_opportunity"],
        "learning_status": context["learning_status"],
        "learning_samples": context["learning_samples"],
        "market_score": market.get("score"),
        "low_ranked_stocks": market.get("low_ranked_stocks", 0),
        "portfolio_health_score": portfolio_health.get("score"),
        "portfolio_health_level": portfolio_health.get("level"),
        "active_alert_count": active_alert_count,
        "top_pick": top_picks[0] if top_picks else None,
        "selective_opportunity": selective_opportunity,
        "executive_reasons": executive_reasons,
        "executive_adjustments": executive_adjustments,
        "reasons": reasons + executive_adjustments,
    }
