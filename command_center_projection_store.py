"""
Atomic non-serving V3 Command Center projection store.

Slice 3 provides validation-before-publication, coherent atomic replacement,
scope checking, compare-and-swap publication and timestamp regression
protection.

There is intentionally no default production path, no route integration,
no dashboard-cache integration, no cron integration and no provider/OpenAI
work. Readers only read an already-published projection; they never create
locks, refresh data or rebuild projections.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import fcntl
import json
import os
from pathlib import Path
import tempfile
from collections.abc import Iterable, Mapping

from command_center_projection_contract import (
    ProjectionValidationError,
    assert_valid_command_center_projection,
)


class ProjectionStoreError(RuntimeError):
    pass


class ProjectionStoreConflictError(
    ProjectionStoreError
):
    pass


class ProjectionStoreIdentityConflictError(
    ProjectionStoreConflictError
):
    pass


class ProjectionStoreRegressionError(
    ProjectionStoreConflictError
):
    pass


class ProjectionStoreScopeMismatchError(
    ProjectionStoreError
):
    pass


class ProjectionStoreCorruptError(
    ProjectionStoreError
):
    pass


class ProjectionStoreSerializationError(
    ProjectionStoreError
):
    pass


class ProjectionStorePublicationAmbiguousError(
    ProjectionStoreError
):
    pass


def _parse_timestamp(value: str) -> datetime:
    text = value.strip()

    if text.endswith("Z"):
        text = text[:-1] + "+00:00"

    return datetime.fromisoformat(text)


def _expected_scope_dict(
    expected_scope: Mapping[str, object],
) -> dict[str, object]:
    if not isinstance(expected_scope, Mapping):
        raise TypeError(
            "expected_scope must be a mapping"
        )

    return deepcopy(dict(expected_scope))


def _assert_expected_scope(
    projection: Mapping[str, object],
    expected_scope: Mapping[str, object],
) -> None:
    actual = projection.get("scope")
    expected = _expected_scope_dict(
        expected_scope
    )

    if actual != expected:
        raise ProjectionStoreScopeMismatchError(
            "Projection scope does not match "
            "the caller's expected scope."
        )


def _serialize_candidate(
    projection: object,
    *,
    expected_scope: Mapping[str, object],
    required_sections: Iterable[str],
    required_source_sections: Iterable[str],
) -> tuple[dict[str, object], bytes]:
    """
    Validate the caller object, serialize it to canonical JSON,
    parse that exact reader-visible representation and validate again.
    """

    required_sections = tuple(
        required_sections
    )
    required_source_sections = tuple(
        required_source_sections
    )

    assert_valid_command_center_projection(
        projection,
        required_sections=required_sections,
        required_source_sections=(
            required_source_sections
        ),
    )

    _assert_expected_scope(
        projection,
        expected_scope,
    )

    try:
        text = json.dumps(
            projection,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ProjectionStoreSerializationError(
            "Projection is not safely JSON serializable."
        ) from exc

    text += "\n"

    normalized = json.loads(text)

    if normalized != projection:
        raise ProjectionStoreSerializationError(
            "Projection JSON serialization would "
            "change reader-visible projection data."
        )

    assert_valid_command_center_projection(
        normalized,
        required_sections=required_sections,
        required_source_sections=(
            required_source_sections
        ),
    )

    _assert_expected_scope(
        normalized,
        expected_scope,
    )

    return normalized, text.encode("utf-8")


def _load_unlocked(
    path: Path,
    *,
    expected_scope: Mapping[str, object],
    required_sections: Iterable[str] = (),
    required_source_sections: Iterable[str] = (),
) -> dict[str, object] | None:
    if not path.exists():
        return None

    try:
        text = path.read_text(
            encoding="utf-8"
        )
        projection = json.loads(text)
    except (
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ) as exc:
        raise ProjectionStoreCorruptError(
            "Published projection cannot be read safely."
        ) from exc

    try:
        assert_valid_command_center_projection(
            projection,
            required_sections=required_sections,
            required_source_sections=(
                required_source_sections
            ),
        )
    except ProjectionValidationError as exc:
        raise ProjectionStoreCorruptError(
            "Published projection violates "
            "the projection contract."
        ) from exc

    _assert_expected_scope(
        projection,
        expected_scope,
    )

    return deepcopy(projection)


def load_command_center_projection(
    path: Path | str,
    *,
    expected_scope: Mapping[str, object],
    required_sections: Iterable[str] = (),
    required_source_sections: Iterable[str] = (),
) -> dict[str, object] | None:
    """
    Read and validate one already-published projection.

    This read path creates no files, lock files, refresh jobs or other
    side effects.
    """

    return _load_unlocked(
        Path(path),
        expected_scope=expected_scope,
        required_sections=required_sections,
        required_source_sections=(
            required_source_sections
        ),
    )


def _publication_lock_path(
    path: Path,
) -> Path:
    return path.with_name(
        path.name + ".lock"
    )


def _open_publication_lock(
    path: Path,
):
    lock_path = _publication_lock_path(
        path
    )

    descriptor = os.open(
        lock_path,
        os.O_RDWR | os.O_CREAT,
        0o600,
    )

    try:
        os.fchmod(
            descriptor,
            0o600,
        )

        return os.fdopen(
            descriptor,
            "r+b",
        )
    except Exception:
        os.close(descriptor)
        raise


def _assert_publication_precondition(
    *,
    current: dict[str, object] | None,
    candidate: dict[str, object],
    expected_current_projection_id: str | None,
) -> bool:
    """
    Return True only for an exact idempotent re-publication.
    Otherwise validate CAS, immutable identity and no-regression.
    """

    if current is None:
        if expected_current_projection_id is not None:
            raise ProjectionStoreConflictError(
                "Expected an existing projection, "
                "but none is published."
            )

        return False

    current_id = current[
        "command_center_projection_id"
    ]

    if (
        expected_current_projection_id
        != current_id
    ):
        raise ProjectionStoreConflictError(
            "Published projection changed since "
            "the caller's expected version."
        )

    candidate_id = candidate[
        "command_center_projection_id"
    ]

    if candidate_id == current_id:
        if candidate == current:
            return True

        raise ProjectionStoreIdentityConflictError(
            "The same projection id cannot identify "
            "different projection content."
        )

    for field in (
        "materialized_at",
        "as_of",
        "source_cutoff",
    ):
        candidate_time = _parse_timestamp(
            candidate[field]
        )
        current_time = _parse_timestamp(
            current[field]
        )

        if candidate_time < current_time:
            raise ProjectionStoreRegressionError(
                f"Candidate {field} regresses behind "
                "the currently published projection."
            )

    return False


def _atomic_replace(
    path: Path,
    payload: bytes,
) -> None:
    parent = path.parent

    if (
        not parent.exists()
        or not parent.is_dir()
    ):
        raise FileNotFoundError(
            f"Projection directory does not exist: {parent}"
        )

    mode = 0o600

    descriptor, temporary_name = (
        tempfile.mkstemp(
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=parent,
        )
    )

    temporary_path = Path(
        temporary_name
    )

    descriptor_open = True

    try:
        os.fchmod(
            descriptor,
            mode,
        )

        with os.fdopen(
            descriptor,
            "wb",
        ) as handle:
            descriptor_open = False
            handle.write(payload)
            handle.flush()
            os.fsync(
                handle.fileno()
            )

        os.replace(
            temporary_path,
            path,
        )

        try:
            directory_descriptor = os.open(
                parent,
                os.O_RDONLY | os.O_DIRECTORY,
            )

            try:
                os.fsync(
                    directory_descriptor
                )
            finally:
                os.close(
                    directory_descriptor
                )

        except OSError as exc:
            raise (
                ProjectionStorePublicationAmbiguousError(
                    "Projection replacement succeeded, "
                    "but durable directory sync failed. "
                    "Re-read the published projection "
                    "before retrying."
                )
            ) from exc

    finally:
        if descriptor_open:
            os.close(descriptor)

        if temporary_path.exists():
            temporary_path.unlink()


def publish_command_center_projection(
    projection: object,
    path: Path | str,
    *,
    expected_scope: Mapping[str, object],
    expected_current_projection_id: str | None,
    required_sections: Iterable[str] = (),
    required_source_sections: Iterable[str] = (),
) -> dict[str, object]:
    """
    Validate and atomically publish one projection.

    Every publication requires an explicit compare-and-swap expectation:
    `None` means the caller expects no current publication; otherwise the
    supplied id must equal the currently published projection id.
    """

    target = Path(path)

    normalized, payload = (
        _serialize_candidate(
            projection,
            expected_scope=expected_scope,
            required_sections=required_sections,
            required_source_sections=(
                required_source_sections
            ),
        )
    )

    if (
        not target.parent.exists()
        or not target.parent.is_dir()
    ):
        raise FileNotFoundError(
            "Projection directory does not exist."
        )

    lock_handle = _open_publication_lock(
        target
    )

    try:
        fcntl.flock(
            lock_handle.fileno(),
            fcntl.LOCK_EX,
        )

        current = _load_unlocked(
            target,
            expected_scope=expected_scope,
        )

        idempotent = (
            _assert_publication_precondition(
                current=current,
                candidate=normalized,
                expected_current_projection_id=(
                    expected_current_projection_id
                ),
            )
        )

        if idempotent:
            return deepcopy(current)

        _atomic_replace(
            target,
            payload,
        )

        return deepcopy(normalized)

    finally:
        try:
            fcntl.flock(
                lock_handle.fileno(),
                fcntl.LOCK_UN,
            )
        finally:
            lock_handle.close()
