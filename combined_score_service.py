from stock_screener_service import stock_screener
from stock_news_service import stock_news_ai_score


def combined_stock_score(client):
    tech_data = stock_screener()
    news_data = stock_news_ai_score(client)

    tech_map = {
        item["stock"]: item
        for item in tech_data.get("ranking", [])
    }

    news_map = {
        item["stock"]: item
        for item in news_data.get("news_ai_scores", [])
    }

    results = []

    for stock_name, tech_item in tech_map.items():
        news_item = news_map.get(stock_name, {})

        technical_score = tech_item.get("score", 0)
        news_score = news_item.get("news_score", 50)

        combined_score = round(
            (technical_score * 0.6) + (news_score * 0.4),
            2
        )

        if combined_score >= 75:
            rating = "Stærk kandidat"
        elif combined_score >= 60:
            rating = "Kandidat"
        elif combined_score >= 45:
            rating = "Neutral"
        else:
            rating = "Svag kandidat"

        results.append({
            "stock": stock_name,
            "price": tech_item.get("price"),
            "original_price": tech_item.get("original_price"),
            "currency": tech_item.get("currency"),
            "weekly_change": tech_item.get("weekly_change"),
            "technical_score": technical_score,
            "news_score": news_score,
            "combined_score": combined_score,
            "rating": rating,
            "ai_analysis": news_item.get("ai_analysis", "")
        })

    results.sort(
        key=lambda x: x.get("combined_score", 0),
        reverse=True
    )

    return {"combined_ranking": results}# Fælles funktioner til Combined Score
