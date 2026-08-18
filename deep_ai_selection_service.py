"""
Brugerspecifikke Deep AI-tilvalg.

Den fælles Deep AI-kerne ligger fortsat i stock_universe.csv.
Denne service gemmer kun personlige tilvalg. Abonnements- og
betalingsrettigheder tilføjes senere i en separat service.
"""

from __future__ import annotations

import fcntl
import json
import os
import re
import tempfile
from contextlib import contextmanager
from pathlib import Path

from aureum_paths import state_path
from deep_ai_entitlement_service import (
    validate_user_deep_ai_selection_count,
)
from stock_universe_service import (
    get_active_stocks,
    get_deep_ai_stocks,
)


STATE_VERSION = 1

SELECTIONS_FILE = state_path(
    "deep_ai_selections.json"
)

LOCK_FILE = state_path(
    "deep_ai_selections.lock"
)

_USER_ID_PATTERN = re.compile(
    r"[a-z0-9][a-z0-9_.-]{0,63}"
)


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

    active_stocks = get_active_stocks()

    invalid = [
        symbol
        for symbol in normalized
        if symbol not in active_stocks
    ]

    if invalid:
        raise ValueError(
            "Ukendte eller inaktive Deep AI-symboler: "
            + ", ".join(invalid)
        )

    core_symbols = set(
        get_deep_ai_stocks()
    )

    redundant_core_symbols = [
        symbol
        for symbol in normalized
        if symbol in core_symbols
    ]

    if redundant_core_symbols:
        raise ValueError(
            "Faste Deep AI-aktier skal ikke "
            "gemmes som personlige tilvalg: "
            + ", ".join(
                redundant_core_symbols
            )
        )

    return normalized


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


def _validate_state(data):
    if not isinstance(
        data,
        dict,
    ):
        raise RuntimeError(
            "Deep AI-selection state skal være et objekt."
        )

    if data.get("version") != STATE_VERSION:
        raise RuntimeError(
            "Ukendt Deep AI-selection state-version."
        )

    users = data.get(
        "users",
        {},
    )

    if not isinstance(
        users,
        dict,
    ):
        raise RuntimeError(
            "Deep AI-selection users skal være et objekt."
        )

    validated_users = {}

    for raw_user_id, raw_record in users.items():
        user_id = _normalize_user_id(
            raw_user_id
        )

        if user_id != raw_user_id:
            raise RuntimeError(
                "Deep AI-bruger-id er ikke normaliseret: "
                f"{raw_user_id!r}"
            )

        if not isinstance(
            raw_record,
            dict,
        ):
            raise RuntimeError(
                "Deep AI-brugerpost skal være et objekt."
            )

        raw_symbols = raw_record.get(
            "selected_symbols",
            [],
        )

        if not isinstance(
            raw_symbols,
            list,
        ):
            raise RuntimeError(
                "selected_symbols skal være en liste."
            )

        normalized_symbols = (
            _normalize_symbols(
                raw_symbols
            )
        )

        if normalized_symbols != raw_symbols:
            raise RuntimeError(
                "selected_symbols er ikke "
                f"normaliseret for {user_id}."
            )

        validated_record = dict(
            raw_record
        )

        validated_record[
            "selected_symbols"
        ] = normalized_symbols

        validated_users[
            user_id
        ] = validated_record

    return {
        "version": STATE_VERSION,
        "users": validated_users,
    }


def _read_state_unlocked():
    if not SELECTIONS_FILE.exists():
        return _default_state()

    try:
        with SELECTIONS_FILE.open(
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
            "Deep AI-selection state "
            "kunne ikke læses."
        ) from error

    return _validate_state(
        data
    )


