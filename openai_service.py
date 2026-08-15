import os
from openai import OpenAI

from ai_usage_service import record_ai_usage

api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    client = OpenAI(api_key=api_key)
else:
    client = None


def create_chat_completion(
    *,
    service,
    model,
    messages,
    operation=None,
    instrument=None,
    route=None,
    **kwargs,
):
    """
    Central gateway for OpenAI Chat Completions.

    Alle fremtidige Chat Completions bør gå gennem
    denne funktion, så faktisk tokenforbrug kan måles.
    """
    if client is None:
        raise RuntimeError(
            "OpenAI-klient ikke tilgængelig."
        )

    response = (
        client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs,
        )
    )

    record_ai_usage(
        response,
        service=service,
        requested_model=model,
        operation=operation,
        instrument=instrument,
        route=route,
    )

    return response
