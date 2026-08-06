import json
import feedparser
from urllib.parse import quote_plus

from stock_universe_service import get_active_stocks, get_news_query


CACHE_FILE = "/root/aureum-ai-platform/stock_news_ai_cache.json"


def build_stock_news_ai_cache(client):
    watchlist = {
        stock_name: get_news_query(stock_name)
        for stock_name in get_active_stocks()
    }

    results = []

    for stock_name, query in watchlist.items():
        try:
            feed = feedparser.parse(
                f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
            )

            titles = [entry.title for entry in feed.entries[:5]]
            text = "\n".join(titles)

            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Du er en forsigtig aktieanalytiker. "
                            "Giv ikke direkte køb/salg-råd. "
                            "Vurder kun nyhedssentiment og risiko."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"""
Analyser nyhedsoverskrifterne for {stock_name}.

Giv svar på dansk i dette format:

Nyhedsscore: 0-100
Sentiment: Meget positiv / Positiv / Neutral / Negativ / Meget negativ

Kort forklaring:
Maks 3 linjer.

Vigtigste positive signaler:
-
-

Vigtigste negative signaler:
-
-

Kortsigtet vurdering 1-3 måneder:
Bullish / Neutral / Bearish

Langsigtet vurdering 1-5 år:
Bullish / Neutral / Bearish

Risikofaktorer:
-
-

Mulige katalysatorer:
-
-

Samlet AI-vurdering:
Stærk kandidat / Kandidat / Neutral / Svag kandidat

Overskrifter:
{text}
""",
                    },
                ],
            )

            ai_text = response.choices[0].message.content

            score = 50
            for line in ai_text.splitlines():
                if "Nyhedsscore" in line:
                    digits = "".join(ch for ch in line if ch.isdigit())
                    if digits:
                        score = int(digits[:3])
                        score = max(0, min(score, 100))

            results.append(
                {
                    "stock": stock_name,
                    "news_score": score,
                    "ai_analysis": ai_text,
                    "headlines": titles,
                }
            )

        except Exception as exc:
            results.append(
                {
                    "stock": stock_name,
                    "error": str(exc),
                }
            )

    results = sorted(
        results,
        key=lambda item: item.get("news_score", 0),
        reverse=True,
    )

    output = {"news_ai_scores": results}

    with open(CACHE_FILE, "w", encoding="utf-8") as file:
        json.dump(output, file, ensure_ascii=False, indent=2)

    return output
