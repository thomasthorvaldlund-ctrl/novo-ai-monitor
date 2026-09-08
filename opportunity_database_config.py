"""D006.1 path selection for the separate canonical V3 SQLite database.

This module selects a path only. It does not open or create a database,
inspect file identity or permissions, establish WAL, migrate a schema,
resolve an opportunity, or change account/production configuration.

Only an absent AUREUM_V3_DB_PATH selects the state_path default. An explicit
empty, invalid or relative override is a configuration error, not fallback.
"""
from __future__ import annotations

from collections.abc import Mapping
import os
from pathlib import Path

from aureum_paths import state_path


V3_DATABASE_FILENAME = "aureum_v3.sqlite3"
V3_DATABASE_PATH_ENV = "AUREUM_V3_DB_PATH"


class OpportunityDatabaseConfigurationError(ValueError):
    """The selected V3 database path configuration is invalid."""


def _absolute_file_path(value: object, *, source: str) -> Path:
    if not isinstance(value, (str, Path)):
        raise OpportunityDatabaseConfigurationError(
            f"{source} must provide a string or Path"
        )
    raw = str(value)
    if not raw.strip() or "\x00" in raw:
        raise OpportunityDatabaseConfigurationError(
            f"{source} must provide a non-empty path without NUL"
        )
    path = Path(raw)
    if not path.is_absolute() or not path.name:
        raise OpportunityDatabaseConfigurationError(
            f"{source} must provide an absolute file path"
        )
    return path


def resolve_opportunity_database_path(
    *, environ: Mapping[str, str] | None = None,
) -> Path:
    """Resolve the D006.1 path without filesystem access or silent fallback."""
    environment = os.environ if environ is None else environ
    if not isinstance(environment, Mapping):
        raise OpportunityDatabaseConfigurationError("environ must be a mapping")
    if V3_DATABASE_PATH_ENV in environment:
        raw = environment[V3_DATABASE_PATH_ENV]
        if not isinstance(raw, str):
            raise OpportunityDatabaseConfigurationError(
                f"{V3_DATABASE_PATH_ENV} must be a string"
            )
        return _absolute_file_path(raw, source=V3_DATABASE_PATH_ENV)
    return _absolute_file_path(
        state_path(V3_DATABASE_FILENAME), source="state_path default"
    )
