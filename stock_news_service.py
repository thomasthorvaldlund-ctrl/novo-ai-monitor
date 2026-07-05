import os
import time
import json
import feedparser
from urllib.parse import quote_plus


def stock_news_ai_score(client):
    cache_file = "/root/novo-ai-monitor/stock_news_ai_cache.json"
    cache_seconds = 21600

    if os.path.exists(cache_file) and time.time() - os.path.getmtime(cache_file) < cache_seconds:
        with open(cache_file, "r") as f:
            return json.load(f)

    return {"news_ai_scores": []}
