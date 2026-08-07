from ai_copilot_decision_service import get_copilot_decision
from ai_context_engine_service import get_ai_context
from ai_copilot_service import get_ai_copilot
from combined_score_service import combined_stock_score
from market_score_service import get_market_score
from market_intelligence_service import get_market_intelligence
from global_market_score_service import get_global_market_score
from top_picks_service import get_top_picks
from portfolio_summary_service import get_portfolio_summary
from ai_alerts_service import get_ai_alerts
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

    copilot = get_ai_copilot(
        market=get_market_score(ranking),
        portfolio=get_portfolio_summary(),
        top_picks=get_top_picks(ranking),
        alerts=get_ai_alerts(),
        stock_explanations=stock_explanations,
        performance=get_signal_statistics(),
        market_intelligence=market_intelligence,
    )

    reasons = []

    reasons.append(
        f"AI handling: {decision['action']}."
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
        f"AI anbefaling: {copilot['recommendation']}"
    )

    reasons.append(
        f"Bedste mulighed: {copilot['best_opportunity']}"
    )

    return {
        "headline": "AI Decision Intelligence",
        "action": decision["action"],
        "priority": decision["priority"],
        "risk": decision["risk"],
        "confidence": context["confidence"],
        "market_status": copilot["market_status"],
        "global_market_score": global_market_score,
        "recommendation": copilot["recommendation"],
        "best_opportunity": copilot["best_opportunity"],
        "learning_status": context["learning_status"],
        "learning_samples": context["learning_samples"],
        "reasons": reasons,
    }
