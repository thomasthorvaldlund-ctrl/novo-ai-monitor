import json
from pathlib import Path

from ai_portfolio_learning_analytics_service import (
    get_learning_analytics
)

from ai_confidence_intelligence_service import (
    get_confidence_intelligence
)


DECISION_FILE = Path(
    "ai_portfolio_decisions.json"
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


        explanation.append(
            f"Porteføljevægt: "
            f"{item.get('weight_pct', 0):.1f}%."
        )


        results.append({

            "stock": item.get("stock"),

            "decision": action,

            "score": item.get("score"),

            "weight_pct": item.get(
                "weight_pct"
            ),

            "reason": item.get(
                "reason"
            ),

            "profit_pct": item.get(
                "profit_pct"
            ),

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
