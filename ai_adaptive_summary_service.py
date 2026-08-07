from ai_adaptive_performance_service import (
    get_adaptive_performance
)

from ai_adaptive_analytics_service import (
    get_adaptive_regime_analysis
)

from ai_adaptive_signal_analytics_service import (
    get_adaptive_signal_analysis
)

from ai_adaptive_quality_service import (
    get_adaptive_data_quality
)


def get_adaptive_learning_summary():
    """
    Samler adaptive learning analyser.
    """

    performance = get_adaptive_performance()

    regime_analysis = get_adaptive_regime_analysis()

    signal_analysis = get_adaptive_signal_analysis()

    quality = get_adaptive_data_quality()


    total_changes = signal_analysis.get(
        "total_changes",
        0
    )


    signal_changes = signal_analysis.get(
        "signal_changes",
        {}
    )


    most_common_change = None

    if signal_changes:
        most_common_change = max(
            signal_changes,
            key=signal_changes.get
        )


    most_active_regime = None

    if regime_analysis:

        most_active_regime = max(
            regime_analysis,
            key=lambda x:
            regime_analysis[x]["simulations"]
        )


    summary = (
        "AI analyserer fortsat læringsdata."
    )


    if most_common_change:

        summary = (
            f"AI ændrer primært signaler "
            f"via {most_common_change}."
        )


    return {
        "total_simulations": performance.get(
            "total_simulations",
            0
        ),

        "changed_decisions": performance.get(
            "changed_decisions",
            0
        ),

        "change_rate": performance.get(
            "change_rate",
            0
        ),

        "most_common_signal_change": most_common_change,

        "most_active_regime": most_active_regime,

        "learning_status": performance.get(
            "status"
        ),

        "data_quality": quality.get(
            "data_quality"
        ),

        "missing_context_records": quality.get(
            "missing_context_records"
        ),

        "total_records": quality.get(
            "total_records"
        ),

        "valid_context_records": quality.get(
            "valid_context_records"
        ),

        "summary": summary,
    }
