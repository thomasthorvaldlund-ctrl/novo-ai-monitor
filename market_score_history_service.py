import csv
import os
from datetime import date


HISTORY_FILE = "market_score_history.csv"


def save_market_score(score, status):
    """
    Gemmer dagens Market Score én gang pr. dag.
    """
    today = date.today().isoformat()

    rows = []

    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

    if any(row.get("date") == today for row in rows):
        return {
            "saved": False,
            "reason": "Dagens Market Score er allerede gemt.",
        }

    file_exists = os.path.exists(HISTORY_FILE)

    with open(HISTORY_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists or os.path.getsize(HISTORY_FILE) == 0:
            writer.writerow([
                "date",
                "score",
                "status",
            ])

        writer.writerow([
            today,
            score,
            status,
        ])

    return {
        "saved": True,
        "date": today,
        "score": score,
        "status": status,
    }
    
def load_market_score_history():
    """
    Returnerer hele Market Score-historikken.
    """
    if not os.path.exists(HISTORY_FILE):
        return []

    with open(HISTORY_FILE, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    return [
        {
            "date": row.get("date"),
            "score": int(float(row.get("score", 0))),
            "status": row.get("status", "Ukendt"),
        }
        for row in rows
    ]