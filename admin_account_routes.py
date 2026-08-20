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

    return {
        "accounts": accounts,
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
