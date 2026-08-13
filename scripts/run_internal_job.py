#!/usr/bin/env python3
"""
Aureum AI internal job client.

Kalder et godkendt lokalt jobendpoint med det interne jobtoken.
Tokenet læses fra /etc/aureum-ai.env og placeres aldrig i
crontab eller i programmets kommandolinjeargumenter.
"""

from __future__ import annotations

import argparse
import hashlib
import http.client
import os
import stat
import sys
from pathlib import Path


ENV_PATH = Path("/etc/aureum-ai.env")

TOKEN_ENV_NAME = "AUREUM_INTERNAL_JOB_TOKEN"
TOKEN_HEADER_NAME = "X-Aureum-Job-Token"

HOST = "127.0.0.1"
PORT = 3000
REQUEST_TIMEOUT_SECONDS = 300

ALLOWED_JOB_PATHS = frozenset({
    "/risk-check",
    "/news-check",
    "/ai-news-check",
    "/status-report",
    "/daily-report",
    "/smart-alerts",
    "/save-history",
    "/portfolio-alerts",
    "/combined-stock-score",
    "/combined-stock-score-report",
    "/update-dashboard-cache",
    "/update-stock-news-ai-cache",
    "/update-stock-screener-cache",
})


class JobClientError(RuntimeError):
    """Kontrolleret fejl i den interne jobklient."""


def load_job_token() -> str:
    """
    Henter præcis én ikke-tom tokenværdi fra miljøfilen.
    """

    if not ENV_PATH.is_file():
        raise JobClientError(
            f"Miljøfilen findes ikke: {ENV_PATH}"
        )

    file_stat = ENV_PATH.stat()
    permissions = stat.S_IMODE(file_stat.st_mode)

    if file_stat.st_uid != 0 or file_stat.st_gid != 0:
        raise JobClientError(
            "Miljøfilen skal være ejet af root:root."
        )

    if permissions & 0o077:
        raise JobClientError(
            "Miljøfilen må ikke være læsbar for "
            "gruppe eller andre."
        )

    matches: list[str] = []

    for raw_line in ENV_PATH.read_text(
        encoding="utf-8"
    ).splitlines():
        line = raw_line.strip()

        if (
            not line
            or line.startswith("#")
            or "=" not in line
        ):
            continue

        key, value = line.split("=", 1)

        if key.strip() == TOKEN_ENV_NAME:
            matches.append(value.strip())

    if len(matches) != 1:
        raise JobClientError(
            f"Forventede præcis én {TOKEN_ENV_NAME}, "
            f"men fandt {len(matches)}."
        )

    token = matches[0]

    if not token:
        raise JobClientError(
            f"{TOKEN_ENV_NAME} er tom."
        )

    if len(token) < 48:
        raise JobClientError(
            "Det interne jobtoken er uventet kort."
        )

    return token


def validate_job_path(path: str) -> str:
    """
    Tillader kun de eksplicit godkendte cronjob-endpoints.
    """

    if path not in ALLOWED_JOB_PATHS:
        raise JobClientError(
            f"Jobendpointet er ikke godkendt: {path}"
        )

    return path


def run_job(path: str, token: str) -> int:
    """
    Kalder det lokale endpoint og videresender svaret til stdout.
    """

    connection = http.client.HTTPConnection(
        HOST,
        PORT,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    try:
        connection.request(
            "GET",
            path,
            headers={
                TOKEN_HEADER_NAME: token,
                "User-Agent": "Aureum-Internal-Job/1.0",
                "Connection": "close",
            },
        )

        response = connection.getresponse()
        body = response.read()

    except OSError as exc:
        raise JobClientError(
            f"Kunne ikke forbinde til Aureum AI: "
            f"{type(exc).__name__}: {exc}"
        ) from exc

    finally:
        connection.close()

    print(
        f"[aureum-job] {path} -> HTTP {response.status}",
        file=sys.stderr,
    )

    if body:
        sys.stdout.buffer.write(body)

        if not body.endswith(b"\n"):
            sys.stdout.buffer.write(b"\n")

        sys.stdout.buffer.flush()

    if not 200 <= response.status < 300:
        raise JobClientError(
            f"Jobbet returnerede HTTP {response.status}."
        )

    return 0


def print_configuration_check(token: str) -> None:
    """
    Viser kun ufølsomme kontroloplysninger.
    """

    fingerprint = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()[:12]

    print("environment_file:", ENV_PATH)
    print("environment_file_owner:", "root:root")
    print("token_variable_count:", 1)
    print("token_length:", len(token))
    print("token_fingerprint:", fingerprint)
    print("token_value_displayed:", False)
    print("allowed_job_count:", len(ALLOWED_JOB_PATHS))
    print("request_host:", HOST)
    print("request_port:", PORT)
    print("configuration_check: OK")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Kør et godkendt Aureum AI-job med "
            "internt token."
        )
    )

    parser.add_argument(
        "path",
        nargs="?",
        help="Godkendt internt jobendpoint.",
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "Kontrollér konfigurationen uden "
            "at foretage et HTTP-kald."
        ),
    )

    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    token = load_job_token()

    if arguments.check:
        if arguments.path:
            raise JobClientError(
                "--check kan ikke kombineres med et endpoint."
            )

        print_configuration_check(token)
        return 0

    if not arguments.path:
        raise JobClientError(
            "Der mangler et jobendpoint."
        )

    path = validate_job_path(arguments.path)

    return run_job(
        path,
        token,
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())

    except JobClientError as exc:
        print(
            f"[aureum-job] FEJL: {exc}",
            file=sys.stderr,
        )
        raise SystemExit(1)
