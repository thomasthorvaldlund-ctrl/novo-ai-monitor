def get_ai_alerts():
    """
    Midlertidig AI Alerts-service.
    Senere kobles den til news_score,
    AI-analyse og porteføljerisiko.
    """

    return [
        {
            "level": "green",
            "title": "Ingen kritiske AI-advarsler",
            "message": "Alle overvågede aktier ser stabile ud."
        }
    ]