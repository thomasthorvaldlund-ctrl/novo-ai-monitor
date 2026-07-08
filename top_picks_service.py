def get_top_picks(ranking, limit=5):
    picks = []

    for stock in ranking[:limit]:
        score = stock["combined_score"]

        if score >= 80:
            stars = 5
            signal = "BUY"
            trend = "📈"
        elif score >= 70:
            stars = 4
            signal = "BUY"
            trend = "📈"
        elif score >= 60:
            stars = 3
            signal = "HOLD"
            trend = "➡️"
        elif score >= 50:
            stars = 2
            signal = "WATCH"
            trend = "➡️"
        else:
            stars = 1
            signal = "AVOID"
            trend = "📉"

        picks.append({
            "stock": stock["stock"],
            "score": score,
            "stars": "⭐" * stars,
            "signal": signal,
            "trend": trend,
        })

    return picks