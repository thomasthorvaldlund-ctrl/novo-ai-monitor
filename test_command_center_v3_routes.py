from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from flask import Flask

from command_center_projection_builder import (
    build_command_center_projection,
)
from command_center_projection_verifier import (
    COMMAND_CENTER_PRESENTATION_POLICY_V1,
)
from command_center_v3_routes import (
    COMMAND_CENTER_V3_READ_PATH,
    create_command_center_v3_read_blueprint,
)


def _projection(
    *,
    projection_id="route-test",
    scope=None,
    sections=None,
):
    if scope is None:
        scope = {
            "kind": "GLOBAL",
        }

    if sections is None:
        sections = {}

    return build_command_center_projection(
        command_center_projection_id=(
            projection_id
        ),
        presentation_policy_version=(
            "command_center_presentation:v1"
        ),
        materialized_at=(
            "2026-09-07T17:00:00+00:00"
        ),
        as_of=(
            "2026-09-07T17:00:00+00:00"
        ),
        source_cutoff=(
            "2026-09-07T16:59:00+00:00"
        ),
        source_references=[
            "source:test",
        ],
        scope=scope,
        build_status="COMPLETE",
        sections=sections,
    )


def _write_projection(
    path,
    projection,
):
    path.write_text(
        json.dumps(
            projection,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )


def _app_for(
    *,
    projection_path,
    expected_scope=None,
    auth_gate=None,
    presentation_policy=None,
    required_sections=(),
    required_source_sections=(),
):
    if expected_scope is None:
        expected_scope = {
            "kind": "GLOBAL",
        }

    if auth_gate is None:
        auth_gate = lambda: None

    if presentation_policy is None:
        presentation_policy = (
            COMMAND_CENTER_PRESENTATION_POLICY_V1
        )

    app = Flask(
        __name__
    )

    app.register_blueprint(
        create_command_center_v3_read_blueprint(
            projection_path=(
                projection_path
            ),
            expected_scope=(
                expected_scope
            ),
            auth_gate=auth_gate,
            presentation_policy=(
                presentation_policy
            ),
            required_sections=(
                required_sections
            ),
            required_source_sections=(
                required_source_sections
            ),
        )
    )

    return app


def _opportunity_section(
    profile,
    cases,
):
    return {
        "availability": "AVAILABLE",
        "freshness": "CURRENT",
        "source_as_of": (
            "2026-09-07T16:59:00+00:00"
        ),
        "source_references": [
            f"source:{profile.lower()}",
        ],
        "payload": cases,
    }


def main():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)

        #
        # Valid projection -> 200.
        #
        valid_path = root / "valid.json"
        valid = _projection(
            projection_id="valid"
        )

        _write_projection(
            valid_path,
            valid,
        )

        original_bytes = (
            valid_path.read_bytes()
        )

        app = _app_for(
            projection_path=valid_path
        )

        client = app.test_client()

        response = client.get(
            COMMAND_CENTER_V3_READ_PATH
        )

        assert response.status_code == 200

        payload = response.get_json()

        assert payload["status"] == "AVAILABLE"
        assert payload["reason"] is None
        assert (
            payload["projection"][
                "command_center_projection_id"
            ]
            == "valid"
        )
        assert (
            payload["verification"][
                "issues"
            ]
            == []
        )

        assert (
            response.headers.get(
                "Cache-Control"
            )
            == "no-store"
        )

        assert (
            valid_path.read_bytes()
            == original_bytes
        )

        assert not Path(
            str(valid_path) + ".lock"
        ).exists()

        print(
            "valid_projection_200: PASS"
        )
        print(
            "valid_read_side_effect_free: PASS"
        )

        #
        # Repeated GET remains deterministic.
        #
        second = client.get(
            COMMAND_CENTER_V3_READ_PATH
        )

        assert second.status_code == 200
        assert second.get_json() == payload
        assert (
            valid_path.read_bytes()
            == original_bytes
        )

        print(
            "repeated_get_deterministic: PASS"
        )

        #
        # Auth gate runs before projection read.
        #
        protected_path = (
            root / "must-not-be-read.json"
        )

        auth_calls = []

        def deny():
            auth_calls.append(
                "called"
            )
            return (
                "Login required",
                401,
            )

        protected_app = _app_for(
            projection_path=protected_path,
            auth_gate=deny,
        )

        protected_response = (
            protected_app.test_client().get(
                COMMAND_CENTER_V3_READ_PATH
            )
        )

        assert (
            protected_response.status_code
            == 401
        )
        assert auth_calls == ["called"]
        assert not protected_path.exists()
        assert not Path(
            str(protected_path) + ".lock"
        ).exists()

        print(
            "auth_gate_precedes_read: PASS"
        )

        #
        # Missing projection -> stable 503.
        #
        missing_path = (
            root / "missing.json"
        )

        missing_response = (
            _app_for(
                projection_path=missing_path
            )
            .test_client()
            .get(
                COMMAND_CENTER_V3_READ_PATH
            )
        )

        assert (
            missing_response.status_code
            == 503
        )

        missing_payload = (
            missing_response.get_json()
        )

        assert (
            missing_payload["status"]
            == "UNAVAILABLE"
        )
        assert (
            missing_payload["reason"]
            == "projection_missing"
        )
        assert (
            missing_payload["projection"]
            is None
        )
        assert not missing_path.exists()
        assert not Path(
            str(missing_path) + ".lock"
        ).exists()

        print(
            "missing_projection_503: PASS"
        )
        print(
            "missing_read_side_effect_free: PASS"
        )

        #
        # Corrupt JSON -> stable 503.
        #
        corrupt_path = (
            root / "corrupt.json"
        )

        corrupt_path.write_text(
            "{not-json",
            encoding="utf-8",
        )

        corrupt_before = (
            corrupt_path.read_bytes()
        )

        corrupt_response = (
            _app_for(
                projection_path=corrupt_path
            )
            .test_client()
            .get(
                COMMAND_CENTER_V3_READ_PATH
            )
        )

        assert (
            corrupt_response.status_code
            == 503
        )

        assert (
            corrupt_response.get_json()[
                "reason"
            ]
            == "projection_invalid_or_corrupt"
        )

        assert (
            corrupt_path.read_bytes()
            == corrupt_before
        )

        print(
            "corrupt_projection_503: PASS"
        )

        #
        # Contract-invalid published JSON -> same
        # corrupt/unavailable transport category.
        #
        invalid_contract_path = (
            root / "invalid-contract.json"
        )

        invalid_contract_path.write_text(
            json.dumps({
                "schema_version": "wrong"
            }),
            encoding="utf-8",
        )

        invalid_contract_response = (
            _app_for(
                projection_path=(
                    invalid_contract_path
                )
            )
            .test_client()
            .get(
                COMMAND_CENTER_V3_READ_PATH
            )
        )

        assert (
            invalid_contract_response.status_code
            == 503
        )

        assert (
            invalid_contract_response.get_json()[
                "reason"
            ]
            == "projection_invalid_or_corrupt"
        )

        print(
            "contract_invalid_projection_503: PASS"
        )

        #
        # Scope mismatch -> fail closed as unavailable,
        # not as an authorization decision.
        #
        scoped_path = (
            root / "scope.json"
        )

        _write_projection(
            scoped_path,
            _projection(
                projection_id="scope"
            ),
        )

        scoped_response = (
            _app_for(
                projection_path=scoped_path,
                expected_scope={
                    "kind": "PERSONAL",
                    "scope_id": "user:test",
                },
            )
            .test_client()
            .get(
                COMMAND_CENTER_V3_READ_PATH
            )
        )

        assert (
            scoped_response.status_code
            == 503
        )

        assert (
            scoped_response.get_json()[
                "reason"
            ]
            == "projection_scope_mismatch"
        )

        print(
            "scope_mismatch_503: PASS"
        )

        #
        # Slice-4 blocking semantic failure -> 503.
        #
        blocking_path = (
            root / "blocking.json"
        )

        blocking_cases = [
            {
                "opportunity_id": f"C-{index}",
                "opportunity_profile": (
                    "COMPOUNDER"
                ),
            }
            for index in range(1, 4)
        ]

        _write_projection(
            blocking_path,
            _projection(
                projection_id="blocking",
                sections={
                    "compounder_opportunities": (
                        _opportunity_section(
                            "COMPOUNDER",
                            blocking_cases,
                        )
                    ),
                },
            ),
        )

        blocking_response = (
            _app_for(
                projection_path=blocking_path
            )
            .test_client()
            .get(
                COMMAND_CENTER_V3_READ_PATH
            )
        )

        assert (
            blocking_response.status_code
            == 503
        )

        blocking_payload = (
            blocking_response.get_json()
        )

        assert (
            blocking_payload["reason"]
            == "projection_verification_failed"
        )

        assert any(
            issue["code"]
            == "executive_opportunity_limit_exceeded"
            and issue["severity"] == "ERROR"
            for issue in (
                blocking_payload[
                    "verification"
                ]["issues"]
            )
        )

        assert (
            blocking_payload["projection"]
            is None
        )

        print(
            "blocking_verifier_issue_503: PASS"
        )

        #
        # Warning-only projection remains serveable.
        #
        warning_path = (
            root / "warning.json"
        )

        warning_cases = [
            {
                "opportunity_id": "same",
                "opportunity_profile": (
                    "COMPOUNDER"
                ),
            },
            {
                "opportunity_id": "same",
                "opportunity_profile": (
                    "COMPOUNDER"
                ),
            },
        ]

        _write_projection(
            warning_path,
            _projection(
                projection_id="warning",
                sections={
                    "compounder_opportunities": (
                        _opportunity_section(
                            "COMPOUNDER",
                            warning_cases,
                        )
                    ),
                },
            ),
        )

        warning_response = (
            _app_for(
                projection_path=warning_path
            )
            .test_client()
            .get(
                COMMAND_CENTER_V3_READ_PATH
            )
        )

        assert (
            warning_response.status_code
            == 200
        )

        warning_payload = (
            warning_response.get_json()
        )

        assert (
            warning_payload["status"]
            == "AVAILABLE"
        )

        assert any(
            issue["code"]
            == "duplicate_executive_opportunity_id"
            and issue["severity"] == "WARNING"
            for issue in (
                warning_payload[
                    "verification"
                ]["issues"]
            )
        )

        print(
            "warning_only_projection_200: PASS"
        )

        #
        # Factory freezes one-shot policy iterables.
        #
        required_path = (
            root / "required.json"
        )

        required_projection = _projection(
            projection_id="required",
            sections={
                "compounder_opportunities": (
                    _opportunity_section(
                        "COMPOUNDER",
                        [],
                    )
                ),
            },
        )

        _write_projection(
            required_path,
            required_projection,
        )

        required_app = _app_for(
            projection_path=required_path,
            required_sections=(
                item
                for item in [
                    "compounder_opportunities"
                ]
            ),
            required_source_sections=(
                item
                for item in [
                    "compounder_opportunities"
                ]
            ),
        )

        required_client = (
            required_app.test_client()
        )

        first_required = required_client.get(
            COMMAND_CENTER_V3_READ_PATH
        )
        second_required = required_client.get(
            COMMAND_CENTER_V3_READ_PATH
        )

        assert (
            first_required.status_code
            == 200
        )
        assert (
            second_required.status_code
            == 200
        )
        assert (
            first_required.get_json()
            == second_required.get_json()
        )

        print(
            "one_shot_policy_iterables_frozen: PASS"
        )

        #
        # Caller scope mutation after factory creation
        # cannot retarget the route.
        #
        mutable_scope = {
            "kind": "GLOBAL",
        }

        isolated_app = _app_for(
            projection_path=valid_path,
            expected_scope=mutable_scope,
        )

        mutable_scope.clear()
        mutable_scope.update({
            "kind": "PERSONAL",
            "scope_id": "changed",
        })

        isolated_response = (
            isolated_app.test_client().get(
                COMMAND_CENTER_V3_READ_PATH
            )
        )

        assert (
            isolated_response.status_code
            == 200
        )

        print(
            "caller_scope_mutation_isolated: PASS"
        )

        #
        # Configuration must remain explicit.
        #
        try:
            create_command_center_v3_read_blueprint(
                projection_path=Path(
                    "relative.json"
                ),
                expected_scope={
                    "kind": "GLOBAL",
                },
                auth_gate=lambda: None,
                presentation_policy=(
                    COMMAND_CENTER_PRESENTATION_POLICY_V1
                ),
            )
        except ValueError:
            pass
        else:
            raise AssertionError(
                "Relative projection path accepted"
            )

        try:
            create_command_center_v3_read_blueprint(
                projection_path=valid_path,
                expected_scope={
                    "kind": "GLOBAL",
                },
                auth_gate=None,
                presentation_policy=(
                    COMMAND_CENTER_PRESENTATION_POLICY_V1
                ),
            )
        except TypeError:
            pass
        else:
            raise AssertionError(
                "Non-callable auth gate accepted"
            )

        print(
            "absolute_projection_path_required: PASS"
        )
        print(
            "explicit_auth_gate_required: PASS"
        )

        #
        # Unknown required-section configuration must
        # fail at factory creation, never as request-time
        # projection corruption or HTTP 500.
        #
        try:
            create_command_center_v3_read_blueprint(
                projection_path=valid_path,
                expected_scope={
                    "kind": "GLOBAL",
                },
                auth_gate=lambda: None,
                presentation_policy=(
                    COMMAND_CENTER_PRESENTATION_POLICY_V1
                ),
                required_sections=(
                    "__not_a_section__",
                ),
            )
        except ValueError:
            pass
        else:
            raise AssertionError(
                "Unknown required section accepted"
            )

        print(
            "unknown_required_section_fail_fast: PASS"
        )

        #
        # Expected scope is configuration and must
        # therefore be valid before a request exists.
        #
        try:
            create_command_center_v3_read_blueprint(
                projection_path=valid_path,
                expected_scope={
                    "kind": "NOT_A_SCOPE",
                },
                auth_gate=lambda: None,
                presentation_policy=(
                    COMMAND_CENTER_PRESENTATION_POLICY_V1
                ),
            )
        except ValueError:
            pass
        else:
            raise AssertionError(
                "Invalid expected scope accepted"
            )

        try:
            create_command_center_v3_read_blueprint(
                projection_path=valid_path,
                expected_scope={
                    "kind": "PERSONAL",
                    "scope_id": "   ",
                },
                auth_gate=lambda: None,
                presentation_policy=(
                    COMMAND_CENTER_PRESENTATION_POLICY_V1
                ),
            )
        except ValueError:
            pass
        else:
            raise AssertionError(
                "Empty personal scope_id accepted"
            )

        print(
            "invalid_expected_scope_fail_fast: PASS"
        )

        #
        # Registered policy meaning must be validated
        # during factory creation, not on first GET.
        #
        from command_center_projection_verifier import (
            ProjectionVerificationPolicy,
        )

        dishonest_policy = (
            ProjectionVerificationPolicy(
                presentation_policy_version=(
                    "command_center_presentation:v1"
                ),
                compounder_max_cases=999,
                catalyst_max_cases=999,
            )
        )

        try:
            create_command_center_v3_read_blueprint(
                projection_path=valid_path,
                expected_scope={
                    "kind": "GLOBAL",
                },
                auth_gate=lambda: None,
                presentation_policy=(
                    dishonest_policy
                ),
            )
        except ValueError:
            pass
        else:
            raise AssertionError(
                "Dishonest presentation policy accepted"
            )

        print(
            "invalid_presentation_policy_fail_fast: PASS"
        )

        #
        # OPTIONS is explicit so it cannot bypass
        # the caller-supplied authorization gate.
        #
        options_auth_calls = []

        def deny_options():
            options_auth_calls.append(
                "called"
            )
            return (
                "Login required",
                401,
            )

        options_denied_app = _app_for(
            projection_path=valid_path,
            auth_gate=deny_options,
        )

        denied_options = (
            options_denied_app
            .test_client()
            .options(
                COMMAND_CENTER_V3_READ_PATH
            )
        )

        assert denied_options.status_code == 401
        assert options_auth_calls == ["called"]
        assert (
            denied_options.headers.get(
                "Cache-Control"
            )
            == "no-store"
        )

        options_corrupt_path = (
            root / "options-corrupt.json"
        )

        options_corrupt_path.write_text(
            "{ corrupt but OPTIONS must not read it",
            encoding="utf-8",
        )

        allowed_options = (
            _app_for(
                projection_path=(
                    options_corrupt_path
                )
            )
            .test_client()
            .options(
                COMMAND_CENTER_V3_READ_PATH
            )
        )

        assert allowed_options.status_code == 204
        assert (
            allowed_options.headers.get(
                "Allow"
            )
            == "GET, HEAD, OPTIONS"
        )
        assert (
            allowed_options.headers.get(
                "Cache-Control"
            )
            == "no-store"
        )

        print(
            "options_auth_gate_enforced: PASS"
        )
        print(
            "options_does_not_read_projection: PASS"
        )

        #
        # Unavailable read-model responses are also
        # explicitly non-cacheable.
        #
        assert (
            missing_response.headers.get(
                "Cache-Control"
            )
            == "no-store"
        )
        assert (
            corrupt_response.headers.get(
                "Cache-Control"
            )
            == "no-store"
        )
        assert (
            scoped_response.headers.get(
                "Cache-Control"
            )
            == "no-store"
        )
        assert (
            blocking_response.headers.get(
                "Cache-Control"
            )
            == "no-store"
        )

        print(
            "read_model_responses_no_store: PASS"
        )

        #
        # No state-changing method is exposed.
        # GET/HEAD/OPTIONS are read-only transport
        # methods; POST remains unavailable.
        #
        method_response = client.post(
            COMMAND_CENTER_V3_READ_PATH
        )

        assert (
            method_response.status_code
            == 405
        )

        print(
            "state_changing_method_not_exposed: PASS"
        )

    print(
        "command_center_v3_routes_test: OK"
    )


if __name__ == "__main__":
    main()
