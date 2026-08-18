"""
Central og backend-isoleret kontoservice.

Den første implementering bruger SQLite på den nuværende
enkeltserver. Flask-routes og øvrige services skal kun bruge
funktionerne i dette modul, så lageret senere kan erstattes
med PostgreSQL uden at ændre brugerfladen.
"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


SCHEMA_VERSION = 3

VALID_ACCOUNT_ROLES = frozenset({
    "admin",
})

DEFAULT_ACCOUNT_DB = Path(
    os.environ.get(
        "AUREUM_ACCOUNT_DB_PATH",
        "aureum_accounts.sqlite3",
    )
)

VALID_ACCOUNT_STATUSES = frozenset({
    "active",
    "disabled",
    "pending",
})


class AccountStoreError(RuntimeError):
    """Grundfejl for kontolageret."""


class AccountConflictError(AccountStoreError):
    """Identitet eller brugernavn tilhører en anden konto."""


class AccountNotFoundError(AccountStoreError):
    """Den ønskede konto findes ikke."""


def _utc_now():
    return datetime.now(
        timezone.utc
    ).replace(
        microsecond=0
    ).isoformat()


def _database_path(path=None):
    selected = (
        Path(path)
        if path is not None
        else DEFAULT_ACCOUNT_DB
    )

    return selected.expanduser()


def _required_text(
    value,
    field_name,
    *,
    lowercase=False,
):
    text = str(value or "").strip()

    if not text:
        raise ValueError(
            f"{field_name} må ikke være tom."
        )

    if lowercase:
        text = text.lower()

    return text


def _optional_text(
    value,
    *,
    lowercase=False,
):
    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    if lowercase:
        text = text.lower()

    return text


def _connect(path):
    database_path = _database_path(path)

    database_path.parent.mkdir(
        parents=True,
        exist_ok=True,
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

    return connection


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


def _row_to_account(row):
    if row is None:
        return None

    return {
        "user_id": row["user_id"],
        "username": row["username"],
        "email": row["email"],
        "status": row["status"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def initialize_account_store(path=None):
    """
    Opretter eller migrerer kontodatabasen additivt.

    Version 1:
        users og user_identities.

    Version 2:
        Deep AI-rettigheder og personlige aktietilvalg.

    Version 3:
        Eksplicitte brugerroller til central adgangskontrol.

    Eksisterende tabeller og brugeridentiteter ændres ikke.
    """

    database_path = _database_path(path)
    connection = _connect(database_path)

    try:
        version = connection.execute(
            "PRAGMA user_version"
        ).fetchone()[0]

        if version > SCHEMA_VERSION:
            raise AccountStoreError(
                "Kontodatabasen bruger en nyere "
                f"skemaversion: {version}."
            )

        if version == 0:
            connection.executescript(
                """
                BEGIN IMMEDIATE;

                CREATE TABLE users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT
                        COLLATE NOCASE
                        UNIQUE,
                    email TEXT
                        COLLATE NOCASE
                        UNIQUE,
                    status TEXT NOT NULL
                        CHECK (
                            status IN (
                                'active',
                                'disabled',
                                'pending'
                            )
                        ),
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE user_identities (
                    provider TEXT
                        COLLATE NOCASE
                        NOT NULL,
                    subject TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (
                        provider,
                        subject
                    ),
                    FOREIGN KEY (user_id)
                        REFERENCES users(user_id)
                        ON DELETE CASCADE
                );

                CREATE INDEX
                    idx_user_identities_user_id
                ON user_identities(user_id);

                PRAGMA user_version = 1;

                COMMIT;
                """
            )

            version = 1

        if version == 1:
            connection.executescript(
                """
                BEGIN IMMEDIATE;

                CREATE TABLE deep_ai_entitlements (
                    user_id TEXT PRIMARY KEY,
                    plan_code TEXT NOT NULL,
                    included_slots INTEGER NOT NULL
                        CHECK (
                            included_slots >= 0
                        ),
                    purchased_slots INTEGER NOT NULL
                        CHECK (
                            purchased_slots >= 0
                        ),
                    unlimited INTEGER NOT NULL
                        CHECK (
                            unlimited IN (0, 1)
                        ),
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (user_id)
                        REFERENCES users(user_id)
                        ON DELETE CASCADE
                );

                CREATE TABLE deep_ai_selections (
                    user_id TEXT NOT NULL,
                    symbol TEXT
                        COLLATE NOCASE
                        NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (
                        user_id,
                        symbol
                    ),
                    FOREIGN KEY (user_id)
                        REFERENCES users(user_id)
                        ON DELETE CASCADE
                );

                CREATE INDEX
                    idx_deep_ai_selections_symbol
                ON deep_ai_selections(symbol);

                PRAGMA user_version = 2;

                COMMIT;
                """
            )

            version = 2

        if version == 2:
            connection.executescript(
                """
                BEGIN IMMEDIATE;

                CREATE TABLE user_roles (
                    user_id TEXT NOT NULL,
                    role TEXT
                        COLLATE NOCASE
                        NOT NULL
                        CHECK (
                            role IN (
                                'admin'
                            )
                        ),
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (
                        user_id,
                        role
                    ),
                    FOREIGN KEY (user_id)
                        REFERENCES users(user_id)
                        ON DELETE CASCADE
                );

                CREATE INDEX
                    idx_user_roles_role
                ON user_roles(role);

                PRAGMA user_version = 3;

                COMMIT;
                """
            )

            version = 3

        if version != SCHEMA_VERSION:
            raise AccountStoreError(
                "Kontodatabasen kunne ikke "
                "migreres til forventet version."
            )

    finally:
        connection.close()
        _secure_database_files(
            database_path
        )

    return database_path

def get_account_store_status(path=None):
    database_path = _database_path(path)

    if not database_path.exists():
        return {
            "path": str(database_path),
            "exists": False,
            "schema_version": 0,
        }

    connection = _connect(database_path)

    try:
        version = connection.execute(
            "PRAGMA user_version"
        ).fetchone()[0]
    finally:
        connection.close()
        _secure_database_files(
            database_path
        )

    return {
        "path": str(database_path),
        "exists": True,
        "schema_version": version,
    }


def ensure_user_account(
    user_id,
    *,
    username=None,
    email=None,
    status="active",
    path=None,
):
    """
    Opretter en konto, hvis den ikke findes.

    Eksisterende status ændres ikke. Manglende brugernavn
    eller e-mail kan udfyldes, men erstattes ikke automatisk.
    """

    normalized_user_id = _required_text(
        user_id,
        "user_id",
        lowercase=True,
    )

    normalized_username = _optional_text(
        username,
        lowercase=True,
    )

    normalized_email = _optional_text(
        email,
        lowercase=True,
    )

    normalized_status = _required_text(
        status,
        "status",
        lowercase=True,
    )

    if (
        normalized_status
        not in VALID_ACCOUNT_STATUSES
    ):
        raise ValueError(
            "Ugyldig kontostatus."
        )

    database_path = initialize_account_store(
        path
    )

    now = _utc_now()
    connection = _connect(database_path)

    try:
        with connection:
            connection.execute(
                """
                INSERT INTO users (
                    user_id,
                    username,
                    email,
                    status,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id)
                DO UPDATE SET
                    username = COALESCE(
                        users.username,
                        excluded.username
                    ),
                    email = COALESCE(
                        users.email,
                        excluded.email
                    ),
                    updated_at = excluded.updated_at
                """,
                (
                    normalized_user_id,
                    normalized_username,
                    normalized_email,
                    normalized_status,
                    now,
                    now,
                ),
            )

    except sqlite3.IntegrityError as error:
        raise AccountConflictError(
            "Brugernavn eller e-mail "
            "tilhører allerede en anden konto."
        ) from error

    finally:
        connection.close()
        _secure_database_files(
            database_path
        )

    return get_user_account(
        normalized_user_id,
        path=database_path,
    )


def get_user_account(
    user_id,
    *,
    path=None,
):
    normalized_user_id = _required_text(
        user_id,
        "user_id",
        lowercase=True,
    )

    database_path = _database_path(path)

    if not database_path.exists():
        return None

    connection = _connect(database_path)

    try:
        row = connection.execute(
            """
            SELECT
                user_id,
                username,
                email,
                status,
                created_at,
                updated_at
            FROM users
            WHERE user_id = ?
            """,
            (
                normalized_user_id,
            ),
        ).fetchone()

        return _row_to_account(row)

    finally:
        connection.close()
        _secure_database_files(
            database_path
        )


def get_user_account_by_username(
    username,
    *,
    path=None,
):
    normalized_username = _required_text(
        username,
        "username",
        lowercase=True,
    )

    database_path = _database_path(path)

    if not database_path.exists():
        return None

    connection = _connect(database_path)

    try:
        row = connection.execute(
            """
            SELECT
                user_id,
                username,
                email,
                status,
                created_at,
                updated_at
            FROM users
            WHERE username = ?
            """,
            (
                normalized_username,
            ),
        ).fetchone()

        return _row_to_account(row)

    finally:
        connection.close()
        _secure_database_files(
            database_path
        )


def set_user_account_status(
    user_id,
    status,
    *,
    path=None,
):
    normalized_user_id = _required_text(
        user_id,
        "user_id",
        lowercase=True,
    )

    normalized_status = _required_text(
        status,
        "status",
        lowercase=True,
    )

    if (
        normalized_status
        not in VALID_ACCOUNT_STATUSES
    ):
        raise ValueError(
            "Ugyldig kontostatus."
        )

    database_path = initialize_account_store(
        path
    )

    connection = _connect(database_path)

    try:
        with connection:
            cursor = connection.execute(
                """
                UPDATE users
                SET
                    status = ?,
                    updated_at = ?
                WHERE user_id = ?
                """,
                (
                    normalized_status,
                    _utc_now(),
                    normalized_user_id,
                ),
            )

            if cursor.rowcount != 1:
                raise AccountNotFoundError(
                    "Brugerkontoen findes ikke."
                )

    finally:
        connection.close()
        _secure_database_files(
            database_path
        )

    return get_user_account(
        normalized_user_id,
        path=database_path,
    )


def link_user_identity(
    user_id,
    provider,
    subject,
    *,
    path=None,
):
    normalized_user_id = _required_text(
        user_id,
        "user_id",
        lowercase=True,
    )

    normalized_provider = _required_text(
        provider,
        "provider",
        lowercase=True,
    )

    normalized_subject = _required_text(
        subject,
        "subject",
    )

    database_path = initialize_account_store(
        path
    )

    if get_user_account(
        normalized_user_id,
        path=database_path,
    ) is None:
        raise AccountNotFoundError(
            "Brugerkontoen findes ikke."
        )

    connection = _connect(database_path)

    try:
        with connection:
            existing = connection.execute(
                """
                SELECT user_id
                FROM user_identities
                WHERE
                    provider = ?
                    AND subject = ?
                """,
                (
                    normalized_provider,
                    normalized_subject,
                ),
            ).fetchone()

            if existing is not None:
                if (
                    existing["user_id"]
                    != normalized_user_id
                ):
                    raise AccountConflictError(
                        "Identiteten tilhører "
                        "allerede en anden konto."
                    )

                return get_user_account(
                    normalized_user_id,
                    path=database_path,
                )

            connection.execute(
                """
                INSERT INTO user_identities (
                    provider,
                    subject,
                    user_id,
                    created_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    normalized_provider,
                    normalized_subject,
                    normalized_user_id,
                    _utc_now(),
                ),
            )

    finally:
        connection.close()
        _secure_database_files(
            database_path
        )

    return get_user_account(
        normalized_user_id,
        path=database_path,
    )


