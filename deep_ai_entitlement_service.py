"""
Rettigheder og kvoter for personlige Deep AI-aktievalg.

Servicen er bevidst adskilt fra betaling. Et fremtidigt
abonnement eller Stripe-webhook skal kun opdatere brugerens
rettighedspost gennem denne service.
"""

from __future__ import annotations

import fcntl
import json
import os
import re
import tempfile
from contextlib import contextmanager

from aureum_paths import state_path


STATE_VERSION = 1

ENTITLEMENTS_FILE = state_path(
    "deep_ai_entitlements.json"
)

LOCK_FILE = state_path(
    "deep_ai_entitlements.lock"
)

DEFAULT_PLAN_CODE = "free"

_USER_ID_PATTERN = re.compile(
    r"[a-z0-9][a-z0-9_.-]{0,63}"
)

_PLAN_CODE_PATTERN = re.compile(
    r"[a-z0-9][a-z0-9_-]{0,31}"
)


def _default_entitlement():
    return {
        "plan_code": DEFAULT_PLAN_CODE,
        "included_slots": 0,
        "purchased_slots": 0,
        "unlimited": False,
    }


def _default_state():
    return {
        "version": STATE_VERSION,
        "users": {},
    }


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


def _validate_entitlement_record(record):
    if not isinstance(record, dict):
        raise RuntimeError(
            "Deep AI-entitlement skal være et objekt."
        )

    plan_code = _normalize_plan_code(
        record.get(
            "plan_code",
            DEFAULT_PLAN_CODE,
        )
    )

    included_slots = _validate_slot_count(
        record.get(
            "included_slots",
            0,
        ),
        "included_slots",
    )

    purchased_slots = _validate_slot_count(
        record.get(
            "purchased_slots",
            0,
        ),
        "purchased_slots",
    )

    unlimited = record.get(
        "unlimited",
        False,
    )

    if not isinstance(unlimited, bool):
        raise ValueError(
            "unlimited skal være true eller false."
        )

    return {
        "plan_code": plan_code,
        "included_slots": included_slots,
        "purchased_slots": purchased_slots,
        "unlimited": unlimited,
    }


def _validate_state(data):
    if not isinstance(data, dict):
        raise RuntimeError(
            "Deep AI-entitlement state "
            "skal være et objekt."
        )

    if data.get("version") != STATE_VERSION:
        raise RuntimeError(
            "Ukendt Deep AI-entitlement "
            "state-version."
        )

    users = data.get(
        "users",
        {},
    )

    if not isinstance(users, dict):
        raise RuntimeError(
            "Deep AI-entitlement users "
            "skal være et objekt."
        )

    validated_users = {}

    for raw_user_id, raw_record in users.items():
        user_id = _normalize_user_id(
            raw_user_id
        )

        if user_id != raw_user_id:
            raise RuntimeError(
                "Deep AI-entitlement bruger-id "
                "er ikke normaliseret."
            )

        validated_users[
            user_id
        ] = _validate_entitlement_record(
            raw_record
        )

    return {
        "version": STATE_VERSION,
        "users": validated_users,
    }


@contextmanager
def _state_lock(exclusive):
    LOCK_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    descriptor = os.open(
        LOCK_FILE,
        os.O_CREAT | os.O_RDWR,
        0o600,
    )

    try:
        os.chmod(
            LOCK_FILE,
            0o600,
        )

        operation = (
            fcntl.LOCK_EX
            if exclusive
            else fcntl.LOCK_SH
        )

        fcntl.flock(
            descriptor,
            operation,
        )

        yield

    finally:
        fcntl.flock(
            descriptor,
            fcntl.LOCK_UN,
        )

        os.close(
            descriptor
        )


def _read_state_unlocked():
    if not ENTITLEMENTS_FILE.exists():
        return _default_state()

    try:
        with ENTITLEMENTS_FILE.open(
            "r",
            encoding="utf-8",
        ) as handle:
            data = json.load(
                handle
            )

    except (
        OSError,
        json.JSONDecodeError,
    ) as error:
        raise RuntimeError(
            "Deep AI-entitlement state "
            "kunne ikke læses."
        ) from error

    return _validate_state(
        data
    )


