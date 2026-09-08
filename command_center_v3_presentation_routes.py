"""Isolated non-serving V3 Command Center HTML presentation route.

Slice 6d binds one already-published projection to the locked presentation
adapter and the Slice-6c template. It intentionally does not:
- select a production projection path
- register itself in app.py or replace /command-center
- alter the existing JSON read-model route
- build, publish, refresh or persist projections
- call business services, providers or OpenAI
- create deep links, navigation or a serving selector

All deployment-sensitive inputs are caller supplied. Ordinary GET/HEAD reads
are side-effect-free and never fall back to V2 business/service generation.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from copy import deepcopy
from pathlib import Path

from flask import (
    Blueprint,
    make_response,
    render_template,
    request,
)

from command_center_presentation_adapter import (
    PresentationAdapterError,
    SECTION_PRESENTATION_ORDER,
    build_command_center_presentation_view_model,
)
from command_center_presentation_payload_contract import (
    PRESENTATION_PAYLOAD_VERSION,
)
from command_center_projection_contract import (
    SCOPE_KINDS,
)
from command_center_projection_store import (
    ProjectionStoreCorruptError,
    ProjectionStoreScopeMismatchError,
    load_command_center_projection,
)
from command_center_projection_verifier import (
    ProjectionVerificationPolicy,
    verify_command_center_projection,
)


COMMAND_CENTER_V3_PRESENTATION_PATH = (
    "/command-center-v3/presentation"
)
COMMAND_CENTER_V3_TEMPLATE = (
    "command_center_v3.html"
)


def _with_no_store(response_value):
    response = make_response(
        response_value
    )
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


def _render_unavailable():
    return _with_no_store((
        render_template(
            COMMAND_CENTER_V3_TEMPLATE,
            vm=None,
        ),
        503,
    ))


def create_command_center_v3_presentation_blueprint(
    *,
    projection_path: Path | str,
    expected_scope: Mapping[str, object],
    auth_gate: Callable[[], object | None],
    presentation_policy: ProjectionVerificationPolicy,
    payload_version: str,
) -> Blueprint:
    """Create an isolated HTML presentation blueprint with no prod defaults."""
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

    frozen_expected_scope = (
        _validated_expected_scope(
            expected_scope
        )
    )

    if payload_version != PRESENTATION_PAYLOAD_VERSION:
        raise ValueError(
            "unsupported presentation payload version"
        )

    # Validate the supplied registered policy at construction time.
    verify_command_center_projection(
        {},
        presentation_policy=(
            presentation_policy
        ),
    )

    blueprint = Blueprint(
        "command_center_v3_presentation",
        __name__,
    )

    @blueprint.route(
        COMMAND_CENTER_V3_PRESENTATION_PATH,
        methods=[
            "GET",
            "HEAD",
            "OPTIONS",
        ],
        provide_automatic_options=False,
    )
    def present_command_center_v3():
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
                        SECTION_PRESENTATION_ORDER
                    ),
                )
            )
        except (
            ProjectionStoreScopeMismatchError,
            ProjectionStoreCorruptError,
        ):
            return _render_unavailable()

        if projection is None:
            return _render_unavailable()

        try:
            view_model = (
                build_command_center_presentation_view_model(
                    projection,
                    presentation_policy=(
                        presentation_policy
                    ),
                    payload_version=(
                        payload_version
                    ),
                )
            )
        except PresentationAdapterError:
            return _render_unavailable()

        return _with_no_store(
            render_template(
                COMMAND_CENTER_V3_TEMPLATE,
                vm=view_model,
            )
        )

    return blueprint
