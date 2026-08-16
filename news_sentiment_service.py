import json

import feedparser

from openai_service import client
from openai_service import create_chat_completion
from ai_result_cache_service import get_cached_ai_result
from ai_result_cache_service import get_latest_cached_ai_result
from ai_result_cache_service import save_cached_ai_result


AI_NEWS_CACHE_CONTRACT_VERSION = "news_sentiment:v2"

AI_NEWS_EXACT_CACHE_MAX_AGE_SECONDS = 21600

AI_NEWS_NARRATIVE_REFRESH_SECONDS = 3600


NEWS_FEED_URL = (
    "https://news.google.com/rss/search?"
    "q=stock+market+OR+stocks+OR+earnings+OR+investing"
    "&hl=en-US&gl=US&ceid=US:en"
)


POSITIVE_WORDS = {
    "beats",
    "growth",
    "surges",
    "rises",
    "gain",
    "gains",
    "record",
    "upgrade",
    "strong",
    "optimism",
    "rebound",
    "profit",
}

NEGATIVE_WORDS = {
    "falls",
    "drops",
    "lawsuit",
    "warning",
    "cuts",
    "misses",
    "pressure",
    "competition",
    "decline",
    "risk",
    "probe",
    "investigation",
    "side effects",
    "downgrade",
    "loss",
    "losses",
}


def get_news_sentiment(limit=20):
    """
    Beregner en enkel nyhedssentiment-score fra 0 til 100.

    50 er neutral.
    Positive overskrifter løfter scoren.
    Negative overskrifter sænker scoren.
    """
    feed = feedparser.parse(NEWS_FEED_URL)
    entries = feed.entries[:limit]
    headlines = []
    articles = []

    positive = 0
    negative = 0
    neutral = 0

    for entry in entries:
        title_text = entry.get("title", "")
        summary_text = entry.get("summary", "")
        link = entry.get("link", "")
        published = entry.get("published", "")

        headlines.append(title_text)

        articles.append({
            "title": title_text,
            "summary": summary_text,
            "link": link,
            "published": published,
        })

        title = title_text.lower()

        has_positive = any(word in title for word in POSITIVE_WORDS)
        has_negative = any(word in title for word in NEGATIVE_WORDS)

        if has_positive and not has_negative:
            positive += 1
        elif has_negative and not has_positive:
            negative += 1
        else:
            neutral += 1

    checked_articles = len(entries)

    if checked_articles == 0:
        score = 50
    else:
        score = round(
            50
            + (positive * 5)
            - (negative * 5)
        )

        score = max(0, min(100, score))

    return {
        "score": score,
        "positive": positive,
        "neutral": neutral,
        "negative": negative,
        "checked_articles": checked_articles,
        "headlines": headlines,
        "articles": articles,
    }
    
def get_ai_news_sentiment(news=None):
    """
    AI-baseret analyse af de seneste nyhedsoverskrifter.

    Eksisterende nyhedsdata kan sendes ind, så RSS-feedet
    ikke behøver at blive hentet flere gange.
    """

    if client is None:
        return {
            "score": None,
            "status": "Unavailable",
            "summary": "OpenAI-klient ikke tilgængelig.",
        }

    if news is None:
        news = get_news_sentiment()

    headlines = "\n".join(news["headlines"])

    # Cache-identiteten ignorerer kun RSS-rækkefølgen.
    # Prompten nedenfor bevarer fortsat den oprindelige headline-rækkefølge.
    cache_input = {
        "headlines": sorted(news["headlines"]),
    }

    try:
        cached_result = get_cached_ai_result(
            service="news_sentiment",
            operation="market_news_sentiment",
            model="gpt-4.1-mini",
            prompt_contract_version=AI_NEWS_CACHE_CONTRACT_VERSION,
            input_payload=cache_input,
            max_age_seconds=AI_NEWS_EXACT_CACHE_MAX_AGE_SECONDS,
        )
    except Exception as e:
        print(
            "AI result cache read error:",
            e,
        )
        cached_result = None

    if cached_result is not None:
        return cached_result

    try:
        latest_result = get_latest_cached_ai_result(
            service="news_sentiment",
            operation="market_news_sentiment",
            model="gpt-4.1-mini",
            prompt_contract_version=AI_NEWS_CACHE_CONTRACT_VERSION,
            max_age_seconds=AI_NEWS_NARRATIVE_REFRESH_SECONDS,
        )
    except Exception as e:
        print(
            "AI latest result cache read error:",
            e,
        )
        latest_result = None

    if latest_result is not None:
        return latest_result

    response = create_chat_completion(
        service="news_sentiment",
        operation="market_news_sentiment",
        instrument=None,
        route="/update-dashboard-cache",
        model="gpt-4.1-mini",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "Du er en erfaren aktieanalytiker. "
                    "Vurder den samlede stemning i nyhederne."
                ),
            },
            {
                "role": "user",
                "content": f"""
Analyser disse nyhedsoverskrifter.

Svar KUN som gyldig JSON.

Format:

{{
    "score": 0,
    "status": "",
    "summary": ""
}}

Hvor:

- score er et helt tal mellem 0 og 100
- status er Positiv, Neutral eller Negativ
- summary er højst to sætninger.

Returnér KUN JSON.

Overskrifter:

{headlines}
""",
            },
        ],
    )

    content = response.choices[0].message.content

    if not content:
        return {
            "score": news.get("score", 50),
            "status": "Neutral",
            "summary": (
                "AI-nyhedsanalysen returnerede intet svar. "
                "Den regelbaserede nyhedsscore bruges midlertidigt."
            ),
        }

    try:
        ai_result = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return {
            "score": news.get("score", 50),
            "status": "Neutral",
            "summary": (
                "AI-nyhedsanalysen returnerede et ugyldigt svar. "
                "Den regelbaserede nyhedsscore bruges midlertidigt."
            ),
        }


    try:
        save_cached_ai_result(
            service="news_sentiment",
            operation="market_news_sentiment",
            model="gpt-4.1-mini",
            prompt_contract_version=AI_NEWS_CACHE_CONTRACT_VERSION,
            input_payload=cache_input,
            result=ai_result,
        )
    except Exception as e:
        print(
            "AI result cache write error:",
            e,
        )

    return ai_result
