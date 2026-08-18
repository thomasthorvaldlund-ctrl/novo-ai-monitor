"""
Read-only status for Deep AI-lagringsbroen.

Servicen ændrer aldrig SQLite eller JSON. Den viser, om
SQLite er primær, om JSON-fallback er aktiv, og om de to
lagre indeholder samme logiske Deep AI-state.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from aureum_paths import state_path
from deep_ai_database_service import (
    load_deep_ai_entitlement_records,
    load_deep_ai_selection_records,
)
from user_account_service import (
    AccountStoreError,
)


DEFAULT_ENTITLEMENTS_FILE = state_path(
    "deep_ai_entitlements.json"
)

DEFAULT_SELECTIONS_FILE = state_path(
    "deep_ai_selections.json"
)


def _selected_path(
    supplied,
    default,
):
    return (
        Path(supplied)
        if supplied is not None
        else default
    )


def _normalize_entitlement_records(
    records,
):
    if not isinstance(records, dict):
        raise ValueError(
            "Entitlement-records skal være et objekt."
        )

    normalized = {}

    for raw_user_id, raw_record in records.items():
        user_id = str(
            raw_user_id or ""
        ).strip().lower()

        if not user_id:
            raise ValueError(
                "Entitlement-bruger-id mangler."
            )

        if not isinstance(raw_record, dict):
            raise ValueError(
                "Entitlement-record skal være et objekt."
            )

        unlimited = raw_record.get(
            "unlimited",
            False,
        )

        if not isinstance(unlimited, bool):
            raise ValueError(
                "unlimited skal være true eller false."
            )

        normalized[user_id] = {
            "plan_code": str(
                raw_record.get(
                    "plan_code",
                    "free",
                )
            ).strip().lower(),
            "included_slots": int(
                raw_record.get(
                    "included_slots",
                    0,
                )
            ),
            "purchased_slots": int(
                raw_record.get(
                    "purchased_slots",
                    0,
                )
            ),
            "unlimited": unlimited,
        }

    return normalized


def _normalize_selection_records(
    records,
):
    if not isinstance(records, dict):
        raise ValueError(
            "Selection-records skal være et objekt."
        )

    normalized = {}

    for raw_user_id, raw_symbols in records.items():
        user_id = str(
            raw_user_id or ""
        ).strip().lower()

        if not user_id:
            raise ValueError(
                "Selection-bruger-id mangler."
            )

        if isinstance(
            raw_symbols,
            (str, bytes),
        ):
            raise ValueError(
                "Selection-symboler skal være en liste."
            )

        symbols = sorted({
            str(symbol or "").strip().upper()
            for symbol in raw_symbols
            if str(symbol or "").strip()
        })

        if symbols:
            normalized[user_id] = symbols

    return normalized


def _read_entitlement_json(path):
    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    if payload.get("version") != 1:
        raise ValueError(
            "Ukendt entitlement JSON-version."
        )

    return _normalize_entitlement_records(
        payload.get(
            "users",
            {},
        )
    )


def _read_selection_json(path):
    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    if payload.get("version") != 1:
        raise ValueError(
            "Ukendt selection JSON-version."
        )

    users = payload.get(
        "users",
        {},
    )

    if not isinstance(users, dict):
        raise ValueError(
            "Selection JSON-users skal være et objekt."
        )

    return _normalize_selection_records({
        user_id: (
            record.get(
                "selected_symbols",
                [],
            )
            if isinstance(record, dict)
            else []
        )
        for user_id, record in users.items()
    })


def _load_database_component(
    loader,
    normalizer,
    database_path,
):
    try:
        records = normalizer(
            loader(
                path=database_path
            )
        )

        return {
            "available": True,
            "records": records,
            "error": None,
        }

    except (
        AccountStoreError,
        OSError,
        RuntimeError,
        ValueError,
        sqlite3.Error,
    ) as error:
        return {
            "available": False,
            "records": {},
            "error": type(error).__name__,
        }


def _load_json_component(
    path,
    reader,
):
    if not path.exists():
        return {
            "available": False,
            "records": {},
            "error": "FileNotFoundError",
        }

    try:
        records = reader(path)

        return {
            "available": True,
            "records": records,
            "error": None,
        }

    except (
        OSError,
        RuntimeError,
        ValueError,
        json.JSONDecodeError,
    ) as error:
        return {
            "available": False,
            "records": {},
            "error": type(error).__name__,
        }


def _resolve_component(
    database,
    legacy,
):
    if database["available"]:
        if not legacy["available"]:
            source = "sqlite"
            synchronized = None
            records = database["records"]

        elif (
            database["records"]
            == legacy["records"]
        ):
            source = "sqlite"
            synchronized = True
            records = database["records"]

        else:
            source = "json"
            synchronized = False
            records = legacy["records"]

    elif legacy["available"]:
        source = "json"
        synchronized = None
        records = legacy["records"]

    else:
        source = "unavailable"
        synchronized = False
        records = {}

    return {
        "read_source": source,
        "synchronized": synchronized,
        "record_count": len(records),
        "database_available": database[
            "available"
        ],
        "json_available": legacy[
            "available"
        ],
        "database_record_count": len(
            database["records"]
        ),
        "json_record_count": len(
            legacy["records"]
        ),
        "database_error": database[
            "error"
        ],
        "json_error": legacy[
            "error"
        ],
    }


def get_deep_ai_storage_status(
    *,
    database_path=None,
    entitlements_file=None,
    selections_file=None,
):
    """
    Returnerer samlet read-only lagringsstatus.
    """
    entitlement_path = _selected_path(
        entitlements_file,
        DEFAULT_ENTITLEMENTS_FILE,
    )

    selection_path = _selected_path(
        selections_file,
        DEFAULT_SELECTIONS_FILE,
    )

    database_entitlements = (
        _load_database_component(
            load_deep_ai_entitlement_records,
            _normalize_entitlement_records,
            database_path,
        )
    )

    database_selections = (
        _load_database_component(
            load_deep_ai_selection_records,
            _normalize_selection_records,
            database_path,
        )
    )

    json_entitlements = (
        _load_json_component(
            entitlement_path,
            _read_entitlement_json,
        )
    )

    json_selections = (
        _load_json_component(
            selection_path,
            _read_selection_json,
        )
    )

    entitlements = _resolve_component(
        database_entitlements,
        json_entitlements,
    )

    selections = _resolve_component(
        database_selections,
        json_selections,
    )

    components = {
        "entitlements": entitlements,
        "selections": selections,
    }

    sources = {
        component["read_source"]
        for component in components.values()
    }

    if "unavailable" in sources:
        status = "unavailable"
        label = "Lagring utilgængelig"
        message = (
            "Hverken SQLite eller JSON-fallback "
            "kan levere alle Deep AI-data."
        )

    elif "json" in sources:
        status = "fallback"
        label = "JSON-fallback aktiv"
        message = (
            "Mindst én Deep AI-datatype læses "
            "midlertidigt fra JSON-fallback."
        )

    elif all(
        component["synchronized"] is True
        for component in components.values()
    ):
        status = "synchronized"
        label = "SQLite synkroniseret"
        message = (
            "SQLite er primær, og JSON-fallback "
            "er fuldt synkroniseret."
        )

    else:
        status = "database_only"
        label = "SQLite aktiv"
        message = (
            "SQLite er primær, men mindst én "
            "JSON-fallbackfil mangler."
        )

    return {
        "status": status,
        "label": label,
        "message": message,
        "primary_storage": "sqlite",
        "sqlite_primary": all(
            component["read_source"]
            == "sqlite"
            for component in components.values()
        ),
        "fallback_active": any(
            component["read_source"]
            == "json"
            for component in components.values()
        ),
        "json_fallback_ready": all(
            component["json_available"]
            for component in components.values()
        ),
        "components": components,
    }
