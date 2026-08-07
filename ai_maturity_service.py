from ai_adaptive_summary_service import (
    get_adaptive_learning_summary
)

from ai_adaptive_explanation_service import (
    get_adaptive_explanation
)


def get_ai_maturity_score():
    """
    Beregner samlet AI maturity score.
    """

    adaptive = get_adaptive_learning_summary()
    explanation = get_adaptive_explanation()

    change_rate = adaptive.get(
        "change_rate",
        0
    )

    simulations = adaptive.get(
        "total_simulations",
        0
    )

    data_quality = adaptive.get(
        "data_quality",
        "No data"
    )

    confidence = explanation.get(
        "confidence",
        0
    )


    adaptation_score = min(
        change_rate,
        100
    )


    learning_score = min(
        simulations * 2,
        100
    )


    total_records = adaptive.get(
        "total_records",
        0
    )

    valid_records = adaptive.get(
        "valid_context_records",
        0
    )

    if total_records:
        quality_score = round(
            valid_records / total_records * 100
        )
    else:
        quality_score = 0


    maturity_score = round(
        (
            adaptation_score * 0.35
            +
            learning_score * 0.25
            +
            quality_score * 0.20
            +
            confidence * 0.20
        )
    )


    if maturity_score >= 80:
        level = "Advanced Learning Phase"
    elif maturity_score >= 60:
        level = "Developing Learning Phase"
    else:
        level = "Early Learning Phase"


    return {
        "score": maturity_score,
        "level": level,
        "components": {
            "adaptation": adaptation_score,
            "learning_activity": learning_score,
            "data_quality": quality_score,
            "explanation_confidence": confidence,
        }
    }
