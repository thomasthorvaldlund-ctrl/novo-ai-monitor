"""Pure D006 normal-connection settings/schema-version contract.

This module performs no I/O and opens no SQLite database. It validates an
already-observed normal V3 connection state against an explicit schema
compatibility policy.

Passing this check is NOT full V3 database admission. The caller must also
compose the SQLite runtime-release guard, database/WAL/SHM permission checks,
and the future schema capability + migration-set/checksum verification before
granting canonical access.

D006 intentionally does not define a SQLite application_id. This module does
not invent one.
"""
from __future__ import annotations

from dataclasses import dataclass


CONNECTION_STATE_CONTRACT_VERSION = "opportunity_connection_state:v1"

READ_ONLY_ACCESS = "READ_ONLY"
CANONICAL_WRITE_ACCESS = "CANONICAL_WRITE"

EXPECTED_FOREIGN_KEYS = 1
EXPECTED_JOURNAL_MODE = "wal"
EXPECTED_BUSY_TIMEOUT_MS = 15000
EXPECTED_WRITE_SYNCHRONOUS = 2
KNOWN_SYNCHRONOUS_VALUES = frozenset({0, 1, 2, 3})
EXPECTED_READ_UNCOMMITTED = 0


class OpportunityDatabaseConnectionContractError(ValueError):
    """Observed connection state or explicit compatibility policy is invalid."""


def _require_exact_nonnegative_int(value: object, *, field: str) -> int:
    if type(value) is not int or value < 0:
        raise OpportunityDatabaseConnectionContractError(
            f"{field} must be a non-negative integer."
        )
    return value


def _require_schema_version(value: object, *, field: str) -> int:
    value = _require_exact_nonnegative_int(value, field=field)
    if value == 0:
        raise OpportunityDatabaseConnectionContractError(
            f"{field} must be a migrated schema version greater than zero."
        )
    return value


@dataclass(frozen=True, slots=True)
class SchemaCompatibilityPolicy:
    required_write_schema_version: int
    minimum_read_schema_version: int | None = None
    maximum_read_schema_version: int | None = None

    def __post_init__(self) -> None:
        required_write = _require_schema_version(
            self.required_write_schema_version,
            field="required_write_schema_version",
        )

        minimum_read = self.minimum_read_schema_version
        maximum_read = self.maximum_read_schema_version

        if minimum_read is None and maximum_read is None:
            return
        if minimum_read is None or maximum_read is None:
            raise OpportunityDatabaseConnectionContractError(
                "Read compatibility must declare both minimum and maximum "
                "schema versions or neither."
            )

        minimum_read = _require_schema_version(
            minimum_read,
            field="minimum_read_schema_version",
        )
        maximum_read = _require_schema_version(
            maximum_read,
            field="maximum_read_schema_version",
        )

        if minimum_read > maximum_read:
            raise OpportunityDatabaseConnectionContractError(
                "minimum_read_schema_version must not exceed "
                "maximum_read_schema_version."
            )
        if not minimum_read <= required_write <= maximum_read:
            raise OpportunityDatabaseConnectionContractError(
                "A declared read range must include the required write "
                "schema version."
            )


@dataclass(frozen=True, slots=True)
class ConnectionStateObservation:
    foreign_keys: int
    journal_mode: str
    busy_timeout_ms: int
    synchronous: int
    read_uncommitted: int
    row_mapping_is_unambiguous: bool
    user_version: int

    def __post_init__(self) -> None:
        _require_exact_nonnegative_int(self.foreign_keys, field="foreign_keys")
        if type(self.journal_mode) is not str or not self.journal_mode:
            raise OpportunityDatabaseConnectionContractError(
                "journal_mode must be a non-empty string."
            )
        _require_exact_nonnegative_int(
            self.busy_timeout_ms,
            field="busy_timeout_ms",
        )
        synchronous = _require_exact_nonnegative_int(
            self.synchronous,
            field="synchronous",
        )
        if synchronous not in KNOWN_SYNCHRONOUS_VALUES:
            raise OpportunityDatabaseConnectionContractError(
                "synchronous must be a recognized SQLite durability value."
            )
        _require_exact_nonnegative_int(
            self.read_uncommitted,
            field="read_uncommitted",
        )
        if type(self.row_mapping_is_unambiguous) is not bool:
            raise OpportunityDatabaseConnectionContractError(
                "row_mapping_is_unambiguous must be a boolean."
            )
        _require_exact_nonnegative_int(
            self.user_version,
            field="user_version",
        )


def assert_connection_settings_compatible(
    observation: ConnectionStateObservation,
    *,
    access_mode: str,
    schema_policy: SchemaCompatibilityPolicy,
) -> ConnectionStateObservation:
    """Fail closed on normal-connection settings or schema-version mismatch.

    This function deliberately does not inspect schema capabilities,
    schema_migrations, migration checksums, filesystem permissions, or the
    loaded SQLite library. Those are separate D006 admission layers.
    """
    if type(observation) is not ConnectionStateObservation:
        raise OpportunityDatabaseConnectionContractError(
            "observation must be exactly ConnectionStateObservation."
        )
    if type(schema_policy) is not SchemaCompatibilityPolicy:
        raise OpportunityDatabaseConnectionContractError(
            "schema_policy must be exactly SchemaCompatibilityPolicy."
        )
    if type(access_mode) is not str or access_mode not in {
        READ_ONLY_ACCESS,
        CANONICAL_WRITE_ACCESS,
    }:
        raise OpportunityDatabaseConnectionContractError(
            "access_mode must be READ_ONLY or CANONICAL_WRITE."
        )

    expected = (
        ("foreign_keys", observation.foreign_keys, EXPECTED_FOREIGN_KEYS),
        ("journal_mode", observation.journal_mode, EXPECTED_JOURNAL_MODE),
        ("busy_timeout_ms", observation.busy_timeout_ms, EXPECTED_BUSY_TIMEOUT_MS),
        ("read_uncommitted", observation.read_uncommitted, EXPECTED_READ_UNCOMMITTED),
        ("row_mapping_is_unambiguous", observation.row_mapping_is_unambiguous, True),
    )

    for field, actual, required in expected:
        if actual != required:
            raise OpportunityDatabaseConnectionContractError(
                f"{field} does not satisfy the locked normal-connection policy."
            )

    if access_mode == READ_ONLY_ACCESS:
        minimum_read = schema_policy.minimum_read_schema_version
        maximum_read = schema_policy.maximum_read_schema_version

        if minimum_read is None or maximum_read is None:
            raise OpportunityDatabaseConnectionContractError(
                "Read-only access requires an explicitly declared read range."
            )
        if not minimum_read <= observation.user_version <= maximum_read:
            raise OpportunityDatabaseConnectionContractError(
                "user_version is outside the explicitly declared read range."
            )
    else:
        if observation.synchronous != EXPECTED_WRITE_SYNCHRONOUS:
            raise OpportunityDatabaseConnectionContractError(
                "Canonical writes require synchronous FULL."
            )
        if observation.user_version != schema_policy.required_write_schema_version:
            raise OpportunityDatabaseConnectionContractError(
                "Canonical writes require the exact required write schema version."
            )

    return observation
