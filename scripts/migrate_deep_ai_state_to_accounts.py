#!/usr/bin/env python3
"""
Migrerer Deep AI-rettigheder og personlige aktietilvalg
fra de tidligere JSON-filer til den centrale kontodatabase.

Migrationen er:
- validerende;
- transaktionssikker;
- idempotent;
- bagudkompatibel, fordi JSON-filerne ikke ændres.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import sys

REPOSITORY_ROOT = (
    Path(__file__).resolve().parents[1]
)

if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(REPOSITORY_ROOT),
    )

from user_account_service import (
    initialize_account_store,
)


STATE_VERSION = 1

DEFAULT_ACCOUNT_DB = Path(
    "aureum_accounts.sqlite3"
)

DEFAULT_ENTITLEMENTS_FILE = Path(
    "deep_ai_entitlements.json"
)

DEFAULT_SELECTIONS_FILE = Path(
    "deep_ai_selections.json"
)

_PLAN_CODE_PATTERN = re.compile(
    r"[a-z0-9][a-z0-9_-]{0,31}"
)


def _utc_now():
    return datetime.now(
        timezone.utc
    ).replace(
        microsecond=0
    ).isoformat()


def _normalize_user_id(value):
    user_id = str(value or "").strip().lower()

    if not user_id:
        raise ValueError(
            "user_id må ikke være tom."
        )

    return user_id


def _load_state(path, label):
    selected_path = Path(path)

    data = json.loads(
        selected_path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(data, dict):
        raise ValueError(
            f"{label} skal være et objekt."
        )

    if data.get("version") != STATE_VERSION:
        raise ValueError(
            f"{label} har en ukendt version."
        )

    users = data.get("users")

    if not isinstance(users, dict):
        raise ValueError(
            f"{label}.users skal være et objekt."
        )

    return users


def _normalize_slot_count(
    value,
    field_name,
):
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 0
    ):
        raise ValueError(
            f"{field_name} skal være "
            "et ikke-negativt heltal."
        )

    return value


def _normalize_entitlement(record):
    if not isinstance(record, dict):
        raise ValueError(
            "Rettighedsposten skal være "
            "et objekt."
        )

    plan_code = str(
        record.get(
            "plan_code",
            "",
        )
    ).strip().lower()

    if not _PLAN_CODE_PATTERN.fullmatch(
        plan_code
    ):
        raise ValueError(
            "Ugyldig plan_code."
        )

    included_slots = (
        _normalize_slot_count(
            record.get("included_slots"),
            "included_slots",
        )
    )

    purchased_slots = (
        _normalize_slot_count(
            record.get(
                "purchased_slots",
                0,
            ),
            "purchased_slots",
        )
    )

    unlimited = record.get(
        "unlimited",
        False,
    )

    if not isinstance(unlimited, bool):
        raise ValueError(
            "unlimited skal være bool."
        )

    return {
        "plan_code": plan_code,
        "included_slots": included_slots,
        "purchased_slots": purchased_slots,
        "unlimited": unlimited,
    }


def _normalize_selections(record):
    if not isinstance(record, dict):
        raise ValueError(
            "Tilvalgsposten skal være "
            "et objekt."
        )

    raw_symbols = record.get(
        "selected_symbols",
        [],
    )

    if not isinstance(raw_symbols, list):
        raise ValueError(
            "selected_symbols skal være "
            "en liste."
        )

    symbols = []

    for raw_symbol in raw_symbols:
        symbol = str(
            raw_symbol or ""
        ).strip().upper()

        if not symbol:
            raise ValueError(
                "Et aktiesymbol må ikke "
                "være tomt."
            )

        if len(symbol) > 64:
            raise ValueError(
                "Aktiesymbolet er for langt."
            )

        symbols.append(symbol)

    return sorted(set(symbols))


def migrate_deep_ai_state(
    *,
    account_db=DEFAULT_ACCOUNT_DB,
    entitlements_file=(
        DEFAULT_ENTITLEMENTS_FILE
    ),
    selections_file=(
        DEFAULT_SELECTIONS_FILE
    ),
):
    account_db = Path(account_db)

    entitlement_users = _load_state(
        entitlements_file,
        "deep_ai_entitlements",
    )

    selection_users = _load_state(
        selections_file,
        "deep_ai_selections",
    )

    normalized_entitlements = {
        _normalize_user_id(user_id):
        _normalize_entitlement(record)
        for user_id, record
        in entitlement_users.items()
    }

    normalized_selections = {
        _normalize_user_id(user_id):
        _normalize_selections(record)
        for user_id, record
        in selection_users.items()
    }

    all_user_ids = sorted({
        *normalized_entitlements,
        *normalized_selections,
    })

    for user_id, symbols in (
        normalized_selections.items()
    ):
        entitlement = (
            normalized_entitlements.get(
                user_id,
                {
                    "included_slots": 0,
                    "purchased_slots": 0,
                    "unlimited": False,
                },
            )
        )

        if entitlement.get("unlimited"):
            continue

        selection_limit = (
            entitlement["included_slots"]
            + entitlement[
                "purchased_slots"
            ]
        )

        if len(symbols) > selection_limit:
            raise ValueError(
                "Deep AI-tilvalgene overskrider "
                f"kvoten for {user_id}."
            )

    initialize_account_store(
        path=account_db
    )

    connection = sqlite3.connect(
        account_db,
        timeout=15,
    )

    connection.row_factory = sqlite3.Row
    connection.execute(
        "PRAGMA foreign_keys = ON"
    )
    connection.execute(
        "PRAGMA busy_timeout = 15000"
    )

    timestamp = _utc_now()

    try:
        with connection:
            existing_users = {
                row["user_id"]
                for row in connection.execute(
                    """
                    SELECT user_id
                    FROM users
                    WHERE user_id IN (
                        SELECT value
                        FROM json_each(?)
                    )
                    """,
                    (
                        json.dumps(
                            all_user_ids
                        ),
                    ),
                ).fetchall()
            } if all_user_ids else set()

            missing_users = sorted(
                set(all_user_ids)
                - existing_users
            )

            if missing_users:
                raise ValueError(
                    "Kontodatabasen mangler "
                    f"brugere: {missing_users}"
                )

            for user_id, record in (
                normalized_entitlements.items()
            ):
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
                        updated_at = CASE
                            WHEN
                                deep_ai_entitlements.plan_code
                                    != excluded.plan_code
                                OR
                                deep_ai_entitlements.included_slots
                                    != excluded.included_slots
                                OR
                                deep_ai_entitlements.purchased_slots
                                    != excluded.purchased_slots
                                OR
                                deep_ai_entitlements.unlimited
                                    != excluded.unlimited
                            THEN excluded.updated_at
                            ELSE
                                deep_ai_entitlements.updated_at
                        END
                    """,
                    (
                        user_id,
                        record["plan_code"],
                        record["included_slots"],
                        record[
                            "purchased_slots"
                        ],
                        int(
                            record["unlimited"]
                        ),
                        timestamp,
                    ),
                )

            for user_id, symbols in (
                normalized_selections.items()
            ):
                if symbols:
                    placeholders = ",".join(
                        "?"
                        for _ in symbols
                    )

                    connection.execute(
                        f"""
                        DELETE FROM
                            deep_ai_selections
                        WHERE
                            user_id = ?
                            AND symbol NOT IN (
                                {placeholders}
                            )
                        """,
                        (
                            user_id,
                            *symbols,
                        ),
                    )
                else:
                    connection.execute(
                        """
                        DELETE FROM
                            deep_ai_selections
                        WHERE user_id = ?
                        """,
                        (
                            user_id,
                        ),
                    )

                for symbol in symbols:
                    connection.execute(
                        """
                        INSERT INTO
                            deep_ai_selections (
                                user_id,
                                symbol,
                                created_at
                            )
                        VALUES (?, ?, ?)
                        ON CONFLICT(
                            user_id,
                            symbol
                        )
                        DO NOTHING
                        """,
                        (
                            user_id,
                            symbol,
                            timestamp,
                        ),
                    )

        entitlement_count = (
            connection.execute(
                """
                SELECT COUNT(*)
                FROM deep_ai_entitlements
                """
            ).fetchone()[0]
        )

        selection_count = (
            connection.execute(
                """
                SELECT COUNT(*)
                FROM deep_ai_selections
                """
            ).fetchone()[0]
        )

        quick_check = connection.execute(
            "PRAGMA quick_check"
        ).fetchone()[0]

        schema_version = connection.execute(
            "PRAGMA user_version"
        ).fetchone()[0]

    finally:
        connection.close()

    if quick_check != "ok":
        raise RuntimeError(
            "SQLite quick_check fejlede."
        )

    return {
        "schema_version": schema_version,
        "migrated_user_ids": all_user_ids,
        "entitlement_count": (
            entitlement_count
        ),
        "selection_count": selection_count,
        "legacy_files_changed": False,
    }


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Migrér Deep AI JSON-state til "
            "den centrale kontodatabase."
        )
    )

    parser.add_argument(
        "--account-db",
        type=Path,
        default=DEFAULT_ACCOUNT_DB,
    )

    parser.add_argument(
        "--entitlements-file",
        type=Path,
        default=DEFAULT_ENTITLEMENTS_FILE,
    )

    parser.add_argument(
        "--selections-file",
        type=Path,
        default=DEFAULT_SELECTIONS_FILE,
    )

    args = parser.parse_args()

    result = migrate_deep_ai_state(
        account_db=args.account_db,
        entitlements_file=(
            args.entitlements_file
        ),
        selections_file=(
            args.selections_file
        ),
    )

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
