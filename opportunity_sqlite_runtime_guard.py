"""Non-serving WAL-reset release gate for the future D006 connection layer.

The gate checks the SQLite version loaded by THIS Python process against
upstream's documented fixed release branches. It opens no database and
changes no package, connection, journal mode or application configuration.

This is NOT binary provenance, schema compatibility, a general security
certification or permission to activate V3. A vendor backport with an older
version needs separate source/build verification; no override is provided.
SQLite's withdrawn 3.52 branch is deliberately excluded from this policy.

References:
https://www.sqlite.org/wal.html#walresetbug
https://www.sqlite.org/releaselog/3_51_3.html
https://www.sqlite.org/changes.html
"""
from __future__ import annotations

import sqlite3


SQLITE_WAL_RESET_RELEASE_POLICY = "sqlite_wal_reset_release:v1"


class OpportunitySQLiteRuntimeError(RuntimeError):
    """The loaded runtime does not satisfy this WAL-reset release gate."""


def _documented_fixed_release(version: object) -> bool:
    if (
        type(version) is not tuple
        or len(version) != 3
        or any(type(part) is not int or part < 0 for part in version)
    ):
        return False

    major, minor, patch = version
    if major != 3 or minor == 52:
        return False
    if minor == 44:
        return patch >= 6
    if minor == 50:
        return patch >= 7
    return version >= (3, 51, 3)


def require_sqlite_wal_reset_fix() -> tuple[int, int, int]:
    """Check the current process, not a CLI binary or caller-supplied version.

    A passing result only satisfies the documented-release check. All other
    D006 identity, permissions, connection and schema gates remain required.
    """
    version = sqlite3.sqlite_version_info
    if not _documented_fixed_release(version):
        raise OpportunitySQLiteRuntimeError(
            "Loaded SQLite does not meet the documented WAL-reset release "
            "policy. An older vendor backport requires separate build review; "
            "do not open or initialize the V3 database through this path."
        )
    return version
