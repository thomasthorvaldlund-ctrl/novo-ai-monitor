"""
Sikkert privat sessionslogin til Aureum AI Platform.

Den eksisterende Basic Auth-kontrol bevares som
migrations- og rollbackfallback. Sessionslogin er kun
aktivt, når AUREUM_SESSION_SECRET er konfigureret.
"""

from __future__ import annotations

import hmac
import os
import secrets
import sqlite3
import threading
import time
from datetime import timedelta
from urllib.parse import urlsplit

from flask import (
    Blueprint,
    Response,
    current_app,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from user_account_service import (
    AccountStoreError,
    get_user_account,
    initialize_account_store,
    resolve_user_identity,
)

from totp_mfa_service import (
    MfaConfigurationError,
    MfaError,
    MfaStateError,
    confirm_totp_setup,
    disable_totp,
    get_totp_setup_details,
    get_totp_status,
    is_totp_enabled,
    regenerate_recovery_codes,
    start_totp_setup,
    verify_mfa_code,
)


SESSION_SECRET_ENVIRONMENT_VARIABLE = (
    "AUREUM_SESSION_SECRET"
)

SESSION_USER_KEY = (
    "_aureum_private_user_id"
)
SESSION_AUTHENTICATED_AT_KEY = (
    "_aureum_private_authenticated_at"
)
SESSION_CSRF_KEY = (
    "_aureum_private_csrf"
)
SESSION_PENDING_MFA_USER_KEY = (
    "_aureum_pending_mfa_user_id"
)
SESSION_PENDING_MFA_AT_KEY = (
    "_aureum_pending_mfa_started_at"
)
SESSION_PENDING_MFA_NEXT_KEY = (
    "_aureum_pending_mfa_next"
)
REQUEST_USER_CACHE_ATTRIBUTE = (
    "_aureum_current_user_id"
)

SESSION_MAX_AGE_SECONDS = 12 * 60 * 60
LOGIN_FAILURE_WINDOW_SECONDS = 15 * 60
LOGIN_LOCKOUT_SECONDS = 15 * 60
LOGIN_MAX_FAILURES = 5
MFA_PENDING_MAX_AGE_SECONDS = 5 * 60

PRIVATE_LOGIN_PATHS = frozenset({
    "/login",
    "/login/two-factor",
    "/logout",
    "/robots.txt",
})

private_login_bp = Blueprint(
    "private_login",
    __name__,
)

_login_attempts = {}
_login_attempts_lock = threading.Lock()


def _private_login_enabled_for_app(app):
    return bool(
        app.extensions.get(
            "aureum_private_login_enabled",
            False,
        )
    )


def private_login_enabled():
    return _private_login_enabled_for_app(
        current_app
    )


def is_private_login_path():
    return request.path in PRIVATE_LOGIN_PATHS


def _safe_next_url(value):
    if value is None:
        return None

    normalized = str(value).strip()

    if not normalized:
        return None

    if any(
        ord(character) < 32
        for character in normalized
    ):
        return None

    if "\\" in normalized:
        return None

    parsed = urlsplit(normalized)

    if parsed.scheme or parsed.netloc:
        return None

    if (
        not normalized.startswith("/")
        or normalized.startswith("//")
    ):
        return None

    if parsed.path in PRIVATE_LOGIN_PATHS:
        return None

    return normalized


def _csrf_token():
    token = session.get(
        SESSION_CSRF_KEY
    )

    if (
        not isinstance(token, str)
        or len(token) < 32
    ):
        token = secrets.token_urlsafe(32)
        session[SESSION_CSRF_KEY] = token

    return token


def _valid_csrf_token(value):
    expected = session.get(
        SESSION_CSRF_KEY,
        "",
    )
    supplied = str(value or "")

    return bool(
        expected
        and supplied
        and hmac.compare_digest(
            str(expected),
            supplied,
        )
    )


def _login_attempt_key(username):
    client_address = str(
        request.remote_addr
        or "unknown"
    ).strip()

    return (
        client_address,
        str(username or "")
        .strip()
        .casefold(),
    )


def _rate_limited(key):
    now = time.monotonic()

    with _login_attempts_lock:
        record = _login_attempts.get(key)

        if record is None:
            return False

        blocked_until = float(
            record.get(
                "blocked_until",
                0,
            )
        )

        if blocked_until > now:
            return True

        failures = [
            timestamp
            for timestamp
            in record.get(
                "failures",
                [],
            )
            if (
                now - timestamp
                <= LOGIN_FAILURE_WINDOW_SECONDS
            )
        ]

        if failures:
            record["failures"] = failures
            record["blocked_until"] = 0
        else:
            _login_attempts.pop(
                key,
                None,
            )

        return False


def _record_login_failure(key):
    now = time.monotonic()

    with _login_attempts_lock:
        record = _login_attempts.setdefault(
            key,
            {
                "failures": [],
                "blocked_until": 0,
            },
        )

        failures = [
            timestamp
            for timestamp
            in record.get(
                "failures",
                [],
            )
            if (
                now - timestamp
                <= LOGIN_FAILURE_WINDOW_SECONDS
            )
        ]

        failures.append(now)
        record["failures"] = failures

        if len(failures) >= LOGIN_MAX_FAILURES:
            record["blocked_until"] = (
                now + LOGIN_LOCKOUT_SECONDS
            )


def _record_login_success(key):
    with _login_attempts_lock:
        _login_attempts.pop(
            key,
            None,
        )


def _mfa_database_path():
    return current_app.config.get(
        "AUREUM_ACCOUNT_DATABASE"
    )


def basic_auth_allowed_for_user(user_id):
    try:
        return not is_totp_enabled(
            user_id,
            path=_mfa_database_path(),
        )
    except (
        MfaError,
        AccountStoreError,
        OSError,
        sqlite3.Error,
    ):
        current_app.logger.exception(
            "Basic Auth MFA-status kunne ikke kontrolleres."
        )
        return False


def _complete_private_login(user_id):
    session.clear()
    session.permanent = True
    session[SESSION_USER_KEY] = user_id
    session[SESSION_AUTHENTICATED_AT_KEY] = int(
        time.time()
    )
    _csrf_token()


def _begin_pending_mfa(user_id, next_url):
    session.clear()
    session.permanent = False
    session[SESSION_PENDING_MFA_USER_KEY] = user_id
    session[SESSION_PENDING_MFA_AT_KEY] = int(time.time())
    session[SESSION_PENDING_MFA_NEXT_KEY] = (
        _safe_next_url(next_url) or ""
    )
    _csrf_token()


def _pending_mfa_user_id():
    user_id = session.get(
        SESSION_PENDING_MFA_USER_KEY
    )
    started_at = session.get(
        SESSION_PENDING_MFA_AT_KEY
    )

    try:
        started_at = int(started_at)
    except (TypeError, ValueError):
        return None

    if (
        not isinstance(user_id, str)
        or not user_id.strip()
        or int(time.time()) - started_at
        > MFA_PENDING_MAX_AGE_SECONDS
    ):
        session.clear()
        return None

    return user_id.strip().lower()


def _render_two_factor_challenge(
    *,
    error_message=None,
    status_code=200,
):
    return (
        render_template(
            "private_two_factor.html",
            csrf_token=_csrf_token(),
            error_message=error_message,
        ),
        status_code,
    )


def _current_password_valid(user_id, password):
    account = get_user_account(
        user_id,
        path=_mfa_database_path(),
    )

    if account is None:
        return False

    username = str(
        account.get("username", "")
    ).strip().lower()
    credential_checker = current_app.extensions.get(
        "aureum_private_credential_checker"
    )

    return bool(
        username
        and password
        and credential_checker
        and credential_checker(username, password)
    )


def _render_two_factor_settings(
    user_id,
    *,
    error_message=None,
    success_message=None,
    recovery_codes=None,
    status_code=200,
):
    database_path = _mfa_database_path()
    mfa_status = get_totp_status(
        user_id,
        path=database_path,
    )
    setup_details = None

    if mfa_status["pending"]:
        setup_details = get_totp_setup_details(
            user_id,
            path=database_path,
        )

    return (
        render_template(
            "security_two_factor.html",
            mfa_status=mfa_status,
            setup_details=setup_details,
            csrf_token=_csrf_token(),
            error_message=error_message,
            success_message=success_message,
            recovery_codes=recovery_codes,
        ),
        status_code,
    )


def _render_login(
    *,
    error_message=None,
    status_code=200,
    next_url=None,
):
    return (
        render_template(
            "private_login.html",
            csrf_token=_csrf_token(),
            error_message=error_message,
            logged_out=(
                request.args.get(
                    "logged_out"
                )
                == "1"
            ),
            next_url=(
                _safe_next_url(next_url)
                or ""
            ),
        ),
        status_code,
    )


def get_authenticated_session_user_id():
    if not private_login_enabled():
        return None

    user_id = session.get(
        SESSION_USER_KEY
    )

    if not isinstance(user_id, str):
        return None

    user_id = user_id.strip().lower()

    if not user_id:
        return None

    authenticated_at = session.get(
        SESSION_AUTHENTICATED_AT_KEY
    )

    try:
        authenticated_at = int(
            authenticated_at
        )
    except (
        TypeError,
        ValueError,
    ):
        session.clear()
        return None

    if (
        int(time.time())
        - authenticated_at
        > SESSION_MAX_AGE_SECONDS
    ):
        session.clear()
        return None

    if hasattr(
        g,
        REQUEST_USER_CACHE_ATTRIBUTE,
    ):
        cached_user_id = getattr(
            g,
            REQUEST_USER_CACHE_ATTRIBUTE,
        )

        if cached_user_id == user_id:
            return user_id

    try:
        account = get_user_account(
            user_id
        )

    except (
        AccountStoreError,
        OSError,
        sqlite3.Error,
    ):
        return None

    if account is None:
        session.clear()
        return None

    status = str(
        account.get(
            "status",
            "",
        )
    ).strip().lower()

    if status != "active":
        session.clear()
        return None

    canonical_user_id = str(
        account.get(
            "user_id",
            "",
        )
    ).strip().lower()

    if canonical_user_id != user_id:
        session.clear()
        return None

    setattr(
        g,
        REQUEST_USER_CACHE_ATTRIBUTE,
        user_id,
    )

    return user_id


def _browser_html_request():
    accept_header = request.headers.get(
        "Accept",
        "",
    ).lower()

    return "text/html" in accept_header


def private_login_required():
    if (
        private_login_enabled()
        and request.method in {
            "GET",
            "HEAD",
        }
        and _browser_html_request()
    ):
        next_url = (
            _safe_next_url(
                request.full_path
            )
            or request.path
        )

        return redirect(
            url_for(
                "private_login.login",
                next=next_url,
            )
        )

    return Response(
        "Login required",
        401,
        {
            "WWW-Authenticate": (
                'Basic realm="Aureum AI Platform"'
            )
        },
    )


@private_login_bp.route(
    "/login",
    methods=["GET", "POST"],
)
def login():
    if not private_login_enabled():
        return Response(
            "Privat login er ikke konfigureret.",
            503,
        )

    requested_next = (
        request.values.get("next")
    )
    next_url = _safe_next_url(
        requested_next
    )

    if request.method == "GET":
        current_user_id = (
            get_authenticated_session_user_id()
        )

        if current_user_id is not None:
            return redirect(
                next_url
                or "/command-center"
            )

        return _render_login(
            next_url=next_url
        )

    if not _valid_csrf_token(
        request.form.get(
            "csrf_token"
        )
    ):
        return _render_login(
            error_message=(
                "Loginformularen er udløbet. "
                "Prøv igen."
            ),
            status_code=400,
            next_url=next_url,
        )

    username = str(
        request.form.get(
            "username",
            "",
        )
    ).strip().lower()
    password = str(
        request.form.get(
            "password",
            "",
        )
    )

    if (
        len(username) > 128
        or len(password) > 4096
    ):
        username = ""
        password = ""

    attempt_key = _login_attempt_key(
        username
    )

    if _rate_limited(attempt_key):
        return _render_login(
            error_message=(
                "For mange loginforsøg. "
                "Vent 15 minutter og prøv igen."
            ),
            status_code=429,
            next_url=next_url,
        )

    credential_checker = (
        current_app.extensions.get(
            "aureum_private_credential_checker"
        )
    )

    credentials_valid = False

    try:
        credentials_valid = bool(
            username
            and password
            and credential_checker
            and credential_checker(
                username,
                password,
            )
        )
    except Exception:
        current_app.logger.exception(
            "Privat credential-kontrol fejlede."
        )

        return _render_login(
            error_message=(
                "Login kan midlertidigt ikke "
                "kontrolleres."
            ),
            status_code=503,
            next_url=next_url,
        )

    account = None

    if credentials_valid:
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
            return _render_login(
                error_message=(
                    "Login kan midlertidigt ikke "
                    "kontrolleres."
                ),
                status_code=503,
                next_url=next_url,
            )

    account_status = str(
        (account or {}).get(
            "status",
            "",
        )
    ).strip().lower()
    canonical_user_id = str(
        (account or {}).get(
            "user_id",
            "",
        )
    ).strip().lower()

    if (
        not credentials_valid
        or account_status != "active"
        or not canonical_user_id
    ):
        _record_login_failure(
            attempt_key
        )

        return _render_login(
            error_message=(
                "Brugernavn eller adgangskode "
                "er forkert."
            ),
            status_code=401,
            next_url=next_url,
        )

    _record_login_success(attempt_key)

    try:
        mfa_enabled = is_totp_enabled(
            canonical_user_id,
            path=_mfa_database_path(),
        )
    except (MfaError, AccountStoreError, OSError, sqlite3.Error):
        current_app.logger.exception(
            "MFA-status kunne ikke kontrolleres."
        )
        return _render_login(
            error_message=(
                "Login kan midlertidigt ikke "
                "sikkerhedskontrolleres."
            ),
            status_code=503,
            next_url=next_url,
        )

    if mfa_enabled:
        _begin_pending_mfa(
            canonical_user_id,
            next_url,
        )
        return redirect(
            url_for(
                "private_login.two_factor_challenge"
            )
        )

    _complete_private_login(canonical_user_id)

    return redirect(
        next_url
        or "/command-center"
    )


@private_login_bp.route(
    "/login/two-factor",
    methods=["GET", "POST"],
)
def two_factor_challenge():
    if not private_login_enabled():
        return Response(
            "Privat login er ikke konfigureret.",
            503,
        )

    pending_user_id = _pending_mfa_user_id()

    if pending_user_id is None:
        return redirect(
            url_for("private_login.login")
        )

    if request.method == "GET":
        return _render_two_factor_challenge()

    if not _valid_csrf_token(
        request.form.get("csrf_token")
    ):
        return _render_two_factor_challenge(
            error_message=(
                "Sikkerhedsformularen er udløbet. "
                "Log ind igen."
            ),
            status_code=400,
        )

    attempt_key = _login_attempt_key(
        "mfa:" + pending_user_id
    )

    if _rate_limited(attempt_key):
        return _render_two_factor_challenge(
            error_message=(
                "For mange kodeforsøg. Vent 15 minutter "
                "og prøv igen."
            ),
            status_code=429,
        )

    try:
        accepted = verify_mfa_code(
            pending_user_id,
            request.form.get("verification_code"),
            path=_mfa_database_path(),
        )
    except (MfaError, AccountStoreError, OSError, sqlite3.Error):
        current_app.logger.exception(
            "MFA-kontrol fejlede."
        )
        return _render_two_factor_challenge(
            error_message=(
                "Sikkerhedskoden kan midlertidigt ikke "
                "kontrolleres."
            ),
            status_code=503,
        )

    if not accepted:
        _record_login_failure(attempt_key)
        return _render_two_factor_challenge(
            error_message=(
                "Sikkerhedskoden er forkert eller allerede brugt."
            ),
            status_code=401,
        )

    next_url = _safe_next_url(
        session.get(SESSION_PENDING_MFA_NEXT_KEY)
    )
    _record_login_success(attempt_key)
    _complete_private_login(pending_user_id)
    return redirect(next_url or "/command-center")


@private_login_bp.get("/security/two-factor")
def two_factor_settings():
    user_id = get_authenticated_session_user_id()

    if user_id is None:
        return private_login_required()

    try:
        return _render_two_factor_settings(user_id)
    except (MfaError, AccountStoreError, OSError, sqlite3.Error):
        current_app.logger.exception(
            "MFA-indstillinger kunne ikke indlæses."
        )
        return Response(
            "MFA-indstillinger er midlertidigt utilgængelige.",
            503,
        )


@private_login_bp.post("/security/two-factor/start")
def start_two_factor_setup():
    user_id = get_authenticated_session_user_id()

    if user_id is None:
        return private_login_required()

    if not _valid_csrf_token(
        request.form.get("csrf_token")
    ):
        return Response("Ugyldig sikkerhedsanmodning.", 400)

    attempt_key = _login_attempt_key(
        "mfa-setup-password:" + user_id
    )

    if _rate_limited(attempt_key):
        return _render_two_factor_settings(
            user_id,
            error_message=(
                "For mange forsøg. Vent 15 minutter "
                "og prøv igen."
            ),
            status_code=429,
        )

    password = str(request.form.get("password", ""))

    try:
        password_valid = _current_password_valid(
            user_id,
            password,
        )
    except Exception:
        current_app.logger.exception(
            "Adgangskodekontrol til MFA fejlede."
        )
        password_valid = False

    if not password_valid:
        _record_login_failure(attempt_key)
        return _render_two_factor_settings(
            user_id,
            error_message="Adgangskoden er forkert.",
            status_code=401,
        )

    _record_login_success(attempt_key)

    try:
        start_totp_setup(
            user_id,
            path=_mfa_database_path(),
        )
        return redirect(
            url_for("private_login.two_factor_settings")
        )
    except (MfaError, AccountStoreError, OSError, sqlite3.Error) as exc:
        return _render_two_factor_settings(
            user_id,
            error_message=str(exc),
            status_code=400,
        )


@private_login_bp.post("/security/two-factor/confirm")
def confirm_two_factor_setup():
    user_id = get_authenticated_session_user_id()

    if user_id is None:
        return private_login_required()

    if not _valid_csrf_token(
        request.form.get("csrf_token")
    ):
        return Response("Ugyldig sikkerhedsanmodning.", 400)

    attempt_key = _login_attempt_key(
        "mfa-setup-confirm:" + user_id
    )

    if _rate_limited(attempt_key):
        return _render_two_factor_settings(
            user_id,
            error_message=(
                "For mange kodeforsøg. Vent 15 minutter "
                "og prøv igen."
            ),
            status_code=429,
        )

    try:
        recovery_codes = confirm_totp_setup(
            user_id,
            request.form.get("verification_code"),
            path=_mfa_database_path(),
        )
    except (MfaError, AccountStoreError, OSError, sqlite3.Error) as exc:
        return _render_two_factor_settings(
            user_id,
            error_message=str(exc),
            status_code=400,
        )

    if recovery_codes is None:
        _record_login_failure(attempt_key)
        return _render_two_factor_settings(
            user_id,
            error_message="Koden kunne ikke bekræftes.",
            status_code=400,
        )

    _record_login_success(attempt_key)

    return _render_two_factor_settings(
        user_id,
        success_message="Tofaktorgodkendelse er nu aktiv.",
        recovery_codes=recovery_codes,
    )


@private_login_bp.post("/security/two-factor/recovery-codes")
def regenerate_two_factor_recovery_codes():
    user_id = get_authenticated_session_user_id()

    if user_id is None:
        return private_login_required()

    if not _valid_csrf_token(
        request.form.get("csrf_token")
    ):
        return Response("Ugyldig sikkerhedsanmodning.", 400)

    attempt_key = _login_attempt_key(
        "mfa-recovery-regenerate:" + user_id
    )

    if _rate_limited(attempt_key):
        return _render_two_factor_settings(
            user_id,
            error_message=(
                "For mange kodeforsøg. Vent 15 minutter "
                "og prøv igen."
            ),
            status_code=429,
        )

    try:
        recovery_codes = regenerate_recovery_codes(
            user_id,
            request.form.get("verification_code"),
            path=_mfa_database_path(),
        )
    except (MfaError, AccountStoreError, OSError, sqlite3.Error):
        recovery_codes = None

    if recovery_codes is None:
        _record_login_failure(attempt_key)
        return _render_two_factor_settings(
            user_id,
            error_message=(
                "Koden er forkert, udløbet eller allerede brugt."
            ),
            status_code=400,
        )

    _record_login_success(attempt_key)

    return _render_two_factor_settings(
        user_id,
        success_message="Nye gendannelseskoder er oprettet.",
        recovery_codes=recovery_codes,
    )


@private_login_bp.post("/security/two-factor/disable")
def disable_two_factor():
    user_id = get_authenticated_session_user_id()

    if user_id is None:
        return private_login_required()

    if not _valid_csrf_token(
        request.form.get("csrf_token")
    ):
        return Response("Ugyldig sikkerhedsanmodning.", 400)

    attempt_key = _login_attempt_key(
        "mfa-disable:" + user_id
    )

    if _rate_limited(attempt_key):
        return _render_two_factor_settings(
            user_id,
            error_message=(
                "For mange forsøg. Vent 15 minutter "
                "og prøv igen."
            ),
            status_code=429,
        )

    password = str(request.form.get("password", ""))

    try:
        password_valid = _current_password_valid(
            user_id,
            password,
        )
    except Exception:
        password_valid = False

    if not password_valid:
        _record_login_failure(attempt_key)
        return _render_two_factor_settings(
            user_id,
            error_message="Adgangskoden er forkert.",
            status_code=401,
        )

    try:
        disabled = disable_totp(
            user_id,
            request.form.get("verification_code"),
            path=_mfa_database_path(),
        )
    except (MfaError, AccountStoreError, OSError, sqlite3.Error):
        disabled = False

    if not disabled:
        _record_login_failure(attempt_key)
        return _render_two_factor_settings(
            user_id,
            error_message=(
                "Koden er forkert, udløbet eller allerede brugt."
            ),
            status_code=400,
        )

    _record_login_success(attempt_key)

    return _render_two_factor_settings(
        user_id,
        success_message="Tofaktorgodkendelse er deaktiveret.",
    )


@private_login_bp.post("/logout")
def logout():
    if not private_login_enabled():
        return Response(
            "Privat login er ikke konfigureret.",
            503,
        )

    if not _valid_csrf_token(
        request.form.get(
            "csrf_token"
        )
    ):
        return Response(
            "Ugyldig logout-anmodning.",
            400,
        )

    session.clear()

    return redirect(
        url_for(
            "private_login.login",
            logged_out="1",
        )
    )


@private_login_bp.get("/robots.txt")
def robots_txt():
    return Response(
        "User-agent: *\nDisallow: /\n",
        mimetype="text/plain",
    )


def _private_login_context():
    enabled = private_login_enabled()
    user_id = None
    logout_csrf_token = ""

    if enabled:
        user_id = (
            get_authenticated_session_user_id()
        )

        if user_id is not None:
            logout_csrf_token = (
                _csrf_token()
            )

    return {
        "private_login_enabled": enabled,
        "private_session_active": (
            user_id is not None
        ),
        "private_session_user_id": user_id,
        "private_logout_csrf_token": (
            logout_csrf_token
        ),
    }


def _private_security_headers(response):
    response.headers.setdefault(
        "X-Robots-Tag",
        "noindex, nofollow, noarchive",
    )
    response.headers.setdefault(
        "X-Content-Type-Options",
        "nosniff",
    )
    response.headers.setdefault(
        "X-Frame-Options",
        "DENY",
    )
    response.headers.setdefault(
        "Referrer-Policy",
        "same-origin",
    )

    if (
        request.path in PRIVATE_LOGIN_PATHS
        or response.mimetype == "text/html"
    ):
        response.headers.setdefault(
            "Cache-Control",
            "no-store",
        )

    return response


def configure_private_login(
    app,
    *,
    credential_checker,
):
    if app.extensions.get(
        "aureum_private_login_configured"
    ):
        return _private_login_enabled_for_app(
            app
        )

    if not callable(credential_checker):
        raise TypeError(
            "credential_checker skal kunne kaldes."
        )

    session_secret = os.environ.get(
        SESSION_SECRET_ENVIRONMENT_VARIABLE,
        "",
    ).strip()

    if (
        session_secret
        and len(session_secret) < 32
    ):
        raise RuntimeError(
            "AUREUM_SESSION_SECRET er for kort."
        )

    enabled = bool(session_secret)

    initialize_account_store(
        app.config.get(
            "AUREUM_ACCOUNT_DATABASE"
        )
    )

    if enabled:
        app.secret_key = session_secret
        app.config.update(
            SESSION_COOKIE_NAME=(
                "aureum_private_session"
            ),
            SESSION_COOKIE_SECURE=True,
            SESSION_COOKIE_HTTPONLY=True,
            SESSION_COOKIE_SAMESITE="Lax",
            SESSION_COOKIE_PATH="/",
            PERMANENT_SESSION_LIFETIME=(
                timedelta(
                    seconds=(
                        SESSION_MAX_AGE_SECONDS
                    )
                )
            ),
            SESSION_REFRESH_EACH_REQUEST=False,
        )

    app.extensions[
        "aureum_private_credential_checker"
    ] = credential_checker
    app.extensions[
        "aureum_private_login_enabled"
    ] = enabled
    app.extensions[
        "aureum_private_login_configured"
    ] = True

    if "private_login" not in app.blueprints:
        app.register_blueprint(
            private_login_bp
        )

    app.context_processor(
        _private_login_context
    )
    app.after_request(
        _private_security_headers
    )

    return enabled