def _write_state_unlocked(data):
    validated = _validate_state(
        data
    )

    ENTITLEMENTS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    descriptor, temporary_name = (
        tempfile.mkstemp(
            prefix=(
                f".{ENTITLEMENTS_FILE.name}."
            ),
            suffix=".tmp",
            dir=ENTITLEMENTS_FILE.parent,
        )
    )

    temporary_path = type(
        ENTITLEMENTS_FILE
    )(
        temporary_name
    )

    try:
        os.chmod(
            temporary_path,
            0o600,
        )

        with os.fdopen(
            descriptor,
            "w",
            encoding="utf-8",
        ) as handle:
            json.dump(
                validated,
                handle,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )

            handle.write(
                "\n"
            )

            handle.flush()
            os.fsync(
                handle.fileno()
            )

        os.replace(
            temporary_path,
            ENTITLEMENTS_FILE,
        )

        os.chmod(
            ENTITLEMENTS_FILE,
            0o600,
        )

        directory_descriptor = os.open(
            ENTITLEMENTS_FILE.parent,
            os.O_RDONLY,
        )

        try:
            os.fsync(
                directory_descriptor
            )
        finally:
            os.close(
                directory_descriptor
            )

    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def load_deep_ai_entitlements():
    """
    Læser entitlement-state uden at ændre den.
    """
    with _state_lock(
        exclusive=False
    ):
        return _read_state_unlocked()


def set_user_deep_ai_entitlement(
    user_id,
    *,
    plan_code,
    included_slots,
    purchased_slots=0,
    unlimited=False,
):
    """
    Opretter eller erstatter én brugers rettigheder.
    """
    normalized_user_id = (
        _normalize_user_id(
            user_id
        )
    )

    record = _validate_entitlement_record({
        "plan_code": plan_code,
        "included_slots": included_slots,
        "purchased_slots": purchased_slots,
        "unlimited": unlimited,
    })

    with _state_lock(
        exclusive=True
    ):
        state = _read_state_unlocked()

        state["users"][
            normalized_user_id
        ] = record

        _write_state_unlocked(
            state
        )

    return get_user_deep_ai_entitlement(
        normalized_user_id
    )


def get_user_deep_ai_entitlement(
    user_id,
):
    """
    Returnerer brugerens effektive plan og kvote.
    """
    normalized_user_id = (
        _normalize_user_id(
            user_id
        )
    )

    state = load_deep_ai_entitlements()

    record = dict(
        state["users"].get(
            normalized_user_id,
            _default_entitlement(),
        )
    )

    selection_limit = (
        None
        if record["unlimited"]
        else (
            record["included_slots"]
            + record["purchased_slots"]
        )
    )

    return {
        "user_id": normalized_user_id,
        **record,
        "selection_limit": selection_limit,
    }


def get_user_deep_ai_usage(
    user_id,
    selected_count,
):
    """
    Sammenholder brugerens kvote med aktuelle tilvalg.
    """
    selected_count = _validate_slot_count(
        selected_count,
        "selected_count",
    )

    entitlement = (
        get_user_deep_ai_entitlement(
            user_id
        )
    )

    selection_limit = entitlement[
        "selection_limit"
    ]

    remaining_slots = (
        None
        if selection_limit is None
        else max(
            selection_limit
            - selected_count,
            0,
        )
    )

    return {
        **entitlement,
        "selected_count": selected_count,
        "remaining_slots": remaining_slots,
        "within_limit": (
            selection_limit is None
            or selected_count
            <= selection_limit
        ),
        "can_add": (
            selection_limit is None
            or selected_count
            < selection_limit
        ),
    }


def validate_user_deep_ai_selection_count(
    user_id,
    selected_count,
):
    """
    Afviser et valg, hvis brugerens kvote overskrides.
    """
    usage = get_user_deep_ai_usage(
        user_id,
        selected_count,
    )

    if not usage["within_limit"]:
        raise ValueError(
            "Antallet af personlige Deep AI-aktier "
            "overskrider brugerens tilgængelige kvote."
        )

    return usage
