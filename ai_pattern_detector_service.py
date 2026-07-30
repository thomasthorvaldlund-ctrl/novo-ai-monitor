from ai_learning_by_stock_service import get_learning_by_stock
from ai_signal_accuracy_service import get_signal_accuracy


def get_pattern_detection():
    """
    Finder simple mønstre i AI'ens historiske læring.
    """

    patterns = []

    # Signalmønstre
    for signal in get_signal_accuracy():
        if signal["total"] >= 3:
            if signal["accuracy"] >= 80:
                patterns.append(
                    f'{signal["signal"]}-signaler viser stabil høj præcision ({signal["accuracy"]:.1f}%).'
                )
            elif signal["accuracy"] < 60:
                patterns.append(
                    f'{signal["signal"]}-signaler har lav historisk præcision ({signal["accuracy"]:.1f}%).'
                )

    # Aktiemønstre
    for stock in get_learning_by_stock():
        if stock["total"] >= 3:
            if stock["accuracy"] >= 80:
                patterns.append(
                    f'{stock["stock"]} har været blandt de mest stabile aktier ({stock["accuracy"]:.1f}%).'
                )
            elif stock["accuracy"] < 60:
                patterns.append(
                    f'{stock["stock"]} viser større variation i AI-præcisionen ({stock["accuracy"]:.1f}%).'
                )

    if not patterns:
        patterns.append(
            "Der er endnu for få historiske beslutninger til at identificere stabile mønstre."
        )

    return {
        "headline": "AI Pattern Detection",
        "patterns": patterns[:8],
    }
