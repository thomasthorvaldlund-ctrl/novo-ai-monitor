from datetime import datetime
from pathlib import Path

from signal_history_service import load_signal_history
from job_status_service import get_job_statuses


CACHE_FILE = Path("dashboard_cache.json")


def get_ai_engine_status():
    """
    Returnerer samlet status for AI Engine.
    """

    last_update = None

    if CACHE_FILE.exists():
        try:
            timestamp = CACHE_FILE.stat().st_mtime
            last_update = datetime.fromtimestamp(
                timestamp
            ).strftime("%d-%m-%Y %H:%M")
        except Exception:
            last_update = None

    try:
        signal_count = len(load_signal_history())
    except Exception:
        signal_count = 0

    return {
        "status": "online",
        "version": "v2.1",
        "last_update": last_update,
        "signal_count": signal_count,
        "jobs": get_job_statuses(),
        "modules": [
            "Market Score",
            "News AI",
            "Explain Engine",
            "Copilot",
        ],
    }