def _write_state_unlocked(data):
    validated = _validate_state(
        data
    )

    SELECTIONS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    descriptor, temporary_name = (
        tempfile.mkstemp(
            prefix=(
                f".{SELECTIONS_FILE.name}."
            ),
            suffix=".tmp",
            dir=SELECTIONS_FILE.parent,
        )
    )

    temporary_path = Path(
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
            SELECTIONS_FILE,
        )

        os.chmod(
            SELECTIONS_FILE,
            0o600,
        )

        directory_descriptor = os.open(
            SELECTIONS_FILE.parent,
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


def load_deep_ai_selections():
    """
    Læser selection-state uden at ændre den.
    """
    with _state_lock(
        exclusive=False
    ):
        return _read_state_unlocked()


def set_user_deep_ai_selections(
    user_id,
    symbols,
):
    """
    Erstatter én brugers personlige Deep AI-tilvalg.
    """
    normalized_user_id = (
        _normalize_user_id(
            user_id
        )
    )

    normalized_symbols = (
        _normalize_symbols(
            symbols
        )
    )

    validate_user_deep_ai_selection_count(
        normalized_user_id,
        len(normalized_symbols),
    )

    with _state_lock(
        exclusive=True
    ):
        state = _read_state_unlocked()

        existing_record = dict(
            state["users"].get(
                normalized_user_id,
                {},
            )
        )

        existing_record[
            "selected_symbols"
        ] = normalized_symbols

        state["users"][
            normalized_user_id
        ] = existing_record

        _write_state_unlocked(
            state
        )

    return {
        "user_id": normalized_user_id,
        "selected_symbols": normalized_symbols,
    }


def get_user_selected_deep_ai_stocks(
    user_id,
):
    """
    Returnerer én brugers personlige tilvalg.
    """
    normalized_user_id = (
        _normalize_user_id(
            user_id
        )
    )

    state = load_deep_ai_selections()

    symbols = state["users"].get(
        normalized_user_id,
        {},
    ).get(
        "selected_symbols",
        [],
    )

    active_stocks = get_active_stocks()

    return {
        symbol: active_stocks[symbol]
        for symbol in symbols
    }


def _selected_user_ids(
    state,
    user_ids,
):
    if user_ids is None:
        return sorted(
            state["users"]
        )

    if isinstance(
        user_ids,
        (str, bytes),
    ):
        user_ids = [
            user_ids
        ]

    return sorted({
        _normalize_user_id(
            user_id
        )
        for user_id in user_ids
    })


def get_effective_deep_ai_stocks(
    user_ids=None,
):
    """
    Returnerer fælles kerne plus valgte brugeres tilvalg.

    user_ids=None anvendes af baggrundsjobbet og giver
    unionen af alle personlige tilvalg. Dermed bliver samme
    aktie kun analyseret én gang.
    """
    state = load_deep_ai_selections()

    effective = dict(
        get_deep_ai_stocks()
    )

    active_stocks = get_active_stocks()

    for user_id in _selected_user_ids(
        state,
        user_ids,
    ):
        symbols = state["users"].get(
            user_id,
            {},
        ).get(
            "selected_symbols",
            [],
        )

        for symbol in symbols:
            effective[
                symbol
            ] = active_stocks[
                symbol
            ]

    return effective


def get_deep_ai_selection_sources(
    user_ids=None,
):
    """
    Forklarer om en aktie kommer fra kernen
    eller fra et personligt valg.
    """
    state = load_deep_ai_selections()

    sources = {
        symbol: {
            "ticker": ticker,
            "core": True,
            "selected_by": [],
        }
        for symbol, ticker
        in get_deep_ai_stocks().items()
    }

    active_stocks = get_active_stocks()

    for user_id in _selected_user_ids(
        state,
        user_ids,
    ):
        symbols = state["users"].get(
            user_id,
            {},
        ).get(
            "selected_symbols",
            [],
        )

        for symbol in symbols:
            item = sources.setdefault(
                symbol,
                {
                    "ticker": (
                        active_stocks[
                            symbol
                        ]
                    ),
                    "core": False,
                    "selected_by": [],
                },
            )

            item["selected_by"].append(
                user_id
            )

    return sources
