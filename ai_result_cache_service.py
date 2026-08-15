from __future__ import annotations

import copy
import fcntl
import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any

from aureum_paths import cache_path


AI_RESULT_CACHE_FILE = cache_path(
    "ai_result_cache.json"
)

AI_RESULT_CACHE_LOCK_FILE = cache_path(
    "ai_result_cache.lock"
)

CACHE_SCHEMA_VERSION = 1

DEFAULT_MAX_ENTRIES_PER_NAMESPACE = 256


def _utc_now() -> datetime:
    return datetime.now(
        timezone.utc
    )


def _canonical_json(
    value: Any,
) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def build_ai_input_fingerprint(
    input_payload: Any,
) -> str:
    canonical = _canonical_json(
        input_payload
    )

    return hashlib.sha256(
        canonical.encode(
            "utf-8"
        )
    ).hexdigest()


def _required_text(
    name: str,
    value: str,
) -> str:
    if (
        not isinstance(
            value,
            str,
        )
        or not value.strip()
    ):
        raise ValueError(
            f"{name} skal være en ikke-tom tekstværdi."
        )

    return value.strip()


def _namespace_dimensions(
    *,
    service: str,
    operation: str,
    model: str,
    prompt_contract_version: str,
) -> dict:
    return {
        "service":
            _required_text(
                "service",
                service,
            ),

        "operation":
            _required_text(
                "operation",
                operation,
            ),

        "model":
            _required_text(
                "model",
                model,
            ),

        "prompt_contract_version":
            _required_text(
                "prompt_contract_version",
                prompt_contract_version,
            ),
    }


def _namespace_key(
    dimensions: dict,
) -> str:
    return hashlib.sha256(
        _canonical_json(
            dimensions
        ).encode(
            "utf-8"
        )
    ).hexdigest()


def _empty_cache() -> dict:
    return {
        "schema_version":
            CACHE_SCHEMA_VERSION,

        "namespaces":
            {},
    }


def _ensure_parent_dirs() -> None:
    AI_RESULT_CACHE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    AI_RESULT_CACHE_LOCK_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


def _open_lock_file():
    _ensure_parent_dirs()

    fd = os.open(
        AI_RESULT_CACHE_LOCK_FILE,
        os.O_RDWR
        | os.O_CREAT,
        0o600,
    )

    os.chmod(
        AI_RESULT_CACHE_LOCK_FILE,
        0o600,
    )

    return os.fdopen(
        fd,
        "r+",
        encoding="utf-8",
    )


def _read_cache_unlocked() -> dict:
    if not AI_RESULT_CACHE_FILE.exists():
        return _empty_cache()

    try:
        with open(
            AI_RESULT_CACHE_FILE,
            "r",
            encoding="utf-8",
        ) as handle:
            data = json.load(
                handle
            )

    except (
        OSError,
        json.JSONDecodeError,
    ):
        return _empty_cache()

    if not isinstance(
        data,
        dict,
    ):
        return _empty_cache()

    if (
        data.get(
            "schema_version"
        )
        != CACHE_SCHEMA_VERSION
    ):
        return _empty_cache()

    if not isinstance(
        data.get(
            "namespaces"
        ),
        dict,
    ):
        return _empty_cache()

    return data


def _write_cache_unlocked(
    data: dict,
) -> None:
    _ensure_parent_dirs()

    temp_file = (
        AI_RESULT_CACHE_FILE.with_suffix(
            AI_RESULT_CACHE_FILE.suffix
            + ".tmp"
        )
    )

    fd = os.open(
        temp_file,
        os.O_WRONLY
        | os.O_CREAT
        | os.O_TRUNC,
        0o600,
    )

    try:
        with os.fdopen(
            fd,
            "w",
            encoding="utf-8",
        ) as handle:
            json.dump(
                data,
                handle,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
                allow_nan=False,
            )

            handle.flush()

            os.fsync(
                handle.fileno()
            )

    except BaseException:

        try:
            temp_file.unlink(
                missing_ok=True
            )

        finally:
            raise

    os.chmod(
        temp_file,
        0o600,
    )

    temp_file.replace(
        AI_RESULT_CACHE_FILE
    )

    os.chmod(
        AI_RESULT_CACHE_FILE,
        0o600,
    )


