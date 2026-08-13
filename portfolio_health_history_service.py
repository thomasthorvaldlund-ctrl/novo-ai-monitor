"""
Aureum AI Portfolio Health History Service

Gemmer ét dagligt snapshot af Portfolio Health, så udviklingen
kan vises som en tidsserie uden at blande den sammen med
porteføljens økonomiske historik.
"""

import csv
import os
from datetime import date

from aureum_paths import data_path


HISTORY_FILE = data_path(
    "portfolio_health_history.csv"
)


def save_portfolio_health_snapshot(portfolio_health, portfolio_summary=None):
    """
    Gemmer dagens Portfolio Health én gang pr. dag.
    """

    health = portfolio_health or {}
    today = date.today().isoformat()

    rows = []

    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, newline="", encoding="utf-8") as file:
            rows = list(csv.DictReader(file))

    if any(row.get("date") == today for row in rows):
        return {
            "saved": False,
            "reason": "Dagens Portfolio Health er allerede gemt.",
        }

    risk = health.get("risk", {}) or {}
    diversification = health.get("diversification", {}) or {}
    momentum = health.get("momentum", {}) or {}
    confidence = health.get("confidence", {}) or {}

    positions = (
        portfolio_summary.get("position_details", [])
        if portfolio_summary
        else []
    )

    portfolio_snapshot = ",".join(
        position.get("stock", "-")
        for position in positions
        if position.get("stock")
    )

    position_count = len(positions)

    row = {
        "date": today,
        "score": round(float(health.get("score", 0)), 1),
        "status": health.get("status", "Ukendt"),
        "risk": risk.get("label", "Ukendt"),
        "risk_score": round(float(risk.get("score", 0)), 1),
        "diversification_score": round(
            float(diversification.get("score", 0)),
            1,
        ),
        "momentum_score": round(
            float(momentum.get("score", 0)),
            1,
        ),
        "confidence_score": round(
            float(confidence.get("score", 0)),
            1,
        ),
        "position_count": position_count,
        "portfolio_snapshot": portfolio_snapshot or "-",
        "best_position": health.get("best_position", "-"),
        "weakest_position": health.get("weakest_position", "-"),
    }

    file_exists = os.path.exists(HISTORY_FILE)

    with open(HISTORY_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=row.keys())

        if not file_exists or os.path.getsize(HISTORY_FILE) == 0:
            writer.writeheader()

        writer.writerow(row)

    return {
        "saved": True,
        **row,
    }


def load_portfolio_health_history():
    """
    Returnerer hele Portfolio Health-historikken med korrekte datatyper.
    """

    if not os.path.exists(HISTORY_FILE):
        return []

    with open(HISTORY_FILE, newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    history = []

    for row in rows:
        try:
            history.append({
                "date": row.get("date"),
                "score": float(row.get("score", 0)),
                "status": row.get("status", "Ukendt"),
                "risk": row.get("risk", "Ukendt"),
                "risk_score": float(row.get("risk_score", 0)),
                "diversification_score": float(
                    row.get("diversification_score", 0)
                ),
                "momentum_score": float(
                    row.get("momentum_score", 0)
                ),
                "confidence_score": float(
                    row.get("confidence_score", 0)
                ),
                "position_count": int(
                    row.get("position_count", 0)
                ),
                "portfolio_snapshot": row.get(
                    "portfolio_snapshot",
                    "-",
                ),
                "best_position": row.get("best_position", "-"),
                "weakest_position": row.get(
                    "weakest_position",
                    "-",
                ),
            })
        except (TypeError, ValueError):
            continue

    return history
