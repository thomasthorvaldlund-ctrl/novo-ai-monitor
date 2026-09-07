"""
Isolated non-serving V3 Command Center read route.

Slice 5 intentionally provides only a blueprint factory around an
already-published Command Center projection.

It does not:
- select a production projection path
- register itself in app.py
- replace /command-center
- render templates
- build or publish projections
- call business services, providers or OpenAI
- trigger refresh/revalidation work from GET

Production registration and serving selection belong to later D009
implementation slices.
"""

from __future__ import annotations

from collections.abc import (
    Callable,
    Iterable,
    Mapping,
)
from copy import deepcopy
from pathlib import Path

from flask import (
    Blueprint,
    jsonify,
    make_response,
    request,
)

from command_center_projection_contract import (
    SCOPE_KINDS,
    validate_command_center_projection,
)
from command_center_projection_store import (
    ProjectionStoreCorruptError,
    ProjectionStoreScopeMismatchError,
    load_command_center_projection,
)
from command_center_projection_verifier import (
    COMMAND_CENTER_PROJECTION_VERIFICATION_VERSION,
    ProjectionVerificationPolicy,
    verify_command_center_projection,
)


COMMAND_CENTER_V3_READ_PATH = (
    "/command-center-v3/read-model"
)


def _with_no_store(response_value):
    response = make_response(
        response_value
    )
    response.headers[
        "Cache-Control"
    ] = "no-store"

    return response


def _json_response(
    payload,
    *,
    status_code=200,
):
    response = jsonify(
        payload
    )
    response.status_code = status_code
    response.headers[
        "Cache-Control"
    ] = "no-store"

    return response


def _validated_expected_scope(
    expected_scope,
):
    if not isinstance(
        expected_scope,
        Mapping,
    ):
        raise TypeError(
            "expected_scope must be a mapping"
        )

    frozen_scope = deepcopy(
        dict(expected_scope)
    )

    kind = frozen_scope.get(
        "kind"
    )

    if kind not in SCOPE_KINDS:
        raise ValueError(
            "expected_scope kind must be "
            "GLOBAL or PERSONAL"
        )

    if kind == "PERSONAL":
        scope_id = frozen_scope.get(
            "scope_id"
        )

        if (
            not isinstance(scope_id, str)
            or not scope_id.strip()
        ):
            raise ValueError(
                "PERSONAL expected_scope requires "
                "a non-empty scope_id"
            )

    return frozen_scope


def _verification_payload(issues):
    return {
        "version": (
            COMMAND_CENTER_PROJECTION_VERIFICATION_VERSION
        ),
        "issues": [
            {
                "code": issue.code,
                "path": issue.path,
                "message": issue.message,
                "severity": issue.severity,
            }
            for issue in issues
        ],
    }


def _unavailable_response(
    reason,
    *,
    issues=(),
):
    return _json_response(
        {
            "status": "UNAVAILABLE",
            "reason": reason,
            "projection": None,
            "verification": _verification_payload(
                issues
            ),
        },
        status_code=503,
    )


def create_command_center_v3_read_blueprint(
    *,
    projection_path: Path | str,
    expected_scope: Mapping[str, object],
    auth_gate: Callable[[], object | None],
    presentation_policy: ProjectionVerificationPolicy,
    required_sections: Iterable[str] = (),
    required_source_sections: Iterable[str] = (),
) -> Blueprint:
    """
    Create an isolated V3 read blueprint.

    All deployment-sensitive inputs are supplied by the caller.
    The factory intentionally has no production defaults.
    """

    if not callable(auth_gate):
        raise TypeError(
            "auth_gate must be callable"
        )

    path = Path(
        projection_path
    )

    if not path.is_absolute():
        raise ValueError(
            "projection_path must be absolute"
        )

    frozen_required_sections = tuple(
        required_sections
    )

    frozen_required_source_sections = tuple(
        required_source_sections
    )

    #
    # Public Slice-1 validation rejects unknown
    # required-section policy before inspecting
    # projection contents.
    #
    validate_command_center_projection(
        {},
        required_sections=(
            frozen_required_sections
        ),
        required_source_sections=(
            frozen_required_source_sections
        ),
    )

    frozen_expected_scope = (
        _validated_expected_scope(
            expected_scope
        )
    )

    #
    # Public Slice-4 verification validates the
    # supplied registered presentation policy
    # before inspecting projection contents.
    #
    verify_command_center_projection(
        {},
        presentation_policy=(
            presentation_policy
        ),
    )

    blueprint = Blueprint(
        "command_center_v3_read",
        __name__,
    )

    @blueprint.route(
        COMMAND_CENTER_V3_READ_PATH,
        methods=[
            "GET",
            "HEAD",
            "OPTIONS",
        ],
        provide_automatic_options=False,
    )
    def read_command_center_v3_projection():
        auth_response = auth_gate()

        if auth_response is not None:
            return _with_no_store(
                auth_response
            )

        if request.method == "OPTIONS":
            response = _with_no_store(
                ("", 204)
            )
            response.headers[
                "Allow"
            ] = "GET, HEAD, OPTIONS"

            return response

        try:
            projection = (
                load_command_center_projection(
                    path,
                    expected_scope=(
                        frozen_expected_scope
                    ),
                    required_sections=(
                        frozen_required_sections
                    ),
                    required_source_sections=(
                        frozen_required_source_sections
                    ),
                )
            )
        except ProjectionStoreScopeMismatchError:
            return _unavailable_response(
                "projection_scope_mismatch"
            )
        except ProjectionStoreCorruptError:
            return _unavailable_response(
                "projection_invalid_or_corrupt"
            )

        if projection is None:
            return _unavailable_response(
                "projection_missing"
            )

        issues = verify_command_center_projection(
            projection,
            presentation_policy=(
                presentation_policy
            ),
            required_sections=(
                frozen_required_sections
            ),
            required_source_sections=(
                frozen_required_source_sections
            ),
        )

        if any(
            issue.severity == "ERROR"
            for issue in issues
        ):
            return _unavailable_response(
                "projection_verification_failed",
                issues=issues,
            )

        return _json_response({
            "status": "AVAILABLE",
            "reason": None,
            "projection": projection,
            "verification": (
                _verification_payload(
                    issues
                )
            ),
        })

    return blueprint