def _parse_created_at(
    value,
):
    if not isinstance(
        value,
        str,
    ):
        return None

    try:
        parsed = datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00",
            )
        )

    except ValueError:
        return None

    if parsed.tzinfo is None:
        return None

    return parsed.astimezone(
        timezone.utc
    )


def _validate_max_age(
    max_age_seconds,
):
    if max_age_seconds is None:
        return None

    if (
        isinstance(
            max_age_seconds,
            bool,
        )
        or not isinstance(
            max_age_seconds,
            (int, float),
        )
        or max_age_seconds < 0
    ):
        raise ValueError(
            "max_age_seconds skal være None "
            "eller et ikke-negativt tal."
        )

    return float(
        max_age_seconds
    )


def get_cached_ai_result(
    *,
    service: str,
    operation: str,
    model: str,
    prompt_contract_version: str,
    input_payload: Any,
    max_age_seconds=None,
):
    dimensions = (
        _namespace_dimensions(
            service=service,
            operation=operation,
            model=model,
            prompt_contract_version=(
                prompt_contract_version
            ),
        )
    )

    fingerprint = (
        build_ai_input_fingerprint(
            input_payload
        )
    )

    namespace_key = (
        _namespace_key(
            dimensions
        )
    )

    max_age = (
        _validate_max_age(
            max_age_seconds
        )
    )

    with _open_lock_file() as lock:

        fcntl.flock(
            lock.fileno(),
            fcntl.LOCK_SH,
        )

        try:
            data = (
                _read_cache_unlocked()
            )

            namespace = (
                data[
                    "namespaces"
                ].get(
                    namespace_key
                )
            )

            if not isinstance(
                namespace,
                dict,
            ):
                return None

            for key, expected in (
                dimensions.items()
            ):
                if (
                    namespace.get(
                        key
                    )
                    != expected
                ):
                    return None

            entries = namespace.get(
                "entries"
            )

            if not isinstance(
                entries,
                dict,
            ):
                return None

            entry = entries.get(
                fingerprint
            )

            if not isinstance(
                entry,
                dict,
            ):
                return None

            if (
                entry.get(
                    "fingerprint"
                )
                != fingerprint
            ):
                return None

            if "result" not in entry:
                return None

            if max_age is not None:

                created_at = (
                    _parse_created_at(
                        entry.get(
                            "created_at"
                        )
                    )
                )

                if created_at is None:
                    return None

                age_seconds = max(
                    0.0,
                    (
                        _utc_now()
                        - created_at
                    ).total_seconds(),
                )

                if (
                    age_seconds
                    > max_age
                ):
                    return None

            return copy.deepcopy(
                entry[
                    "result"
                ]
            )

        finally:
            fcntl.flock(
                lock.fileno(),
                fcntl.LOCK_UN,
            )


def get_latest_cached_ai_result(
    *,
    service: str,
    operation: str,
    model: str,
    prompt_contract_version: str,
    max_age_seconds=None,
):
    """
    Returnerer det nyeste gyldige resultat i et AI-cache namespace.

    Lookup er uafhængigt af input-fingerprint og bruges derfor kun,
    når en caller bevidst ønsker en bounded refresh-policy.

    Rå AI-inputs læses eller returneres ikke.
    """
    dimensions = (
        _namespace_dimensions(
            service=service,
            operation=operation,
            model=model,
            prompt_contract_version=(
                prompt_contract_version
            ),
        )
    )

    namespace_key = (
        _namespace_key(
            dimensions
        )
    )

    max_age = (
        _validate_max_age(
            max_age_seconds
        )
    )

    with _open_lock_file() as lock:

        fcntl.flock(
            lock.fileno(),
            fcntl.LOCK_SH,
        )

        try:
            data = (
                _read_cache_unlocked()
            )

            namespace = (
                data[
                    "namespaces"
                ].get(
                    namespace_key
                )
            )

            if not isinstance(
                namespace,
                dict,
            ):
                return None

            for key, expected in (
                dimensions.items()
            ):
                if (
                    namespace.get(
                        key
                    )
                    != expected
                ):
                    return None

            entries = namespace.get(
                "entries"
            )

            if not isinstance(
                entries,
                dict,
            ):
                return None

            candidates = []

            for fingerprint, entry in (
                entries.items()
            ):
                if not isinstance(
                    entry,
                    dict,
                ):
                    continue

                if (
                    entry.get(
                        "fingerprint"
                    )
                    != fingerprint
                ):
                    continue

                if "result" not in entry:
                    continue

                created_at = (
                    _parse_created_at(
                        entry.get(
                            "created_at"
                        )
                    )
                )

                if created_at is None:
                    continue

                if max_age is not None:

                    age_seconds = max(
                        0.0,
                        (
                            _utc_now()
                            - created_at
                        ).total_seconds(),
                    )

                    if (
                        age_seconds
                        > max_age
                    ):
                        continue

                candidates.append(
                    (
                        created_at,
                        fingerprint,
                        entry[
                            "result"
                        ],
                    )
                )

            if not candidates:
                return None

            latest = max(
                candidates,
                key=lambda item:
                    (
                        item[0],
                        item[1],
                    ),
            )

            return copy.deepcopy(
                latest[
                    2
                ]
            )

        finally:
            fcntl.flock(
                lock.fileno(),
                fcntl.LOCK_UN,
            )


