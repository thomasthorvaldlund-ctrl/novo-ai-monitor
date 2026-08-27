"""
TOTP-baseret tofaktorgodkendelse til Aureum AI Platform.

TOTP-hemmeligheder krypteres med Fernet. Gendannelseskoder
gemmes kun som nøglede SHA-256-digests og kan bruges én gang.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import io
import os
import secrets
import sqlite3
import time
from datetime import datetime, timezone

import pyotp
import qrcode
import qrcode.image.svg
from cryptography.fernet import Fernet, InvalidToken

from user_account_service import (
    AccountStoreError,
    get_user_account,
    initialize_account_store,
)


MFA_ENCRYPTION_KEY_ENVIRONMENT_VARIABLE = (
    "AUREUM_MFA_ENCRYPTION_KEY"
)
TOTP_ISSUER = "Aureum AI Platform"
TOTP_DIGITS = 6
TOTP_INTERVAL_SECONDS = 30
TOTP_VALID_WINDOW = 1
RECOVERY_CODE_COUNT = 10
RECOVERY_ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"


class MfaError(RuntimeError):
    """Grundfejl for MFA-funktioner."""


class MfaConfigurationError(MfaError):
    """MFA-krypteringsnøglen mangler eller er ugyldig."""


class MfaStateError(MfaError):
    """Den ønskede MFA-handling passer ikke til tilstanden."""


def _utc_now():
    return datetime.now(
        timezone.utc
    ).isoformat(timespec="seconds")


def _normalize_user_id(value):
    user_id = str(value or "").strip().lower()

    if not user_id or len(user_id) > 128:
        raise ValueError("Ugyldigt bruger-ID.")

    return user_id


def _normalize_totp_code(value):
    code = "".join(
        character
        for character in str(value or "")
        if character.isdigit()
    )

    if len(code) != TOTP_DIGITS:
        return ""

    return code


def _normalize_recovery_code(value):
    return "".join(
        character
        for character in str(value or "").upper()
        if character in RECOVERY_ALPHABET
    )


def _database_path(path=None):
    return initialize_account_store(path)


def _connect(path):
    connection = sqlite3.connect(
        str(path),
        timeout=10,
    )
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 10000")
    return connection


def _fernet():
    value = os.environ.get(
        MFA_ENCRYPTION_KEY_ENVIRONMENT_VARIABLE,
        "",
    ).strip()

    if not value:
        raise MfaConfigurationError(
            "MFA-krypteringsnøglen er ikke konfigureret."
        )

    try:
        return Fernet(value.encode("ascii"))
    except (ValueError, TypeError) as exc:
        raise MfaConfigurationError(
            "MFA-krypteringsnøglen er ugyldig."
        ) from exc


def mfa_encryption_configured():
    try:
        _fernet()
        return True
    except MfaConfigurationError:
        return False


def _encrypt_secret(secret):
    return _fernet().encrypt(
        secret.encode("ascii")
    ).decode("ascii")


def _decrypt_secret(value):
    try:
        return _fernet().decrypt(
            str(value).encode("ascii")
        ).decode("ascii")
    except (InvalidToken, ValueError, UnicodeError) as exc:
        raise MfaConfigurationError(
            "Den gemte MFA-hemmelighed kan ikke dekrypteres."
        ) from exc


def _recovery_digest(code):
    normalized = _normalize_recovery_code(code)

    if len(normalized) != 16:
        return ""

    raw_key = os.environ.get(
        MFA_ENCRYPTION_KEY_ENVIRONMENT_VARIABLE,
        "",
    ).encode("ascii")
    digest_key = hashlib.sha256(
        b"aureum-mfa-recovery-v1:" + raw_key
    ).digest()

    return hmac.new(
        digest_key,
        normalized.encode("ascii"),
        hashlib.sha256,
    ).hexdigest()


def _new_recovery_codes():
    values = []

    while len(values) < RECOVERY_CODE_COUNT:
        raw = "".join(
            secrets.choice(RECOVERY_ALPHABET)
            for _ in range(16)
        )
        formatted = "-".join(
            raw[index:index + 4]
            for index in range(0, 16, 4)
        )

        if formatted not in values:
            values.append(formatted)

    return tuple(values)


def _matching_totp_step(secret, code, now=None):
    normalized = _normalize_totp_code(code)

    if not normalized:
        return None

    timestamp = int(time.time() if now is None else now)
    current_step = timestamp // TOTP_INTERVAL_SECONDS
    totp = pyotp.TOTP(
        secret,
        digits=TOTP_DIGITS,
        interval=TOTP_INTERVAL_SECONDS,
    )

    for offset in range(
        -TOTP_VALID_WINDOW,
        TOTP_VALID_WINDOW + 1,
    ):
        step = current_step + offset

        if step < 0:
            continue

        expected = totp.at(
            step * TOTP_INTERVAL_SECONDS
        )

        if hmac.compare_digest(expected, normalized):
            return step

    return None


def get_totp_status(user_id, *, path=None):
    normalized_user_id = _normalize_user_id(user_id)
    database_path = _database_path(path)
    connection = _connect(database_path)

    try:
        row = connection.execute(
            """
            SELECT
                enabled,
                created_at,
                confirmed_at,
                updated_at
            FROM user_totp_credentials
            WHERE user_id = ?
            """,
            (normalized_user_id,),
        ).fetchone()
        remaining = connection.execute(
            """
            SELECT COUNT(*)
            FROM user_mfa_recovery_codes
            WHERE user_id = ? AND used_at IS NULL
            """,
            (normalized_user_id,),
        ).fetchone()[0]

        return {
            "configured": row is not None,
            "enabled": bool(row and row["enabled"]),
            "pending": bool(row and not row["enabled"]),
            "created_at": row["created_at"] if row else None,
            "confirmed_at": row["confirmed_at"] if row else None,
            "updated_at": row["updated_at"] if row else None,
            "recovery_codes_remaining": int(remaining),
            "encryption_ready": mfa_encryption_configured(),
        }

    finally:
        connection.close()


def is_totp_enabled(user_id, *, path=None):
    return bool(
        get_totp_status(
            user_id,
            path=path,
        )["enabled"]
    )


def start_totp_setup(user_id, *, path=None):
    normalized_user_id = _normalize_user_id(user_id)
    database_path = _database_path(path)
    account = get_user_account(
        normalized_user_id,
        path=database_path,
    )

    if account is None:
        raise MfaStateError("Brugerkontoen findes ikke.")

    if str(account.get("status", "")).lower() != "active":
        raise MfaStateError("Brugerkontoen er ikke aktiv.")

    secret = pyotp.random_base32(length=32)
    encrypted_secret = _encrypt_secret(secret)
    now = _utc_now()
    connection = _connect(database_path)

    try:
        connection.execute("BEGIN IMMEDIATE")
        existing = connection.execute(
            """
            SELECT enabled
            FROM user_totp_credentials
            WHERE user_id = ?
            """,
            (normalized_user_id,),
        ).fetchone()

        if existing and existing["enabled"]:
            raise MfaStateError(
                "Tofaktorgodkendelse er allerede aktiv."
            )

        connection.execute(
            """
            INSERT INTO user_totp_credentials (
                user_id,
                encrypted_secret,
                enabled,
                last_used_step,
                created_at,
                confirmed_at,
                updated_at
            )
            VALUES (?, ?, 0, NULL, ?, NULL, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                encrypted_secret = excluded.encrypted_secret,
                enabled = 0,
                last_used_step = NULL,
                created_at = excluded.created_at,
                confirmed_at = NULL,
                updated_at = excluded.updated_at
            """,
            (
                normalized_user_id,
                encrypted_secret,
                now,
                now,
            ),
        )
        connection.execute(
            """
            DELETE FROM user_mfa_recovery_codes
            WHERE user_id = ?
            """,
            (normalized_user_id,),
        )
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    return get_totp_setup_details(
        normalized_user_id,
        path=database_path,
    )


def get_totp_setup_details(user_id, *, path=None):
    normalized_user_id = _normalize_user_id(user_id)
    database_path = _database_path(path)
    connection = _connect(database_path)

    try:
        row = connection.execute(
            """
            SELECT encrypted_secret, enabled
            FROM user_totp_credentials
            WHERE user_id = ?
            """,
            (normalized_user_id,),
        ).fetchone()

    finally:
        connection.close()

    if row is None or row["enabled"]:
        return None

    secret = _decrypt_secret(row["encrypted_secret"])
    totp = pyotp.TOTP(
        secret,
        digits=TOTP_DIGITS,
        interval=TOTP_INTERVAL_SECONDS,
    )
    uri = totp.provisioning_uri(
        name=normalized_user_id,
        issuer_name=TOTP_ISSUER,
    )
    image = qrcode.make(
        uri,
        image_factory=qrcode.image.svg.SvgPathImage,
    )
    buffer = io.BytesIO()
    image.save(buffer)
    qr_data_uri = (
        "data:image/svg+xml;base64,"
        + base64.b64encode(buffer.getvalue()).decode("ascii")
    )

    return {
        "manual_secret": " ".join(
            secret[index:index + 4]
            for index in range(0, len(secret), 4)
        ),
        "qr_data_uri": qr_data_uri,
    }


def confirm_totp_setup(user_id, code, *, path=None, now=None):
    normalized_user_id = _normalize_user_id(user_id)
    database_path = _database_path(path)
    connection = _connect(database_path)

    try:
        connection.execute("BEGIN IMMEDIATE")
        row = connection.execute(
            """
            SELECT encrypted_secret, enabled
            FROM user_totp_credentials
            WHERE user_id = ?
            """,
            (normalized_user_id,),
        ).fetchone()

        if row is None or row["enabled"]:
            raise MfaStateError(
                "Der findes ingen åben 2FA-opsætning."
            )

        secret = _decrypt_secret(row["encrypted_secret"])
        step = _matching_totp_step(secret, code, now=now)

        if step is None:
            return None

        recovery_codes = _new_recovery_codes()
        timestamp = _utc_now()
        connection.execute(
            """
            UPDATE user_totp_credentials
            SET
                enabled = 1,
                last_used_step = ?,
                confirmed_at = ?,
                updated_at = ?
            WHERE user_id = ? AND enabled = 0
            """,
            (
                step,
                timestamp,
                timestamp,
                normalized_user_id,
            ),
        )
        connection.execute(
            """
            DELETE FROM user_mfa_recovery_codes
            WHERE user_id = ?
            """,
            (normalized_user_id,),
        )
        connection.executemany(
            """
            INSERT INTO user_mfa_recovery_codes (
                user_id,
                code_digest,
                created_at,
                used_at
            )
            VALUES (?, ?, ?, NULL)
            """,
            [
                (
                    normalized_user_id,
                    _recovery_digest(recovery_code),
                    timestamp,
                )
                for recovery_code in recovery_codes
            ],
        )
        connection.commit()
        return recovery_codes

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def verify_mfa_code(user_id, code, *, path=None, now=None):
    normalized_user_id = _normalize_user_id(user_id)
    database_path = _database_path(path)
    connection = _connect(database_path)

    try:
        connection.execute("BEGIN IMMEDIATE")
        row = connection.execute(
            """
            SELECT encrypted_secret, enabled, last_used_step
            FROM user_totp_credentials
            WHERE user_id = ?
            """,
            (normalized_user_id,),
        ).fetchone()

        if row is None or not row["enabled"]:
            connection.rollback()
            return False

        normalized_totp = _normalize_totp_code(code)

        if normalized_totp:
            secret = _decrypt_secret(row["encrypted_secret"])
            step = _matching_totp_step(
                secret,
                normalized_totp,
                now=now,
            )
            last_step = row["last_used_step"]

            if (
                step is None
                or (
                    last_step is not None
                    and step <= int(last_step)
                )
            ):
                connection.rollback()
                return False

            cursor = connection.execute(
                """
                UPDATE user_totp_credentials
                SET last_used_step = ?, updated_at = ?
                WHERE
                    user_id = ?
                    AND enabled = 1
                    AND (
                        last_used_step IS NULL
                        OR last_used_step < ?
                    )
                """,
                (
                    step,
                    _utc_now(),
                    normalized_user_id,
                    step,
                ),
            )
            accepted = cursor.rowcount == 1
            connection.commit() if accepted else connection.rollback()
            return accepted

        digest = _recovery_digest(code)

        if not digest:
            connection.rollback()
            return False

        cursor = connection.execute(
            """
            UPDATE user_mfa_recovery_codes
            SET used_at = ?
            WHERE
                user_id = ?
                AND code_digest = ?
                AND used_at IS NULL
            """,
            (
                _utc_now(),
                normalized_user_id,
                digest,
            ),
        )
        accepted = cursor.rowcount == 1
        connection.commit() if accepted else connection.rollback()
        return accepted

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def regenerate_recovery_codes(
    user_id,
    verification_code,
    *,
    path=None,
    now=None,
):
    normalized_user_id = _normalize_user_id(user_id)

    if not verify_mfa_code(
        normalized_user_id,
        verification_code,
        path=path,
        now=now,
    ):
        return None

    database_path = _database_path(path)
    recovery_codes = _new_recovery_codes()
    timestamp = _utc_now()
    connection = _connect(database_path)

    try:
        with connection:
            connection.execute(
                """
                DELETE FROM user_mfa_recovery_codes
                WHERE user_id = ?
                """,
                (normalized_user_id,),
            )
            connection.executemany(
                """
                INSERT INTO user_mfa_recovery_codes (
                    user_id,
                    code_digest,
                    created_at,
                    used_at
                )
                VALUES (?, ?, ?, NULL)
                """,
                [
                    (
                        normalized_user_id,
                        _recovery_digest(code),
                        timestamp,
                    )
                    for code in recovery_codes
                ],
            )

        return recovery_codes

    finally:
        connection.close()


def disable_totp(
    user_id,
    verification_code,
    *,
    path=None,
    now=None,
):
    normalized_user_id = _normalize_user_id(user_id)

    if not verify_mfa_code(
        normalized_user_id,
        verification_code,
        path=path,
        now=now,
    ):
        return False

    database_path = _database_path(path)
    connection = _connect(database_path)

    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            """
            DELETE FROM user_mfa_recovery_codes
            WHERE user_id = ?
            """,
            (normalized_user_id,),
        )
        connection.execute(
            """
            DELETE FROM user_totp_credentials
            WHERE user_id = ?
            """,
            (normalized_user_id,),
        )
        connection.commit()
        return True

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
