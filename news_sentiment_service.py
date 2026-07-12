import feedparser


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

    positive = 0
    negative = 0
    neutral = 0

    for entry in entries:
        title = entry.get("title", "").lower()

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
    }