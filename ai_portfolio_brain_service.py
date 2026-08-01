from ai_portfolio_executive_service import get_ai_portfolio_executive
from ai_context_engine_service import get_ai_context
from ai_strategy_engine_service import get_ai_strategy
from ai_prediction_engine_service import get_prediction_engine
from ai_decision_intelligence_service import get_decision_intelligence
from ai_decision_performance_service import get_decision_performance


def get_ai_portfolio_brain():
    """
    Samler alle AI Portfolio-moduler til én samlet vurdering.
    """

    executive = get_ai_portfolio_executive()
    context = get_ai_context()
    strategy = get_ai_strategy()
    prediction = get_prediction_engine()
    intelligence = get_decision_intelligence()
    performance = get_decision_performance()


    warnings = []

    if context.get("learning_status") == "For lidt data":
        warnings.append(
            "AI har endnu for få historiske observationer."
        )

    if prediction.get("reliability_status") == "For lidt data":
        warnings.append(
            "Prediction Engine har begrænset datagrundlag."
        )


    opportunities = []

    if intelligence.get("best_opportunity"):
        opportunities.append(
            intelligence["best_opportunity"]
        )


    return {
        "status": executive.get("strategy"),
        "action": executive.get("action"),
        "confidence": executive.get("confidence"),
        "risk": executive.get("risk"),

        "strategy": strategy.get("strategy"),

        "prediction_accuracy": prediction.get(
            "expected_accuracy"
        ),

        "decision_status": performance.get(
            "status"
        ),

        "main_reason": executive.get(
            "summary"
        ),

        "market_status": intelligence.get(
            "market_status"
        ),

        "warnings": warnings,

        "opportunities": opportunities,

        "learning_status": context.get(
            "learning_status"
        ),

        "learning_samples": context.get(
            "learning_samples"
        ),
    }