def save_cached_ai_result(
    *,
    service: str,
    operation: str,
    model: str,
    prompt_contract_version: str,
    input_payload: Any,
    result: Any,
    max_entries_per_namespace: int = (
        DEFAULT_MAX_ENTRIES_PER_NAMESPACE
    ),
) -> str:
    if result is None:
        raise ValueError(
            "result må ikke være None."
        )

    if (
        isinstance(
            max_entries_per_namespace,
            bool,
        )
        or not isinstance(
            max_entries_per_namespace,
            int,
        )
        or max_entries_per_namespace < 1
    ):
        raise ValueError(
            "max_entries_per_namespace skal være "
            "et positivt heltal."
        )

    _canonical_json(
        result
    )

    dimensions = (
        _namespace_dimensions(
            service=service,
            operation=operation,
            model=model,
            prompt_contract_version=(
                prompt_contract_version
            ),
        )
    )

    fingerprint = (
        build_ai_input_fingerprint(
            input_payload
        )
    )

    namespace_key = (
        _namespace_key(
            dimensions
        )
    )

    created_at = (
        _utc_now()
        .astimezone(
            timezone.utc
        )
        .isoformat()
    )

    with _open_lock_file() as lock:

        fcntl.flock(
            lock.fileno(),
            fcntl.LOCK_EX,
        )

        try:
            data = (
                _read_cache_unlocked()
            )

            namespaces = data[
                "namespaces"
            ]

            namespace = (
                namespaces.get(
                    namespace_key
                )
            )

            if not isinstance(
                namespace,
                dict,
            ):
                namespace = {
                    **dimensions,
                    "entries": {},
                }

                namespaces[
                    namespace_key
                ] = namespace

            else:
                mismatch = any(
                    namespace.get(
                        key
                    )
                    != expected

                    for key, expected
                    in dimensions.items()
                )

                if mismatch:
                    namespace = {
                        **dimensions,
                        "entries": {},
                    }

                    namespaces[
                        namespace_key
                    ] = namespace

            entries = namespace.get(
                "entries"
            )

            if not isinstance(
                entries,
                dict,
            ):
                entries = {}

                namespace[
                    "entries"
                ] = entries

            entries[
                fingerprint
            ] = {
                "fingerprint":
                    fingerprint,

                "created_at":
                    created_at,

                "result":
                    copy.deepcopy(
                        result
                    ),
            }

            if (
                len(
                    entries
                )
                > max_entries_per_namespace
            ):
                newest = sorted(
                    entries.items(),
                    key=lambda item:
                        (
                            item[1].get(
                                "created_at",
                                "",
                            )
                            if isinstance(
                                item[1],
                                dict,
                            )
                            else ""
                        ),
                    reverse=True,
                )

                namespace[
                    "entries"
                ] = dict(
                    newest[
                        :max_entries_per_namespace
                    ]
                )

            _write_cache_unlocked(
                data
            )

        finally:
            fcntl.flock(
                lock.fileno(),
                fcntl.LOCK_UN,
            )

    return fingerprint
