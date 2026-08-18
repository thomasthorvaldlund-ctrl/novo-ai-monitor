"""
SQLite-adapter for Deep AI-rettigheder og personlige tilvalg.

Dette modul indeholder kun databaseadgang. Validering mod
aktieuniverset, kvoteregler og JSON-fallback ligger fortsat
i de eksisterende Deep AI-services.
"""

from __future__ import annotations

import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from user_account_service import (
    AccountNotFoundError,
    AccountStoreError,
    DEFAULT_ACCOUNT_DB,
    initialize_account_store,
)


_USER_ID_PATTERN = re.compile(
    r"[a-z0-9][a-z0-9_.-]{0,63}"
)

_PLAN_CODE_PATTERN = re.compile(
    r"[a-z0-9][a-z0-9_-]{0,31}"
)

_SYMBOL_PATTERN = re.compile(
    r"[A-Z0-9][A-Z0-9_.-]{0,63}"
)


def _database_path(path=None):
    selected = (
        Path(path)
        if path is not None
        else DEFAULT_ACCOUNT_DB
    )

    return selected.expanduser()


def _utc_now():
    return datetime.now(
        timezone.utc
    ).replace(
        microsecond=0
    ).isoformat()


def _normalize_user_id(user_id):
    normalized = str(
        user_id or ""
    ).strip().lower()

    if not _USER_ID_PATTERN.fullmatch(
        normalized
    ):
        raise ValueError(
            "Ugyldigt Deep AI-bruger-id."
        )

    return normalized


def _normalize_plan_code(plan_code):
    normalized = str(
        plan_code or ""
    ).strip().lower()

    if not _PLAN_CODE_PATTERN.fullmatch(
        normalized
    ):
        raise ValueError(
            "Ugyldig Deep AI-plan."
        )

    return normalized


def _validate_slot_count(
    value,
    field_name,
):
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 0
        or value > 1000
    ):
        raise ValueError(
            f"{field_name} skal være et heltal "
            "mellem 0 og 1000."
        )

    return value


def _normalize_symbols(symbols):
    if isinstance(
        symbols,
        (str, bytes),
    ):
        raise ValueError(
            "Deep AI-symboler skal være en liste."
        )

    normalized = sorted({
        str(symbol or "").strip().upper()
        for symbol in symbols
        if str(symbol or "").strip()
    })

    invalid = [
        symbol
        for symbol in normalized
        if not _SYMBOL_PATTERN.fullmatch(
            symbol
        )
    ]

    if invalid:
        raise ValueError(
            "Ugyldige Deep AI-symboler: "
            + ", ".join(invalid)
        )

    return normalized


def _secure_database_files(path):
    database_path = _database_path(path)

    for candidate in (
        database_path,
        Path(f"{database_path}-wal"),
        Path(f"{database_path}-shm"),
    ):
        if candidate.exists():
            os.chmod(
                candidate,
                0o600,
            )


def _connect_existing(path=None):
    database_path = _database_path(path)

    if not database_path.exists():
        raise AccountStoreError(
            "Kontodatabasen findes ikke."
        )

    connection = sqlite3.connect(
        database_path,
        timeout=15,
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )
    connection.execute(
        "PRAGMA busy_timeout = 15000"
    )
    connection.execute(
        "PRAGMA journal_mode = WAL"
    )

    version = connection.execute(
        "PRAGMA user_version"
    ).fetchone()[0]

    if version != 2:
        connection.close()

        raise AccountStoreError(
            "Kontodatabasen har ikke "
            "Deep AI-schema version 2."
        )

    return database_path, connection


def _require_user(
    connection,
    user_id,
):
    row = connection.execute(
        """
        SELECT user_id
        FROM users
        WHERE user_id = ?
        """,
        (
            user_id,
        ),
    ).fetchone()

    if row is None:
        raise AccountNotFoundError(
            "Brugerkontoen findes ikke."
        )


def load_deep_ai_entitlement_records(
    *,
    path=None,
):
    """
    Returnerer alle eksplicitte Deep AI-rettigheder.
    """
    database_path, connection = (
        _connect_existing(path)
    )

    try:
        rows = connection.execute(
            """
            SELECT
                user_id,
                plan_code,
                included_slots,
                purchased_slots,
                unlimited
            FROM deep_ai_entitlements
            ORDER BY user_id
            """
        ).fetchall()

        return {
            row["user_id"]: {
                "plan_code": row[
                    "plan_code"
                ],
                "included_slots": row[
                    "included_slots"
                ],
                "purchased_slots": row[
                    "purchased_slots"
                ],
                "unlimited": bool(
                    row["unlimited"]
                ),
            }
            for row in rows
        }

    finally:
        connection.close()
        _secure_database_files(
            database_path
        )


