import json
from pathlib import Path

from aureum_paths import data_path

import math

from ai_portfolio_learning_analytics_service import (
    get_learning_analytics
)

from ai_confidence_intelligence_service import (
    get_confidence_intelligence
)

DECISION_FILE = data_path(
    "ai_portfolio_decisions.json"
)

def clean_number(value):
    if value is None:
        return 0

    try:
        if math.isnan(float(value)):
            return 0
    except:
        pass

    return value


def _resolve_portfolio_action(
    item,
    weight,
):
    portfolio_action = item.get(
        "portfolio_action"
    )
    portfolio_reason = item.get(
        "portfolio_reason",
        ""
    )

    if portfolio_action:
        return (
            portfolio_action,
            portfolio_reason,
        )

    if weight >= 60:
        return (
            "DIVERSIFY",
            "Positionen fylder for meget i porteføljen.",
        )

    return (
        "NONE",
        "",
    )


def load_latest_portfolio_decisions():

    if not DECISION_FILE.exists():
        return []

    with open(
        DECISION_FILE,
        encoding="utf-8"
    ) as f:
        history = json.load(f)

    if not history:
        return []

    return history[-1].get(
        "decisions",
        []
    )


def get_stock_decision_intelligence():

    decisions = load_latest_portfolio_decisions()

    learning = get_learning_analytics()

    confidence = get_confidence_intelligence()


    results = []


    best_signal = learning.get(
        "best_signal"
    )

    best_score = learning.get(
        "best_signal_score",
        0
    )

    for item in decisions:

        action = item.get(
            "action"
        )

        explanation = []

        signal_meaning = {
            "BUY": "AI identificerer en attraktiv mulighed.",
            "HOLD": "AI vurderer, at positionen bør fastholdes.",
            "WATCH": "AI anbefaler overvågning før ny beslutning.",
            "REDUCE": "AI anbefaler risikoreduktion."
        }
        

        explanation.append(
            signal_meaning.get(
                action,
                f"Aktuel AI beslutning: {action}."
            )
        )


        reason = item.get(
            "reason",
            ""
        ).rstrip(".")


        explanation.append(
            f"Begrundelse: {reason}."
        )

        signal_data = learning.get(
            "signal_performance",
            {}
        ).get(
            action,
            {}
        )

        signal_accuracy = signal_data.get(
            "accuracy",
            0
        )

        signal_type = {
            "BUY": "mulighedssignal",
            "HOLD": "positionsstyring",
            "WATCH": "overvågningssignal",
            "REDUCE": "risikostyring"
        }.get(
            action,
            "AI signal"
        )

        explanation.append(
            f"{action} er {signal_type} "
            f"med historisk præcision på {signal_accuracy}%."
        )

        score = item.get(
            "score",
            0
        )

        if score >= 70:
            score_text = "Høj AI-score understøtter positiv vurdering."
        elif score >= 50:
            score_text = "Mellem AI-score indikerer neutral vurdering."
        else:
            score_text = "Lav AI-score indikerer øget forsigtighed."

        explanation.append(
            score_text
        )

        clean_weight = clean_number(
            item.get("weight_pct")
        )

        explanation.append(
            f"Porteføljevægt: {clean_weight:.1f}%."
        )

        (
            portfolio_action,
            portfolio_reason,
        ) = _resolve_portfolio_action(
            item,
            clean_weight,
        )

        if portfolio_action == "DIVERSIFY":
            explanation.append(
                "Porteføljehandling: DIVERSIFY. "
                + (
                    portfolio_reason
                    or "Porteføljen bør diversificeres."
                )
            )

        results.append({

            "stock": item.get("stock"),

            "decision": action,

            "score": item.get("score"),

            "weight_pct": clean_weight,

            "reason": item.get("reason"),

            "portfolio_action":
                portfolio_action,

            "portfolio_reason":
                portfolio_reason,

            "profit_pct": item.get("profit_pct"),

            "confidence":
                confidence.get(
                    "overall_confidence"
                ),

            "learning_strength":
                confidence.get(
                    "learning_strength"
                ),

            "explanation":
                explanation

        })

    return results
