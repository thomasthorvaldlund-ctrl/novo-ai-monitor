"""
Central filesystem-konfiguration for Aureum AI.

Standardværdierne matcher den nuværende produktion præcist.
De kan senere overskrives via miljøvariabler uden at ændre
forbrugende kode.
"""

from __future__ import annotations

import os
from pathlib import Path


DEFAULT_PROJECT_DIR = Path(
    "/root/aureum-ai-platform"
)


def _environment_path(
    variable_name: str,
    default: Path,
) -> Path:
    """
    Returnerer en absolut Path fra environment eller default.

    Funktionen opretter ingen mapper og ændrer ingen filer.
    """

    raw_value = os.getenv(
        variable_name,
        "",
    ).strip()

    path = (
        Path(raw_value).expanduser()
        if raw_value
        else default
    )

    if not path.is_absolute():
        raise RuntimeError(
            f"{variable_name} skal være en absolut sti: "
            f"{path}"
        )

    return path


PROJECT_DIR = _environment_path(
    "AUREUM_PROJECT_DIR",
    DEFAULT_PROJECT_DIR,
)

DATA_DIR = _environment_path(
    "AUREUM_DATA_DIR",
    PROJECT_DIR,
)

STATE_DIR = _environment_path(
    "AUREUM_STATE_DIR",
    DATA_DIR,
)

CACHE_DIR = _environment_path(
    "AUREUM_CACHE_DIR",
    DATA_DIR,
)

LOG_DIR = _environment_path(
    "AUREUM_LOG_DIR",
    PROJECT_DIR,
)


def project_path(*parts: str) -> Path:
    return PROJECT_DIR.joinpath(*parts)


def data_path(*parts: str) -> Path:
    return DATA_DIR.joinpath(*parts)


def state_path(*parts: str) -> Path:
    return STATE_DIR.joinpath(*parts)


def cache_path(*parts: str) -> Path:
    return CACHE_DIR.joinpath(*parts)


def log_path(*parts: str) -> Path:
    return LOG_DIR.joinpath(*parts)
