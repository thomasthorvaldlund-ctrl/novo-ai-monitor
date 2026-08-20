"""
Central rollebaseret adgangskontrol for Aureum AI Platform.

Identiteten kommer fra user_identity_service, mens roller
læses fra den centrale kontodatabase. Routes behøver derfor
ikke kende loginmetoden eller databasens detaljer.

Autorisation fejler lukket: en fejl i rollelagringen giver
aldrig adgang via fallback.
"""

from __future__ import annotations

import sqlite3

from flask import (
    abort,
    g,
    has_request_context,
)

from user_account_service import (
    AccountStoreError,
    VALID_ACCOUNT_ROLES,
    get_user_account_roles,
)

from user_identity_service import (
    get_optional_current_user_id,
    require_current_user_id,
)


_ROLE_CACHE_USER_KEY = (
    "_aureum_role_cache_user_id"
)

_ROLE_CACHE_VALUE_KEY = (
    "_aureum_role_cache_roles"
)


def _normalize_role(role):
    normalized_role = str(
        role
    ).strip().lower()

    if normalized_role not in VALID_ACCOUNT_ROLES:
        raise ValueError(
            f"Ukendt kontorolle: {normalized_role!r}."
        )

    return normalized_role


def _load_user_roles(user_id):
    try:
        roles = get_user_account_roles(
            user_id
        )

    except (
        AccountStoreError,
        OSError,
        sqlite3.Error,
    ):
        abort(
            503,
            description=(
                "Kontoadgang kan midlertidigt "
                "ikke kontrolleres."
            ),
        )

    return tuple(
        sorted({
            _normalize_role(role)
            for role in roles
        })
    )


def _get_roles_for_user(user_id):
    normalized_user_id = str(
        user_id
    ).strip()

    if not normalized_user_id:
        return ()

    if has_request_context():
        cached_user_id = getattr(
            g,
            _ROLE_CACHE_USER_KEY,
            None,
        )

        cached_roles = getattr(
            g,
            _ROLE_CACHE_VALUE_KEY,
            None,
        )

        if (
            cached_user_id == normalized_user_id
            and cached_roles is not None
        ):
            return cached_roles

    roles = _load_user_roles(
        normalized_user_id
    )

    if has_request_context():
        setattr(
            g,
            _ROLE_CACHE_USER_KEY,
            normalized_user_id,
        )

        setattr(
            g,
            _ROLE_CACHE_VALUE_KEY,
            roles,
        )

    return roles


def get_current_user_roles():
    """
    Returnerer den aktuelle brugers roller.

    Manglende request context eller identitet giver en tom
    tuple. Rollelagringsfejl giver HTTP 503.
    """

    user_id = (
        get_optional_current_user_id()
    )

    if user_id is None:
        return ()

    return _get_roles_for_user(
        user_id
    )


def current_user_has_role(role):
    """
    Returnerer True, hvis den aktuelle bruger har rollen.
    """

    normalized_role = _normalize_role(
        role
    )

    return (
        normalized_role
        in get_current_user_roles()
    )


def require_current_user_role(role):
    """
    Kræver identitet og den angivne rolle.

    Returnerer det kanoniske bruger-ID ved succes.
    """

    normalized_role = _normalize_role(
        role
    )

    user_id = require_current_user_id()

    if (
        normalized_role
        not in _get_roles_for_user(user_id)
    ):
        abort(
            403,
            description=(
                "Din konto har ikke adgang "
                "til denne funktion."
            ),
        )

    return user_id


def require_current_admin():
    """
    Kræver administratorrollen og returnerer bruger-ID.
    """

    return require_current_user_role(
        "admin"
    )
