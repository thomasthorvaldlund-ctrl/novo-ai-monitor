import json
import os
from aureum_paths import cache_path


CACHE_FILE = cache_path(
    "dashboard_cache.json"
)


def load_dashboard_cache():
    """
    Indlæser dashboard cache defensivt.
    """

    if not CACHE_FILE.exists():
        return {}

    try:
        with open(
            CACHE_FILE,
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        if isinstance(data, dict):
            return data

        return {}

    except (OSError, json.JSONDecodeError):
        return {}


def save_dashboard_cache(data):
    """
    Gemmer dashboard cache atomisk.

    Readers ser enten den gamle komplette cache
    eller den nye komplette cache.
    """

    temp_file = CACHE_FILE.with_suffix(
        CACHE_FILE.suffix + ".tmp"
    )

    with open(
        temp_file,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False,
        )

        f.flush()
        os.fsync(f.fileno())

    temp_file.replace(
        CACHE_FILE
    )
