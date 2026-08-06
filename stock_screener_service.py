import json
from pathlib import Path


CACHE_FILE = Path("/root/aureum-ai-platform/stock_screener_cache.json")


def stock_screener():
    if not CACHE_FILE.exists():
        return {
            "ranking": [],
            "error": "Stock screener cache findes ikke",
        }

    try:
        with CACHE_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)

    except (OSError, json.JSONDecodeError) as e:
        return {
            "ranking": [],
            "error": f"Kunne ikke læse stock screener cache: {e}",
        }

    ranking = data.get("ranking", [])

    if not isinstance(ranking, list):
        return {
            "ranking": [],
            "error": "Stock screener cache har ugyldigt format",
        }

    return {
        "ranking": ranking,
    }
