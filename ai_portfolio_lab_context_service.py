from importlib import import_module


SERVICE_SPECS = {
    "learning_feedback": (
        "ai_learning_feedback_service",
        "get_learning_feedback",
    ),
    "decision_performance": (
        "ai_decision_performance_service",
        "get_decision_performance",
    ),
    "portfolio_decision_history": (
        "ai_portfolio_decision_service",
        "load_portfolio_decisions",
    ),
    "portfolio_changes": (
        "ai_portfolio_change_service",
        "get_portfolio_changes",
    ),
    "portfolio_performance": (
        "ai_portfolio_performance_service",
        "get_portfolio_performance",
    ),
    "portfolio_analytics": (
        "ai_portfolio_analytics_service",
        "get_portfolio_analytics",
    ),
    "learning_report": (
        "ai_learning_service",
        "get_learning_report",
    ),
    "learning_timeline": (
        "ai_learning_timeline_service",
        "get_learning_timeline",
    ),
    "confidence_calibration": (
        "ai_confidence_calibration_service",
        "get_confidence_calibration",
    ),
    "portfolio_confidence_calibration": (
        "ai_portfolio_confidence_calibration_service",
        "get_confidence_calibration",
    ),
    "learning_by_stock": (
        "ai_learning_by_stock_service",
        "get_learning_by_stock",
    ),
    "signal_accuracy": (
        "ai_signal_accuracy_service",
        "get_signal_accuracy",
    ),
    "improvement_advisor": (
        "ai_improvement_advisor_service",
        "get_improvement_advisor",
    ),
    "learning_trends": (
        "ai_learning_trends_service",
        "get_learning_trends",
    ),
    "ai_insight": (
        "ai_insight_generator_service",
        "get_ai_insight",
    ),
    "pattern_detection": (
        "ai_pattern_detector_service",
        "get_pattern_detection",
    ),
    "prediction_engine": (
        "ai_prediction_engine_service",
        "get_prediction_engine",
    ),
    "decision_optimizer": (
        "ai_decision_optimizer_service",
        "get_decision_optimizer",
    ),
    "ai_context": (
        "ai_context_engine_service",
        "get_ai_context",
    ),
    "ai_strategy": (
        "ai_strategy_engine_service",
        "get_ai_strategy",
    ),
    "ai_copilot": (
        "ai_copilot_engine_service",
        "get_ai_copilot",
    ),
    "copilot_decision": (
        "ai_copilot_decision_service",
        "get_copilot_decision",
    ),
    "decision_memory": (
        "ai_portfolio_decision_memory_service",
        "get_decision_memory",
    ),
    "memory_trends": (
        "ai_portfolio_memory_trend_service",
        "get_memory_trends",
    ),
    "memory_insights": (
        "ai_portfolio_memory_insight_service",
        "get_memory_insights",
    ),
    "memory_advisor": (
        "ai_portfolio_memory_advisor_service",
        "get_memory_advisor",
    ),
    "memory_learning": (
        "ai_portfolio_memory_learning_service",
        "get_memory_learning",
    ),
    "learning_evolution": (
        "ai_portfolio_learning_evolution_service",
        "get_learning_evolution",
    ),
    "learning_analytics": (
        "ai_portfolio_learning_analytics_service",
        "get_learning_analytics",
    ),
    "confidence_intelligence": (
        "ai_confidence_intelligence_service",
        "get_confidence_intelligence",
    ),
    "stock_decision_intelligence": (
        "ai_stock_decision_intelligence_service",
        "get_stock_decision_intelligence",
    ),
    "ai_data_quality": (
        "ai_data_quality_service",
        "get_ai_data_quality",
    ),
    "decision_evolution": (
        "ai_decision_evolution_service",
        "get_decision_evolution",
    ),
    "ai_portfolio_overview": (
        "ai_portfolio_overview_service",
        "get_ai_portfolio_overview",
    ),
}


def _call_service(key):
    module_name, function_name = (
        SERVICE_SPECS[key]
    )

    module = import_module(
        module_name
    )

    function = getattr(
        module,
        function_name,
    )

    return function()


def build_portfolio_lab_context(
    cached_values=None,
):
    """
    Bygger hele Portfolio Lab-contexten til cachejobbet.
    """
    cache = (
        cached_values
        if isinstance(
            cached_values,
            dict,
        )
        else {}
    )

    decision_intelligence = cache.get(
        "decision_intelligence",
        {},
    )

    if not isinstance(
        decision_intelligence,
        dict,
    ):
        decision_intelligence = {}

    learning_feedback = cache.get(
        "learning_feedback"
    )

    if not isinstance(
        learning_feedback,
        dict,
    ):
        learning_feedback = _call_service(
            "learning_feedback"
        )

    decision_performance = cache.get(
        "decision_performance"
    )

    if not isinstance(
        decision_performance,
        dict,
    ):
        decision_performance = (
            _call_service(
                "decision_performance"
            )
        )

    from ai_portfolio_executive_service import (
        get_ai_portfolio_executive,
    )
    from ai_portfolio_brain_service import (
        get_ai_portfolio_brain,
    )
    from ai_portfolio_brain_score_service import (
        get_brain_score,
    )
    from ai_portfolio_brain_score_explanation_service import (
        get_brain_score_explanation,
    )
    from ai_portfolio_memory_center_service import (
        get_memory_center,
    )
    from ai_portfolio_memory_intelligence_service import (
        get_memory_intelligence,
    )

    ai_portfolio_executive = (
        get_ai_portfolio_executive(
            decision_intelligence=(
                decision_intelligence
            )
        )
    )

    ai_portfolio_brain = (
        get_ai_portfolio_brain(
            portfolio_executive=(
                ai_portfolio_executive
            ),
            decision_intelligence=(
                decision_intelligence
            ),
        )
    )

    brain_score = get_brain_score(
        portfolio_brain=(
            ai_portfolio_brain
        )
    )

    brain_score_explanation = (
        get_brain_score_explanation(
            brain_score=brain_score
        )
    )

    memory_center = get_memory_center()

    memory_intelligence = (
        get_memory_intelligence(
            memory_center=memory_center
        )
    )

    context = {
        "portfolio_insights": cache.get(
            "portfolio_insights",
            [],
        ),
        "portfolio_recommendations": cache.get(
            "portfolio_recommendations",
            [],
        ),
        "rebalancing": cache.get(
            "rebalancing",
            {},
        ),
        "learning_feedback":
            learning_feedback,
        "decision_intelligence":
            decision_intelligence,
        "decision_performance":
            decision_performance,
        "ai_portfolio_executive":
            ai_portfolio_executive,
        "ai_portfolio_brain":
            ai_portfolio_brain,
        "brain_score":
            brain_score,
        "brain_score_explanation":
            brain_score_explanation,
        "memory_center":
            memory_center,
        "memory_intelligence":
            memory_intelligence,
    }

    for key in SERVICE_SPECS:
        if key in context:
            continue

        context[key] = _call_service(
            key
        )

    return context