def set_deep_ai_entitlement_record(
    user_id,
    *,
    plan_code,
    included_slots,
    purchased_slots=0,
    unlimited=False,
    path=None,
):
    """
    Opretter eller erstatter én rettighedspost.
    """
    normalized_user_id = (
        _normalize_user_id(user_id)
    )
    normalized_plan_code = (
        _normalize_plan_code(plan_code)
    )
    normalized_included = (
        _validate_slot_count(
            included_slots,
            "included_slots",
        )
    )
    normalized_purchased = (
        _validate_slot_count(
            purchased_slots,
            "purchased_slots",
        )
    )

    if not isinstance(unlimited, bool):
        raise ValueError(
            "unlimited skal være true eller false."
        )

    database_path = initialize_account_store(
        _database_path(path)
    )

    database_path, connection = (
        _connect_existing(database_path)
    )

    try:
        with connection:
            _require_user(
                connection,
                normalized_user_id,
            )

            connection.execute(
                """
                INSERT INTO deep_ai_entitlements (
                    user_id,
                    plan_code,
                    included_slots,
                    purchased_slots,
                    unlimited,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id)
                DO UPDATE SET
                    plan_code =
                        excluded.plan_code,
                    included_slots =
                        excluded.included_slots,
                    purchased_slots =
                        excluded.purchased_slots,
                    unlimited =
                        excluded.unlimited,
                    updated_at =
                        excluded.updated_at
                """,
                (
                    normalized_user_id,
                    normalized_plan_code,
                    normalized_included,
                    normalized_purchased,
                    int(unlimited),
                    _utc_now(),
                ),
            )

    finally:
        connection.close()
        _secure_database_files(
            database_path
        )

    return {
        "user_id": normalized_user_id,
        "plan_code": normalized_plan_code,
        "included_slots": normalized_included,
        "purchased_slots": normalized_purchased,
        "unlimited": unlimited,
    }


def load_deep_ai_selection_records(
    *,
    path=None,
):
    """
    Returnerer personlige Deep AI-symboler pr. bruger.
    """
    database_path, connection = (
        _connect_existing(path)
    )

    try:
        rows = connection.execute(
            """
            SELECT user_id, symbol
            FROM deep_ai_selections
            ORDER BY user_id, symbol
            """
        ).fetchall()

        records = {}

        for row in rows:
            records.setdefault(
                row["user_id"],
                [],
            ).append(
                row["symbol"].upper()
            )

        return records

    finally:
        connection.close()
        _secure_database_files(
            database_path
        )


def replace_deep_ai_selection_records(
    user_id,
    symbols,
    *,
    path=None,
):
    """
    Erstatter atomisk én brugers personlige symboler.
    """
    normalized_user_id = (
        _normalize_user_id(user_id)
    )
    normalized_symbols = (
        _normalize_symbols(symbols)
    )

    database_path = initialize_account_store(
        _database_path(path)
    )

    database_path, connection = (
        _connect_existing(database_path)
    )

    try:
        with connection:
            _require_user(
                connection,
                normalized_user_id,
            )

            if normalized_symbols:
                placeholders = ", ".join(
                    "?"
                    for _ in normalized_symbols
                )

                connection.execute(
                    f"""
                    DELETE FROM deep_ai_selections
                    WHERE
                        user_id = ?
                        AND symbol NOT IN (
                            {placeholders}
                        )
                    """,
                    (
                        normalized_user_id,
                        *normalized_symbols,
                    ),
                )
            else:
                connection.execute(
                    """
                    DELETE FROM deep_ai_selections
                    WHERE user_id = ?
                    """,
                    (
                        normalized_user_id,
                    ),
                )

            created_at = _utc_now()

            for symbol in normalized_symbols:
                connection.execute(
                    """
                    INSERT INTO deep_ai_selections (
                        user_id,
                        symbol,
                        created_at
                    )
                    VALUES (?, ?, ?)
                    ON CONFLICT(user_id, symbol)
                    DO NOTHING
                    """,
                    (
                        normalized_user_id,
                        symbol,
                        created_at,
                    ),
                )

    finally:
        connection.close()
        _secure_database_files(
            database_path
        )

    return {
        "user_id": normalized_user_id,
        "selected_symbols": normalized_symbols,
    }
