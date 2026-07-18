import csv
import os
from datetime import datetime

from portfolio import get_portfolio_summary


HISTORY_FILE = "portfolio_history.csv"


def save_portfolio_history():
    portfolio = get_portfolio_summary()

    file_exists = os.path.exists(HISTORY_FILE)

    row = {
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_value": round(portfolio["total_value"], 2),
        "total_profit": round(portfolio["total_profit"], 2),
        "total_profit_pct": round(portfolio["total_profit_pct"], 2),
    }

    with open(HISTORY_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=row.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)

    return row

def load_portfolio_history():
    if not os.path.exists(HISTORY_FILE):
        return []

    with open(HISTORY_FILE, newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))