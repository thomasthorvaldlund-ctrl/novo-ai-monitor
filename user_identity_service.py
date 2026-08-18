"""
Central brugeridentitet for Aureum AI Platform.

HTTP Basic Auth valideres fortsat af applikationens globale
auth-gate. Denne kompatibilitetsbro oversætter derefter den
godkendte Basic Auth-identitet til platformens kanoniske
bruger-ID i den centrale kontodatabase.

Hvis kontodatabasen endnu ikke indeholder identiteten eller
midlertidigt ikke kan læses, bevares det nuværende Basic
Auth-brugernavn som sikker migrationsfallback.
"""

from __future__ import annotations

import sqlite3

from flask import (
    abort,
    has_request_context,
    request,
)

from user_account_service import (
    AccountStoreError,
    resolve_user_identity,
)


def _get_basic_auth_username():
    if not has_request_context():
        return None

    authorization = request.authorization

    if (
        authorization is None
        or not authorization.username
    ):
        return None

    username = str(
        authorization.username
    ).strip()

    return username or None


def get_optional_current_user_id():
    """
    Returnerer det aktuelle kanoniske bruger-ID eller None.

    Basic Auth-adgangskoden er allerede kontrolleret af
    applikationens globale before_request-gate.

    En aktiv konto returnerer sit kanoniske bruger-ID.
    En deaktiveret eller afventende konto returnerer None.
    Manglende eller utilgængelig kontodatabase falder tilbage
    til Basic Auth-brugernavnet under migrationen.
    """

    username = _get_basic_auth_username()

    if username is None:
        return None

    try:
        account = resolve_user_identity(
            "basic_auth",
            username,
        )

    except (
        AccountStoreError,
        OSError,
        sqlite3.Error,
    ):
        return username

    if account is None:
        return username

    status = str(
        account.get(
            "status",
            "",
        )
    ).strip().lower()

    if status != "active":
        return None

    user_id = str(
        account.get(
            "user_id",
            "",
        )
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
