from ai_portfolio_confidence_calibration_service import (
    get_confidence_calibration
)

from ai_portfolio_learning_analytics_service import (
    get_learning_analytics
)


def get_confidence_intelligence():

    calibration = get_confidence_calibration()

    learning = get_learning_analytics()


    reasons = []
    warnings = []


    best_signal = learning.get(
        "best_signal"
    )

    best_score = learning.get(
        "best_signal_score",
        0
    )


    if best_score >= 80:

        reasons.append(
            f"{best_signal} har stærk historisk performance "
            f"({best_score}%)."
        )

    else:

        warnings.append(
            "Historisk signalperformance er endnu begrænset."
        )


    decisions = calibration.get(
        "decisions",
        0
    )

    samples = calibration.get(
        "samples",
        0
    )


    if decisions >= 100:

        reasons.append(
            f"AI har {decisions} historiske beslutninger."
        )

    else:

        warnings.append(
            "AI har endnu begrænset beslutningshistorik."
        )


    if samples < 10:

        warnings.append(
            "Confidence calibration har få validerede samples."
        )


    overall = "Lav"


    if best_score >= 80 and decisions >= 100 and samples >= 10:

        overall = "Høj"

    elif best_score >= 60 and decisions >= 50:

        overall = "Middel"


    return {

        "overall_confidence":
            overall,

        "learning_strength":
            learning.get(
                "confidence",
                "Ukendt"
            ),

        "calibration_status":
            calibration.get(
                "status",
                "Ukendt"
            ),

        "decision_count":
            decisions,

        "sample_count":
            samples,

        "best_signal":
            best_signal,

        "best_signal_score":
            best_score,

        "reasons":
            reasons,

        "warnings":
            warnings
    }
