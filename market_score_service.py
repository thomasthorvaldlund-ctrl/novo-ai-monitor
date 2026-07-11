def get_market_score(ranking=None):
    """
    Beregner en dynamisk Market Score ud fra combined ranking.

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
        stock.get("combined_score", 0)
        for stock in ranking
        if stock.get("combined_score") is not None
    ]

    if not scores:
        return {
            "score": 50,
            "status": "Neutral",
            "color": "orange",
        }

    score = round(sum(scores) / len(scores))

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
    }