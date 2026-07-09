import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = "8532274659"


def send_signal_notification(change):
    """
    Sender en Telegram-besked ved AI-signalændringer.
    """

    if not BOT_TOKEN or not CHAT_ID:
        return False

    message = (
        "🔔 AI Signal Update\n\n"
        f"{change['stock']}\n\n"
        f"{change.get('old_signal')} ➜ {change.get('new_signal')}\n\n"
        f"Score: {change.get('score')}\n"
        f"Confidence: {change.get('confidence')}%\n"
        f"Risk: {change.get('risk')}"
    )

    response = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": message,
        },
        timeout=10,
    )

    return response.status_code == 200