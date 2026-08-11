import os
import time
import json
from pathlib import Path
import feedparser
from urllib.parse import quote_plus


def stock_news_ai_score(client):
    cache_file = Path(
        "/root/aureum-ai-platform/stock_news_ai_cache.json"
    )
    cache_seconds = 21600

    if (
        cache_file.exists()
        and time.time() - cache_file.stat().st_mtime < cache_seconds
    ):
        try:
            with open(
                cache_file,
                "r",
                encoding="utf-8",
            ) as f:
                data = json.load(f)

            if isinstance(data, dict):
                return data

        except (OSError, json.JSONDecodeError):
            pass

    return {"news_ai_scores": []}
