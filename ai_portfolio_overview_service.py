from ai_learning_service import get_learning_report
from ai_learning_trends_service import get_learning_trends
from ai_confidence_calibration_service import get_confidence_calibration
from ai_performance_service import get_ai_performance


def get_ai_portfolio_overview():
    """
    Samlet vurdering af AI Portfolio Lab modenhed.
    """

    learning = get_learning_report()
    trends = get_learning_trends()
    calibration = get_confidence_calibration()
    performance = get_ai_performance()

    accuracy = learning.get("accuracy", 0)

    total_signals = performance.get(
        "evaluated_signals",
        0
    )

    # Accuracy score (40%)
    accuracy_points = min(
        accuracy * 0.4,
        40
    )

    # Historik score (30%)
    history_points = min(
        total_signals / 2,
        30
    )

    # Confidence calibration (20%)
    calibration_points = 0

    for row in calibration.values():
        if row["total"] > 0:
            calibration_points += row["accuracy_pct"] * 0.05

    calibration_points = min(
        calibration_points,
        20
    )

    # Learning trend (10%)
    if trends.get("trend") == "Forbedres":
        trend_points = 10
    elif trends.get("trend") == "Stabil":
        trend_points = 7
    else:
        trend_points = 3

    score = round(
        accuracy_points
        + history_points
        + calibration_points
        + trend_points
    )

    if score >= 80:
        status = "Avanceret"
    elif score >= 60:
        status = "Moden"
    elif score >= 40:
        status = "Under udvikling"
    else:
        status = "Tidlig fase"

    return {
        "score": score,
        "status": status,
        "accuracy": accuracy,
        "observations": total_signals,
        "learning_status": learning.get("status"),
        "trend": trends.get("trend"),
    }