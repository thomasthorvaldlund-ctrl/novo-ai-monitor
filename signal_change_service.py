from signal_history_service import save_signal
from telegram_notification_service import send_signal_notification


def process_signal(stock, score, signal, confidence, risk):
    """
    Gemmer signal og sender Telegram-besked hvis signalet ændrer sig.
    """

    result = save_signal(
        stock=stock,
        score=score,
        signal=signal,
        confidence=confidence,
        risk=risk,
    )

    if result.get("changed"):
        send_signal_notification(result)

    return result