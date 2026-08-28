from signal_history_service import save_signal
from telegram_notification_service import send_signal_notification


def process_signal(
    stock,
    score,
    signal,
    confidence,
    risk,
):
    """
    Gemmer alle signalændringer, men sender
    kun Telegram for aktuelle positioner.
    """
    from portfolio_stock_service import (
        is_monitored_stock,
    )

    result = save_signal(
        stock=stock,
        score=score,
        signal=signal,
        confidence=confidence,
        risk=risk,
    )

    notification_eligible = (
        is_monitored_stock(
            stock=stock
        )
    )

    result = {
        **result,
        "notification_eligible": (
            notification_eligible
        ),
        "notification_sent": False,
    }

    if (
        result.get("changed")
        and notification_eligible
    ):
        result["notification_sent"] = bool(
            send_signal_notification(
                result
            )
        )

    return result
