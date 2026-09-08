from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from bs4 import BeautifulSoup
from flask import Flask
from jinja2 import StrictUndefined

from command_center_presentation_payload_contract import (
    PRESENTATION_PAYLOAD_VERSION,
)
from command_center_projection_verifier import (
    COMMAND_CENTER_PRESENTATION_POLICY_V1,
)
from command_center_v3_presentation_routes import (
    COMMAND_CENTER_V3_PRESENTATION_PATH,
    create_command_center_v3_presentation_blueprint,
)
from command_center_projection_builder import (
    build_command_center_projection,
)


ROOT = Path(__file__).resolve().parent


def _item(
    item_id,
):
    return {
        "item_id": item_id,
        "title": "Materialized item",
        "text": "Materialized text",
        "source_references": [
            "source:item",
        ],
    }


def _opportunity(
    profile,
    *,
    opportunity_id,
):
    return {
        "opportunity_id": opportunity_id,
        "opportunity_profile": profile,
        "instrument_id": "instrument:test",
        "instrument_label": "Example",
        "lifecycle": "MONITOR",
        "opportunity_score": 71,
        "ai_confidence": "MODERATE",
        "data_confidence": "HIGH",
        "why_now": "Materialized reason",
        "critical_blockers": [],
        "source_references": [
            "source:case",
        ],
    }


def _section(
    payload,
    *,
    source="source:section",
):
    return {
        "availability": "AVAILABLE",
        "freshness": "CURRENT",
        "source_as_of": "2026-09-07T16:59:00+00:00",
        "source_references": [
            source,
        ],
        "payload": payload,
    }