def resolve_user_identity(
    provider,
    subject,
    *,
    path=None,
):
    normalized_provider = _required_text(
        provider,
        "provider",
        lowercase=True,
    )

    normalized_subject = _required_text(
        subject,
        "subject",
    )

    database_path = _database_path(path)

    if not database_path.exists():
        return None

    connection = _connect(database_path)

    try:
        row = connection.execute(
            """
            SELECT
                users.user_id,
                users.username,
                users.email,
                users.status,
                users.created_at,
                users.updated_at
            FROM user_identities
            INNER JOIN users
                ON users.user_id =
                    user_identities.user_id
            WHERE
                user_identities.provider = ?
                AND user_identities.subject = ?
            """,
            (
                normalized_provider,
                normalized_subject,
            ),
        ).fetchone()

        return _row_to_account(row)

    finally:
        connection.close()
        _secure_database_files(
            database_path
        )

def _normalize_account_role(role):
    normalized_role = _required_text(
        role,
        "role",
        lowercase=True,
    )

    if (
        normalized_role
        not in VALID_ACCOUNT_ROLES
    ):
        raise ValueError(
            "Ugyldig brugerrolle."
        )

    return normalized_role


def get_user_account_roles(
    user_id,
    *,
    path=None,
):
    """
    Returnerer kontoens eksplicitte roller.

    Funktionen er read-only og migrerer ikke databasen.
    """

    normalized_user_id = _required_text(
        user_id,
        "user_id",
        lowercase=True,
    )

    database_path = _database_path(path)

    if not database_path.exists():
        return []

    connection = _connect(database_path)

    try:
        version = connection.execute(
            "PRAGMA user_version"
        ).fetchone()[0]

        if version < 3:
            return []

        rows = connection.execute(
            """
            SELECT role
            FROM user_roles
            WHERE user_id = ?
            ORDER BY role
            """,
            (
                normalized_user_id,
            ),
        ).fetchall()

        return [
            row["role"]
            for row in rows
        ]

    finally:
        connection.close()
        _secure_database_files(
            database_path
        )


