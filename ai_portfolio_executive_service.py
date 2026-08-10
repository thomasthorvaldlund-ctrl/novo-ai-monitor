from ai_strategy_engine_service import get_ai_strategy
from ai_copilot_engine_service import get_ai_copilot
from ai_copilot_decision_service import get_copilot_decision
from ai_decision_intelligence_service import get_decision_intelligence


def get_ai_portfolio_executive(
    decision_intelligence=None
):

    strategy = get_ai_strategy()
    copilot = get_ai_copilot()
    decision = get_copilot_decision()

    intelligence = (
        decision_intelligence
        if decision_intelligence is not None
        else get_decision_intelligence()
    )

    return {
        "strategy": strategy.get("strategy"),
        "confidence": strategy.get("confidence"),
        "prediction_accuracy": strategy.get("prediction_accuracy"),

        "action": decision.get("action"),
        "priority": decision.get("priority"),
        "risk": decision.get("risk"),

        "summary": copilot.get("summary"),

        "market_status": intelligence.get("market_status"),
        "best_opportunity": intelligence.get("best_opportunity"),

        "reasons": intelligence.get("reasons", [])
    }