def _projection(
    *,
    scope=None,
):
    if scope is None:
        scope = {
            "kind": "GLOBAL",
        }

    sections = {
        "page_context": _section({
            "title": "Command Center V3",
            "description": "Materialized overview",
        }),
        "attention": _section([
            _item("attention:1"),
        ]),
        "executive_decision_summary": _section({
            "points": [
                "Materialized summary",
            ],
            "source_references": [
                "source:summary",
            ],
        }),
        "compounder_opportunities": _section([
            _opportunity(
                "COMPOUNDER",
                opportunity_id="opportunity:compounder",
            ),
        ]),
        "catalyst_opportunities": _section([
            _opportunity(
                "CATALYST",
                opportunity_id="opportunity:catalyst",
            ),
        ]),
        "portfolio_relevance": _section([{
            **_item("portfolio:1"),
            "instrument_id": "instrument:test",
            "opportunity_id": "opportunity:compounder",
            "portfolio_fit": 0,
        }]),
        "what_changed": _section([{
            **_item("changed:1"),
            "record_reference": "record:test",
        }]),
        "market_context": _section([
            _item("market:1"),
        ]),
        "trust_data_system_state": _section([
            _item("trust:1"),
        ]),
    }

    return build_command_center_projection(
        command_center_projection_id="slice6d:test",
        presentation_policy_version=(
            "command_center_presentation:v1"
        ),
        materialized_at="2026-09-07T17:00:00+00:00",
        as_of="2026-09-07T17:00:00+00:00",
        source_cutoff="2026-09-07T16:59:00+00:00",
        source_references=[
            "source:projection",
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
    payload_version=PRESENTATION_PAYLOAD_VERSION,
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
        __name__,
        template_folder=str(
            ROOT / "templates"
        ),
        static_folder=str(
            ROOT / "static"
        ),
    )
    app.testing = True
    app.jinja_env.undefined = StrictUndefined

    app.register_blueprint(
        create_command_center_v3_presentation_blueprint(
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
            payload_version=(
                payload_version
            ),
        )
    )

    return app


def _soup(response):
    return BeautifulSoup(
        response.get_data(as_text=True),
        "html.parser",
    )


def _assert_unavailable_html(
    response,
):
    assert response.status_code == 503
    assert response.headers[
        "Cache-Control"
    ] == "no-store"

    soup = _soup(response)

    assert soup.select_one(
        '[data-page-state="unavailable"]'
    ) is not None
    assert not soup.select(
        "[data-section], .cc-v3-case"
    )


def main():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)

        # Valid already-published projection -> deterministic HTML.
        valid_path = root / "valid.json"
        valid = _projection()
        _write_projection(
            valid_path,
            valid,
        )

        app = _app_for(
            projection_path=valid_path,
        )
        client = app.test_client()

        first = client.get(
            COMMAND_CENTER_V3_PRESENTATION_PATH
        )
        second = client.get(
            COMMAND_CENTER_V3_PRESENTATION_PATH
        )

        assert first.status_code == 200
        assert first.content_type.startswith(
            "text/html"
        )
        assert first.headers[
            "Cache-Control"
        ] == "no-store"
        assert first.data == second.data

        soup = _soup(first)
        section_keys = [
            node["data-section"]
            for node in soup.select(
                "[data-section]"
            )
        ]

        assert section_keys == [
            "page_context",
            "attention",
            "executive_decision_summary",
            "compounder_opportunities",
            "catalyst_opportunities",
            "portfolio_relevance",
            "what_changed",
            "market_context",
            "trust_data_system_state",
        ]
        assert len(
            soup.select(
                ".cc-v3-case"
            )
        ) == 2

        lock_path = valid_path.with_name(
            valid_path.name + ".lock"
        )
        assert not lock_path.exists()

        print(
            "valid_projection_renders_html: PASS"
        )
        print(
            "repeated_get_deterministic: PASS"
        )
        print(
            "html_read_side_effect_free: PASS"
        )

        # HEAD follows the same read path but returns no entity body.
        head = client.head(
            COMMAND_CENTER_V3_PRESENTATION_PATH
        )
        assert head.status_code == 200
        assert head.data == b""
        assert head.headers[
            "Cache-Control"
        ] == "no-store"

        print(
            "head_html_read_no_store: PASS"
        )

        # Authorization precedes any filesystem read.
        auth_calls = []

        def deny():
            auth_calls.append(
                "called"
            )
            return (
                "denied",
                401,
            )

        protected_path = (
            root / "must-not-be-read.json"
        )
        protected = _app_for(
            projection_path=protected_path,
            auth_gate=deny,
        ).test_client().get(
            COMMAND_CENTER_V3_PRESENTATION_PATH
        )

        assert protected.status_code == 401
        assert protected.headers[
            "Cache-Control"
        ] == "no-store"
        assert auth_calls == [
            "called"
        ]

        print(
            "auth_gate_precedes_projection_read: PASS"
        )

        # OPTIONS is authorized but never reads a corrupt/missing projection.
        options_auth_calls = []

        def deny_options():
            options_auth_calls.append(
                "called"
            )
            return (
                "denied",
                401,
            )

        denied_options = _app_for(
            projection_path=(
                root / "options-missing.json"
            ),
            auth_gate=deny_options,
        ).test_client().options(
            COMMAND_CENTER_V3_PRESENTATION_PATH
        )

        assert denied_options.status_code == 401
        assert options_auth_calls == [
            "called"
        ]
        assert denied_options.headers[
            "Cache-Control"
        ] == "no-store"

        corrupt_options_path = (
            root / "options-corrupt.json"
        )
        corrupt_options_path.write_text(
            "{corrupt",
            encoding="utf-8",
        )

        allowed_options = _app_for(
            projection_path=(
                corrupt_options_path
            ),
        ).test_client().options(
            COMMAND_CENTER_V3_PRESENTATION_PATH
        )

        assert allowed_options.status_code == 204
        assert allowed_options.headers[
            "Allow"
        ] == "GET, HEAD, OPTIONS"
        assert allowed_options.headers[
            "Cache-Control"
        ] == "no-store"

        print(
            "options_auth_gate_enforced: PASS"
        )
        print(
            "options_does_not_read_projection: PASS"
        )

        # Missing/corrupt/scope-mismatched projections fail closed as HTML.
        missing = _app_for(
            projection_path=(
                root / "missing.json"
            ),
        ).test_client().get(
            COMMAND_CENTER_V3_PRESENTATION_PATH
        )
        _assert_unavailable_html(
            missing
        )

        corrupt_path = root / "corrupt.json"
        corrupt_path.write_text(
            "{not-json",
            encoding="utf-8",
        )
        corrupt = _app_for(
            projection_path=corrupt_path,
        ).test_client().get(
            COMMAND_CENTER_V3_PRESENTATION_PATH
        )
        _assert_unavailable_html(
            corrupt
        )

        personal_path = root / "personal.json"
        personal = _projection(
            scope={
                "kind": "PERSONAL",
                "scope_id": "owner-a",
            }
        )
        _write_projection(
            personal_path,
            personal,
        )
        mismatch = _app_for(
            projection_path=personal_path,
            expected_scope={
                "kind": "PERSONAL",
                "scope_id": "owner-b",
            },
        ).test_client().get(
            COMMAND_CENTER_V3_PRESENTATION_PATH
        )
        _assert_unavailable_html(
            mismatch
        )

        print(
            "missing_projection_503_html: PASS"
        )
        print(
            "corrupt_projection_503_html: PASS"
        )
        print(
            "scope_mismatch_503_html: PASS"
        )

        # Adapter/payload failures fail closed instead of rendering facts.
        malformed_path = root / "malformed-payload.json"
        malformed = _projection()
        del malformed[
            "sections"
        ][
            "compounder_opportunities"
        ][
            "payload"
        ][0][
            "data_confidence"
        ]
        _write_projection(
            malformed_path,
            malformed,
        )
        malformed_response = _app_for(
            projection_path=malformed_path,
        ).test_client().get(
            COMMAND_CENTER_V3_PRESENTATION_PATH
        )
        _assert_unavailable_html(
            malformed_response
        )

        profile_path = root / "profile-mismatch.json"
        profile_projection = _projection()
        profile_projection[
            "sections"
        ][
            "compounder_opportunities"
        ][
            "payload"
        ][0][
            "opportunity_profile"
        ] = "CATALYST"
        _write_projection(
            profile_path,
            profile_projection,
        )
        profile_response = _app_for(
            projection_path=profile_path,
        ).test_client().get(
            COMMAND_CENTER_V3_PRESENTATION_PATH
        )
        _assert_unavailable_html(
            profile_response
        )

        print(
            "payload_contract_failure_503_html: PASS"
        )
        print(
            "profile_verification_failure_503_html: PASS"
        )

        # Warning-only projection remains renderable and warning stays visible.
        warning_path = root / "warning.json"
        warning_projection = _projection()
        duplicate = deepcopy(
            warning_projection[
                "sections"
            ][
                "compounder_opportunities"
            ][
                "payload"
            ][0]
        )
        warning_projection[
            "sections"
        ][
            "compounder_opportunities"
        ][
            "payload"
        ].append(
            duplicate
        )
        _write_projection(
            warning_path,
            warning_projection,
        )
        warning_response = _app_for(
            projection_path=warning_path,
        ).test_client().get(
            COMMAND_CENTER_V3_PRESENTATION_PATH
        )

        assert warning_response.status_code == 200
        warning_soup = _soup(
            warning_response
        )
        assert len(
            warning_soup.select(
                '[data-section="compounder_opportunities"] '
                ".cc-v3-case"
            )
        ) == 2
        warning_text = warning_soup.select_one(
            "[data-verification-warnings]"
        ).get_text()
        assert (
            "duplicate_executive_opportunity_id"
            in warning_text
        )

        print(
            "warning_only_projection_200_html: PASS"
        )

        # Caller-owned scope input is frozen at factory construction.
        caller_scope = {
            "kind": "GLOBAL",
        }
        isolated_app = _app_for(
            projection_path=valid_path,
            expected_scope=caller_scope,
        )
        caller_scope[
            "kind"
        ] = "PERSONAL"
        caller_scope[
            "scope_id"
        ] = "mutated"

        isolated_response = (
            isolated_app.test_client().get(
                COMMAND_CENTER_V3_PRESENTATION_PATH
            )
        )
        assert isolated_response.status_code == 200

        print(
            "caller_scope_mutation_isolated: PASS"
        )

        # Configuration errors fail before a request can be served.
        try:
            create_command_center_v3_presentation_blueprint(
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
                payload_version=(
                    PRESENTATION_PAYLOAD_VERSION
                ),
            )
        except ValueError:
            pass
        else:
            raise AssertionError(
                "Relative projection path accepted"
            )

        try:
            create_command_center_v3_presentation_blueprint(
                projection_path=valid_path,
                expected_scope={
                    "kind": "GLOBAL",
                },
                auth_gate=None,
                presentation_policy=(
                    COMMAND_CENTER_PRESENTATION_POLICY_V1
                ),
                payload_version=(
                    PRESENTATION_PAYLOAD_VERSION
                ),
            )
        except TypeError:
            pass
        else:
            raise AssertionError(
                "Non-callable auth gate accepted"
            )

        for invalid_scope in (
            {},
            {"kind": "OTHER"},
            {"kind": "PERSONAL"},
        ):
            try:
                create_command_center_v3_presentation_blueprint(
                    projection_path=valid_path,
                    expected_scope=invalid_scope,
                    auth_gate=lambda: None,
                    presentation_policy=(
                        COMMAND_CENTER_PRESENTATION_POLICY_V1
                    ),
                    payload_version=(
                        PRESENTATION_PAYLOAD_VERSION
                    ),
                )
            except (TypeError, ValueError):
                pass
            else:
                raise AssertionError(
                    "Invalid expected scope accepted"
                )

        try:
            create_command_center_v3_presentation_blueprint(
                projection_path=valid_path,
                expected_scope={
                    "kind": "GLOBAL",
                },
                auth_gate=lambda: None,
                presentation_policy=(
                    COMMAND_CENTER_PRESENTATION_POLICY_V1
                ),
                payload_version="future:v999",
            )
        except ValueError:
            pass
        else:
            raise AssertionError(
                "Future payload version accepted"
            )

        print(
            "absolute_projection_path_required: PASS"
        )
        print(
            "explicit_auth_gate_required: PASS"
        )
        print(
            "invalid_expected_scope_fail_fast: PASS"
        )
        print(
            "payload_version_bound: PASS"
        )

        # POST is not exposed and this isolated app has no V2 route.
        method_response = client.post(
            COMMAND_CENTER_V3_PRESENTATION_PATH
        )
        assert method_response.status_code == 405

        rules = {
            rule.rule
            for rule in app.url_map.iter_rules()
            if rule.endpoint != "static"
        }
        assert rules == {
            COMMAND_CENTER_V3_PRESENTATION_PATH
        }
        assert "/command-center" not in rules
        assert "/command-center-v3/read-model" not in rules

        print(
            "state_changing_method_not_exposed: PASS"
        )
        print(
            "isolated_html_blueprint_only: PASS"
        )

        # Static source boundary: no provider/business/generation imports.
        source = (
            ROOT
            / "command_center_v3_presentation_routes.py"
        ).read_text(
            encoding="utf-8"
        ).lower()

        for forbidden in (
            "openai_service",
            "yfinance",
            "feedparser",
            "requests.",
            "dashboard_cache_builder",
            "command_center_routes",
            "command_center_v3_routes",
        ):
            assert forbidden not in source, forbidden

        assert "render_template" in source
        assert "load_command_center_projection" in source
        assert (
            "build_command_center_presentation_view_model"
            in source
        )

        print(
            "render_path_provider_business_boundary: PASS"
        )

    print(
        "command_center_v3_presentation_routes_test: OK"
    )


if __name__ == "__main__":
    main()
