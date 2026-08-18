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
    g,
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


def _resolve_current_user_id_uncached():
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


def get_optional_current_user_id():
    """
    Returnerer det aktuelle kanoniske bruger-ID eller None.

    Resultatet gemmes i Flask request-contexten, så den
    centrale kontodatabase kun læses én gang per request.
    """

    if not has_request_context():
        return None

    cache_attribute = (
        "_aureum_current_user_id"
    )

    if hasattr(
        g,
        cache_attribute,
    ):
        return getattr(
            g,
            cache_attribute,
        )

    user_id = (
        _resolve_current_user_id_uncached()
    )

    setattr(
        g,
        cache_attribute,
        user_id,
    )

    return user_id

def require_current_user_id():
    """
    Returnerer bruger-ID eller afbryder med HTTP 401.
    """

    user_id = get_optional_current_user_id()

    if user_id is None:
        abort(401)

    return user_id
