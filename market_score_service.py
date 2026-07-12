from news_sentiment_service import get_news_sentiment
from signal_history_service import get_latest_signals


def get_market_score(ranking=None):
    """
    Beregner en dynamisk Market Score ud fra:

    - 50 % gennemsnitlig Combined Score
    - 25 % aktuelle BUY/HOLD/WATCH/SELL-signaler
    - 15 % kritiske AI-alerts
    - 10 % nyhedssentiment

    Hvis ranking mangler, bruges en neutral fallback-score.
    """
    ranking = ranking or []

    if not ranking:
        return {
            "score": 50,
            "status": "Neutral",
            "color": "orange",
        }

    scores = [
        stock.get("combined_score")
        for stock in ranking
        if stock.get("combined_score") is not None
    ]

    if not scores:
        return {
            "score": 50,
            "status": "Neutral",
            "color": "orange",
        }

    combined_score = sum(scores) / len(scores)

    latest_signals = get_latest_signals()

    signal_values = {
        "BUY": 80,
        "HOLD": 60,
        "WATCH": 40,
        "SELL": 20,
    }

    current_signal_scores = [
        signal_values.get(row.get("signal"), 50)
        for row in latest_signals.values()
    ]

    if current_signal_scores:
        signal_score = (
            sum(current_signal_scores)
            / len(current_signal_scores)
        )
    else:
        signal_score = 50

    critical_alerts = sum(
        1
        for stock in ranking
        if stock.get("combined_score") is not None
        and stock.get("combined_score") < 45
    )

    alert_score = max(20, 50 - critical_alerts * 10)

    news_sentiment = get_news_sentiment()
    news_score = news_sentiment.get("score", 50)

    score = round(
        combined_score * 0.50
        + signal_score * 0.25
        + alert_score * 0.15
        + news_score * 0.10
    )

    if score >= 70:
        status = "Bullish"
        color = "green"
    elif score >= 50:
        status = "Neutral"
        color = "orange"
    else:
        status = "Bearish"
        color = "red"

    return {
        "score": score,
        "status": status,
        "color": color,
        "combined_component": round(combined_score, 1),
        "signal_component": round(signal_score, 1),
        "alert_component": round(alert_score, 1),
        "critical_alerts": critical_alerts,
        "news_component": round(news_score, 1),
        "news_positive": news_sentiment.get("positive", 0),
        "news_neutral": news_sentiment.get("neutral", 0),
        "news_negative": news_sentiment.get("negative", 0),
        "news_checked_articles": news_sentiment.get(
            "checked_articles",
            0,
        ),
    }