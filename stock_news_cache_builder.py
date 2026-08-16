import json
import os
from aureum_paths import cache_path

import feedparser
from urllib.parse import quote_plus

from openai_service import create_chat_completion
from ai_result_cache_service import get_cached_ai_result
from ai_result_cache_service import save_cached_ai_result
from stock_universe_service import get_deep_ai_stocks, get_news_query


CACHE_FILE = cache_path(
    "stock_news_ai_cache.json"
)


STOCK_NEWS_CACHE_CONTRACT_VERSION = "stock_news:v1"


def build_stock_news_ai_cache(client):
    watchlist = {
        stock_name: get_news_query(stock_name)
        for stock_name in get_deep_ai_stocks()
    }

    results = []

    for stock_name, query in watchlist.items():
        try:
            feed = feedparser.parse(
                f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
            )

            titles = [entry.title for entry in feed.entries[:5]]
            text = "\n".join(titles)

            cache_input = {
                "stock": stock_name,
                "headlines": sorted(titles),
            }

            try:
                cached_result = get_cached_ai_result(
                    service="stock_news",
                    operation="news_sentiment",
                    model="gpt-4.1-mini",
                    prompt_contract_version=STOCK_NEWS_CACHE_CONTRACT_VERSION,
                    input_payload=cache_input,
                )
            except Exception as exc:
                print(
                    "Stock News exact cache read error:",
                    exc,
                )
                cached_result = None

            cached_score = None
            cached_analysis = None

            if isinstance(
                cached_result,
                dict,
            ):
                cached_score = cached_result.get(
                    "news_score"
                )
                cached_analysis = cached_result.get(
                    "ai_analysis"
                )

            valid_cached_score = (
                isinstance(
                    cached_score,
                    int,
                )
                and not isinstance(
                    cached_score,
                    bool,
                )
                and 0
                <= cached_score
                <= 100
            )

            valid_cached_analysis = (
                isinstance(
                    cached_analysis,
                    str,
                )
                and bool(
                    cached_analysis.strip()
                )
            )

            if (
                valid_cached_score
                and valid_cached_analysis
            ):
                results.append(
                    {
                        "stock": stock_name,
                        "news_score": cached_score,
                        "ai_analysis": cached_analysis,
                        "headlines": titles,
                    }
                )
                continue

            response = create_chat_completion(
                service="stock_news",
                operation="news_sentiment",
                instrument=stock_name,
                route="/update-stock-news-ai-cache",
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

            if ai_text.strip():
                try:
                    save_cached_ai_result(
                        service="stock_news",
                        operation="news_sentiment",
                        model="gpt-4.1-mini",
                        prompt_contract_version=STOCK_NEWS_CACHE_CONTRACT_VERSION,
                        input_payload=cache_input,
                        result={
                            "news_score": score,
                            "ai_analysis": ai_text,
                        },
                    )
                except Exception as exc:
                    print(
                        "Stock News result cache write error:",
                        exc,
                    )

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

    temp_file = CACHE_FILE.with_suffix(
        CACHE_FILE.suffix + ".tmp"
    )

    with open(
        temp_file,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            output,
            file,
            ensure_ascii=False,
            indent=2,
        )

        file.flush()
        os.fsync(file.fileno())

    temp_file.replace(
        CACHE_FILE
    )

    return output
