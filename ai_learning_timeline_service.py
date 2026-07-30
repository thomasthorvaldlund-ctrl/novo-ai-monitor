from ai_portfolio_analytics_service import get_portfolio_analytics


def get_learning_timeline():
    """
    Midlertidig Learning Timeline.
    Senere udvides den med historiske data og grafer.
    """

    analytics = get_portfolio_analytics()
    accuracy = analytics["accuracy_pct"]

    return {
        "last_7_days": accuracy,
        "last_30_days": accuracy,
        "last_90_days": accuracy,
        "trend": "Stable",
    }
