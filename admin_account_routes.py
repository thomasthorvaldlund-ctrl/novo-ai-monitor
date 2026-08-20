"""
Skrivebeskyttet, administratorbeskyttet kontooversigt.
"""

from __future__ import annotations

import sqlite3

from flask import (
    Blueprint,
    abort,
    render_template,
)

from werkzeug.exceptions import (
    ServiceUnavailable,
)

from user_account_service import (
    AccountStoreError,
    list_user_accounts,
)

from user_authorization_service import (
    current_user_has_role,
    require_current_admin,
)


admin_accounts_bp = Blueprint(
    "admin_accounts",
    __name__,
)


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


@admin_accounts_bp.route(
    "/admin/accounts",
    methods=["GET"],
)
def admin_accounts_page():
    current_admin_id = (
        require_current_admin()
    )

    accounts = _load_accounts()

    return render_template(
        "admin_accounts.html",
        accounts=accounts,
        account_summary=(
            _build_summary(accounts)
        ),
        current_admin_id=current_admin_id,
    )
