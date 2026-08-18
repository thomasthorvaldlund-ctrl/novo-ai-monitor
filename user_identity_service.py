"""
Central brugeridentitet for Aureum AI Platform.

Servicen er en kompatibilitetsbro. Den nuværende
identitet kommer fortsat fra HTTP Basic Auth, men
forbrugende routes behøver ikke kende auth-metoden.
Et fremtidigt sessionslogin kan derfor implementeres
her uden at ændre Deep AI-, abonnements- eller
dataudbyderlagene.
"""

from __future__ import annotations

from flask import (
    abort,
    has_request_context,
    request,
)


def get_optional_current_user_id():
    """
    Returnerer det aktuelle bruger-ID eller None.

    Manglende request context og manglende Basic Auth
    behandles ens, så read-only servicekode også kan
    testes isoleret.
    """

    if not has_request_context():
        return None

    authorization = request.authorization

    if (
        authorization is None
        or not authorization.username
    ):
        return None

    user_id = str(
        authorization.username
    ).strip()

    return user_id or None


def require_current_user_id():
    """
    Returnerer bruger-ID eller afbryder med HTTP 401.
    """

    user_id = get_optional_current_user_id()

    if user_id is None:
        abort(401)

    return user_id