def user_has_account_role(
    user_id,
    role,
    *,
    path=None,
):
    normalized_role = (
        _normalize_account_role(
            role
        )
    )

    return (
        normalized_role
        in get_user_account_roles(
            user_id,
            path=path,
        )
    )


def set_user_account_role(
    user_id,
    role,
    *,
    enabled=True,
    path=None,
):
    normalized_user_id = _required_text(
        user_id,
        "user_id",
        lowercase=True,
    )

    normalized_role = (
        _normalize_account_role(
            role
        )
    )

    if not isinstance(enabled, bool):
        raise ValueError(
            "enabled skal være boolsk."
        )

    database_path = initialize_account_store(
        path
    )

    if get_user_account(
        normalized_user_id,
        path=database_path,
    ) is None:
        raise AccountNotFoundError(
            "Brugerkontoen findes ikke."
        )

    connection = _connect(database_path)

    try:
        with connection:
            if enabled:
                connection.execute(
                    """
                    INSERT INTO user_roles (
                        user_id,
                        role,
                        created_at
                    )
                    VALUES (?, ?, ?)
                    ON CONFLICT(
                        user_id,
                        role
                    )
                    DO NOTHING
                    """,
                    (
                        normalized_user_id,
                        normalized_role,
                        _utc_now(),
                    ),
                )
            else:
                connection.execute(
                    """
                    DELETE FROM user_roles
                    WHERE
                        user_id = ?
                        AND role = ?
                    """,
                    (
                        normalized_user_id,
                        normalized_role,
                    ),
                )

    finally:
        connection.close()
        _secure_database_files(
            database_path
        )

    return get_user_account_roles(
        normalized_user_id,
        path=database_path,
    )


def list_user_accounts(
    *,
    path=None,
):
    database_path = _database_path(path)

    if not database_path.exists():
        return []

    connection = _connect(database_path)

    try:
        version = connection.execute(
            "PRAGMA user_version"
        ).fetchone()[0]

        account_rows = connection.execute(
            """
            SELECT
                user_id,
                username,
                email,
                status,
                created_at,
                updated_at
            FROM users
            ORDER BY
                username,
                user_id
            """
        ).fetchall()

        role_map = {}

        if version >= 3:
            role_rows = connection.execute(
                """
                SELECT
                    user_id,
                    role
                FROM user_roles
                ORDER BY
                    user_id,
                    role
                """
            ).fetchall()

            for row in role_rows:
                role_map.setdefault(
                    row["user_id"],
                    [],
                ).append(
                    row["role"]
                )

        accounts = []

        for row in account_rows:
            account = _row_to_account(row)
            account["roles"] = list(
                role_map.get(
                    account["user_id"],
                    [],
                )
            )
            accounts.append(account)

        return accounts

    finally:
        connection.close()
        _secure_database_files(
            database_path
        )
