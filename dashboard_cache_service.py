import json
import os

CACHE_FILE = "dashboard_cache.json"


def load_dashboard_cache():
    if not os.path.exists(CACHE_FILE):
        return {}

    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_dashboard_cache(data):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, indent=2)