"""
Administratorbeskyttet kontooversigt og sikker adgangsstyring.
"""

from __future__ import annotations

import sqlite3
from urllib.parse import urlsplit

from flask import (
    Blueprint,
    abort,
    redirect,
    render_template,
    request,
    url_for,
)

from werkzeug.exceptions import (
    ServiceUnavailable,
)

from user_account_service import (
    AccountAccessInvariantError,
    AccountNotFoundError,
    AccountStoreError,
    list_admin_account_audit,
    list_user_accounts,
    update_user_account_access,
)

from user_authorization_service import (
    current_user_has_role,
    require_current_admin,
)


admin_accounts_bp = Blueprint(
    "admin_accounts",
    __name__,
)


RESULT_MESSAGES = {
    "activated": (
        "Kontoen blev aktiveret."
    ),
    "disabled": (
        "Kontoen blev deaktiveret."
    ),
    "admin_granted": (
        "Administratorrollen blev tilføjet."
    ),
    "admin_revoked": (
        "Administratorrollen blev fjernet."
    ),
}


ERROR_MESSAGES = {
    "protected": (
        "Ændringen blev afvist af "
        "platformens sikkerhedsregler."
    ),
    "missing": (
        "Brugerkontoen findes ikke."
    ),
    "invalid": (
        "Den valgte handling er ugyldig."
    ),
}


@admin_accounts_bp.app_context_processor
def inject_admin_account_navigation():
    try:
        is_admin = current_user_has_role(
            "admin"
        )

    except ServiceUnavailable:
        is_admin = False

    return {
        "current_user_is_admin": is_admin,
    }


def _is_same_origin_post():
    source_url = (
        request.headers.get("Origin")
        or request.headers.get("Referer")
        or ""
    ).strip()

    if not source_url:
        return False

    parsed = urlsplit(
        source_url
    )

    return (
        parsed.scheme in {
            "http",
            "https",
        }
        and parsed.netloc.lower()
        == request.host.lower()
    )


AUDIT_ACTIONS = {
    "status_changed": {
        "icon": "🔄",
        "label": "Kontostatus ændret",
        "tone": "status",
    },
    "admin_granted": {
        "icon": "🔐",
        "label": "Administrator tildelt",
        "tone": "granted",
    },
    "admin_revoked": {
        "icon": "🔓",
        "label": "Administrator fjernet",
        "tone": "revoked",
    },
}


def _audit_value_label(
    action,
    value,
):
    if action == "status_changed":
        return {
            "active": "Aktiv",
            "disabled": "Deaktiveret",
            "pending": "Afventer",
        }.get(value, value)

    return {
        "true": "Administrator",
        "false": "Ingen administratorrolle",
    }.get(value, value)


def _format_audit_timestamp(value):
    normalized = str(value or "").strip()

    if not normalized:
        return "Tidspunkt ikke registreret"

    date_part, separator, time_part = (
        normalized.partition("T")
    )

    if not separator:
        return normalized

    date_items = date_part.split("-")

    if len(date_items) == 3:
        date_part = ".".join(
            reversed(date_items)
        )

    time_part = (
        time_part
        .replace("+00:00", "")
        .replace("Z", "")
    )

    return f"{date_part} kl. {time_part} UTC"


def _load_audit_events():
    try:
        events = list_admin_account_audit(
            limit=20
        )

    except (
        AccountStoreError,
        OSError,
        sqlite3.Error,
    ):
        abort(
            503,
            description=(
                "Revisionsloggen kan midlertidigt "
                "ikke indlæses."
            ),
        )

    formatted = []

    for event in events:
        presentation = AUDIT_ACTIONS.get(
            event.get("action"),
            {
                "icon": "📝",
                "label": "Kontoændring",
                "tone": "status",
            },
        )

        formatted.append({
            **event,
            **presentation,
            "previous_label": (
                _audit_value_label(
                    event.get("action"),
                    event.get("previous_value"),
                )
            ),
            "new_label": (
                _audit_value_label(
                    event.get("action"),
                    event.get("new_value"),
                )
            ),
            "display_time": (
                _format_audit_timestamp(
                    event.get("created_at")
                )
            ),
        })

    return formatted


def _load_accounts():
    try:
        return list_user_accounts()

    except (
        AccountStoreError,
        OSError,
        sqlite3.Error,
    ):
        abort(
            503,
            description=(
                "Kontoadministrationen kan "
                "midlertidigt ikke indlæses."
            ),
        )


def _build_summary(accounts):
    return {
        "account_count": len(accounts),
        "active_count": sum(
            1
            for account in accounts
            if account.get("status") == "active"
        ),
        "admin_count": sum(
            1
            for account in accounts
            if (
                "admin"
                in account.get("roles", [])
            )
        ),
    }


def _page_context(
    current_admin_id,
    *,
    result_code="",
    error_code="",
):
    accounts = _load_accounts()
    audit_events = _load_audit_events()

    return {
        "accounts": accounts,
        "audit_events": audit_events,
        "account_summary": (
            _build_summary(accounts)
        ),
        "current_admin_id": (
            current_admin_id
        ),
        "status_message": (
            RESULT_MESSAGES.get(
                result_code
            )
        ),
        "error_message": (
            ERROR_MESSAGES.get(
                error_code
            )
        ),
    }


@admin_accounts_bp.route(
    "/admin/accounts",
    methods=["GET"],
)
def admin_accounts_page():
    current_admin_id = (
        require_current_admin()
    )

    return render_template(
        "admin_accounts.html",
        **_page_context(
            current_admin_id,
            result_code=(
                request.args.get(
                    "result",
                    "",
                ).strip()
            ),
            error_code=(
                request.args.get(
                    "error",
                    "",
                ).strip()
            ),
        ),
    )


@admin_accounts_bp.route(
    "/admin/accounts/<user_id>/access",
    methods=["POST"],
)
def update_admin_account_access(
    user_id
):
    current_admin_id = (
        require_current_admin()
    )

    if not _is_same_origin_post():
        abort(400)

    action = request.form.get(
        "action",
        "",
    ).strip().lower()

    changes = {
        "activate": {
            "status": "active",
            "result": "activated",
        },
        "disable": {
            "status": "disabled",
            "result": "disabled",
        },
        "grant_admin": {
            "admin_enabled": True,
            "result": "admin_granted",
        },
        "revoke_admin": {
            "admin_enabled": False,
            "result": "admin_revoked",
        },
    }

    selected = changes.get(
        action
    )

    if selected is None:
        return redirect(
            url_for(
                "admin_accounts."
                "admin_accounts_page",
                error="invalid",
            )
        )

    try:
        update_user_account_access(
            user_id,
            actor_user_id=(
                current_admin_id
            ),
            status=selected.get(
                "status"
            ),
            admin_enabled=selected.get(
                "admin_enabled"
            ),
        )

    except AccountAccessInvariantError:
        return redirect(
            url_for(
                "admin_accounts."
                "admin_accounts_page",
                error="protected",
            )
        )

    except AccountNotFoundError:
        return redirect(
            url_for(
                "admin_accounts."
                "admin_accounts_page",
                error="missing",
            )
        )

    except ValueError:
        return redirect(
            url_for(
                "admin_accounts."
                "admin_accounts_page",
                error="invalid",
            )
        )

    except (
        AccountStoreError,
        OSError,
        sqlite3.Error,
    ):
        abort(
            503,
            description=(
                "Kontoændringen kunne "
                "midlertidigt ikke gemmes."
            ),
        )

    return redirect(
        url_for(
            "admin_accounts."
            "admin_accounts_page",
            result=selected["result"],
        )
    )
