from ai_portfolio_analytics_service import get_portfolio_analytics


def get_learning_report():
    """
    Første version af AI Learning Engine.
    Bygger et simpelt læringsresumé ud fra Analytics.
    """

    analytics = get_portfolio_analytics()
    accuracy = analytics["accuracy_pct"]

    if accuracy >= 80:
        status = "Excellent"
        recommendation = "AI performs consistently well."
    elif accuracy >= 60:
        status = "Good"
        recommendation = "Continue monitoring current strategy."
    elif accuracy >= 40:
        status = "Needs Improvement"
        recommendation = "Review recent AI decisions for recurring mistakes."
    else:
        status = "Poor"
        recommendation = "Consider adjusting AI weighting and decision rules."

    return {
        "accuracy": accuracy,
        "status": status,
        "recommendation": recommendation,
        "analytics": analytics,
    }
