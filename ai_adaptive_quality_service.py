from ai_adaptive_history_service import load_adaptive_history


def get_adaptive_data_quality():
    """
    Evaluerer kvaliteten af adaptive læringsdata.
    """

    history = load_adaptive_history()

    total_records = len(history)

    valid_context_records = sum(
        1
        for item in history
        if item.get("market_regime")
        and item.get("market_score") is not None
    )

    missing_context_records = (
        total_records
        -
        valid_context_records
    )

    if total_records == 0:
        quality = "No data"

    elif valid_context_records == total_records:
        quality = "Complete"

    else:
        quality = "Partial"


    return {
        "total_records": total_records,
        "valid_context_records": valid_context_records,
        "missing_context_records": missing_context_records,
        "data_quality": quality,
    }
