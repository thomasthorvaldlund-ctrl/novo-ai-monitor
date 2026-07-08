import os
from datetime import datetime

JOBS = [
    ("Risk Check", "last_check.log"),
    ("News Check", "last_news_check.log"),
    ("AI News Check", "last_ai_news_check.log"),
    ("Status Report", "last_status_report.log"),
    ("Daily Report", "daily_report.log"),
    ("Smart Alerts", "last_smart_alerts.log"),
    ("DSV AI News", "dsv_ai_cron.log"),
    ("Save History", "history_save.log"),
    ("Portfolio Alerts", "portfolio_alerts.log"),
    ("Combined Score", "combined_score.log"),
    ("Combined Report", "combined_report.log"),
    ("Dashboard Cache", "dashboard_cache.log"),
]


def get_job_statuses():
    statuses = []

    for name, log_file in JOBS:
        path = os.path.join("/root/novo-ai-monitor", log_file)

        if os.path.exists(path):
            modified = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%d-%m-%Y %H:%M")
            size = os.path.getsize(path)
            status = "OK" if size >= 0 else "Unknown"
        else:
            modified = "Aldrig"
            size = 0
            status = "Mangler"

        statuses.append({
            "name": name,
            "log_file": log_file,
            "last_run": modified,
            "size": size,
            "status": status,
        })

    return statuses