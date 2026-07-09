from signal_history_service import save_signal


def process_signal(stock, score, signal, confidence, risk):
    """
    Gemmer signal og returnerer information om ændringen.
    """

    result = save_signal(
        stock=stock,
        score=score,
        signal=signal,
        confidence=confidence,
        risk=risk,
    )

    return result