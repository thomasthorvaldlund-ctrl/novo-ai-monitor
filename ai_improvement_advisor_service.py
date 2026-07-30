from ai_learning_by_stock_service import get_learning_by_stock
from ai_signal_accuracy_service import get_signal_accuracy
from ai_confidence_calibration_service import get_confidence_calibration


def get_improvement_advisor():
    """
    Returnerer AI'ens vurdering af egne styrker og fokusområder.
    """

    strengths = []
    focus_areas = []

    # Signal Accuracy
    for signal in get_signal_accuracy():
        if signal["accuracy"] >= 80:
            strengths.append(
                f'{signal["signal"]}-signaler har høj historisk præcision ({signal["accuracy"]:.1f}%).'
            )
        elif signal["total"] >= 5:
            focus_areas.append(
                f'{signal["signal"]}-signaler har kun {signal["accuracy"]:.1f}% præcision.'
            )

    # Learning by Stock
    for stock in get_learning_by_stock():
        if stock["accuracy"] >= 80 and stock["total"] >= 3:
            strengths.append(
                f'{stock["stock"]} har været blandt de mest præcise aktier ({stock["accuracy"]:.1f}%).'
            )
        elif stock["total"] >= 3:
            focus_areas.append(
                f'{stock["stock"]} har lavere historisk præcision ({stock["accuracy"]:.1f}%).'
            )

    # Confidence Calibration
    calibration = get_confidence_calibration()

    for label, bucket in calibration.items():
        if bucket["accuracy_pct"] >= 80 and bucket["total"] > 0:
            strengths.append(
                f'Confidence-niveau "{label}" har høj præcision ({bucket["accuracy_pct"]:.1f}%).'
            )

    return {
        "strengths": strengths[:5],
        "focus_areas": focus_areas[:5],
        "overall_assessment": (
            "AI Learning Engine viser stabile resultater og identificerer løbende områder, "
            "hvor analysemodellen kan forbedres."
        ),
    }
