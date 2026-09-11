"""Pure D006 V3 runtime-file permission admission contract.

This module performs no filesystem I/O.  It validates an already-observed
permission state for the canonical database and any existing WAL/SHM sidecars.

The contract is deliberately narrow:
- it does not change file modes;
- it does not invent a UID/GID ownership requirement;
- it does not invent a symlink policy;
- passing it is NOT full V3 database admission.

D006 requires private runtime permissions with at least owner read/write
(mode 0600).  Existing WAL/SHM sidecars are checked when present.

For sidecars, mode None is admissible only when the matching
``*_absence_confirmed`` flag is true.  That flag means the collector
authoritatively confirmed absence; unknown or unobservable state must remain
unconfirmed and therefore fail permission admission.
"""
from __future__ import annotations

from dataclasses import dataclass


RUNTIME_PERMISSION_CONTRACT_VERSION = "opportunity_runtime_permissions:v1"

REQUIRED_OWNER_PERMISSION_BITS = 0o600
FORBIDDEN_GROUP_OTHER_PERMISSION_BITS = 0o077
MAX_SUPPORTED_PERMISSION_MODE = 0o7777


class OpportunityDatabasePermissionContractError(ValueError):
    """Observed V3 runtime-file permissions are not admissible."""


def _optional_permission_mode(value: object, *, field: str) -> int | None:
    if value is None:
        return None
    if (
        type(value) is not int
        or value < 0
        or value > MAX_SUPPORTED_PERMISSION_MODE
    ):
        raise OpportunityDatabasePermissionContractError(
            f"{field} must be None or Unix permission-mode bits "
            "between 0o0000 and 0o7777."
        )
    return value


def _require_exact_bool(value: object, *, field: str) -> bool:
    if type(value) is not bool:
        raise OpportunityDatabasePermissionContractError(
            f"{field} must be a boolean."
        )
    return value


@dataclass(frozen=True, slots=True)
class RuntimePermissionObservation:
    database_mode: int | None
    wal_mode: int | None = None
    shm_mode: int | None = None
    wal_absence_confirmed: bool = False
    shm_absence_confirmed: bool = False

    def __post_init__(self) -> None:
        _optional_permission_mode(
            self.database_mode,
            field="database_mode",
        )
        _optional_permission_mode(
            self.wal_mode,
            field="wal_mode",
        )
        _optional_permission_mode(
            self.shm_mode,
            field="shm_mode",
        )

        _require_exact_bool(
            self.wal_absence_confirmed,
            field="wal_absence_confirmed",
        )
        _require_exact_bool(
            self.shm_absence_confirmed,
            field="shm_absence_confirmed",
        )

        for field, mode, absence_confirmed in (
            (
                "wal_mode",
                self.wal_mode,
                self.wal_absence_confirmed,
            ),
            (
                "shm_mode",
                self.shm_mode,
                self.shm_absence_confirmed,
            ),
        ):
            if mode is not None and absence_confirmed:
                raise OpportunityDatabasePermissionContractError(
                    f"{field} cannot be present and confirmed absent."
                )


def _assert_private_mode(mode: int, *, field: str) -> None:
    if (
        mode & REQUIRED_OWNER_PERMISSION_BITS
        != REQUIRED_OWNER_PERMISSION_BITS
    ):
        raise OpportunityDatabasePermissionContractError(
            f"{field} must grant owner read/write permissions."
        )
    if mode & FORBIDDEN_GROUP_OTHER_PERMISSION_BITS:
        raise OpportunityDatabasePermissionContractError(
            f"{field} must not grant group/other permissions."
        )


def assert_runtime_permissions_compatible(
    observation: RuntimePermissionObservation,
) -> RuntimePermissionObservation:
    """Fail closed unless observed DB/WAL/SHM permissions satisfy D006."""
    if type(observation) is not RuntimePermissionObservation:
        raise OpportunityDatabasePermissionContractError(
            "observation must be exactly RuntimePermissionObservation."
        )

    if observation.database_mode is None:
        raise OpportunityDatabasePermissionContractError(
            "The canonical database must exist before permission admission."
        )

    _assert_private_mode(
        observation.database_mode,
        field="database_mode",
    )

    for field, mode, absence_confirmed in (
        (
            "wal_mode",
            observation.wal_mode,
            observation.wal_absence_confirmed,
        ),
        (
            "shm_mode",
            observation.shm_mode,
            observation.shm_absence_confirmed,
        ),
    ):
        if mode is None:
            if not absence_confirmed:
                raise OpportunityDatabasePermissionContractError(
                    f"{field} absence must be authoritatively confirmed."
                )
            continue

        _assert_private_mode(
            mode,
            field=field,
        )

    return observation
