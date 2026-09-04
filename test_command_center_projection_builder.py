from copy import deepcopy
from inspect import signature

from command_center_projection_builder import (
    build_command_center_projection,
)
from command_center_projection_contract import (
    COMMAND_CENTER_PROJECTION_SCHEMA_VERSION,
    ProjectionValidationError,
)


def valid_inputs():
    return {
        "command_center_projection_id":
            "projection-2026-09-02T12:00:00Z",
        "presentation_policy_version":
            "command_center_presentation:v1",
        "materialized_at":
            "2026-09-02T12:00:00+00:00",
        "as_of":
            "2026-09-02T12:00:00+00:00",
        "source_cutoff":
            "2026-09-02T11:59:00+00:00",
        "source_references": [
            "source:opportunities:123",
            "source:alerts:456",
        ],
        "scope": {
            "kind": "GLOBAL",
        },
        "build_status": "COMPLETE",
        "sections": {
            "attention": {
                "availability": "AVAILABLE",
                "freshness": "CURRENT",
                "source_as_of":
                    "2026-09-02T11:59:00+00:00",
                "source_references": [
                    "source:alerts:456",
                ],
            },
            "compounder_opportunities": {
                "availability": "AVAILABLE",
                "freshness": "CURRENT",
                "source_as_of":
                    "2026-09-02T11:58:00+00:00",
                "source_references": [
                    "source:compounder:1",
                ],
            },
            "catalyst_opportunities": {
                "availability": "PARTIAL",
                "freshness": "STALE",
                "source_as_of":
                    "2026-09-02T11:30:00+00:00",
                "source_references": [
                    "source:catalyst:1",
                ],
            },
            "portfolio_relevance": {
                "availability": "UNAVAILABLE",
                "freshness": "UNKNOWN",
                "source_as_of": None,
                "source_references": [],
            },
        },
    }


def issue_codes(exc):
    return {
        issue.code
        for issue in exc.issues
    }


def run_test():
    inputs = valid_inputs()
    before = deepcopy(inputs)

    projection = (
        build_command_center_projection(
            **inputs
        )
    )

    assert inputs == before

    assert projection[
        "schema_version"
    ] == COMMAND_CENTER_PROJECTION_SCHEMA_VERSION

    assert projection[
        "command_center_projection_id"
    ] == inputs[
        "command_center_projection_id"
    ]

    assert projection[
        "presentation_policy_version"
    ] == inputs[
        "presentation_policy_version"
    ]

    assert projection[
        "materialized_at"
    ] == inputs["materialized_at"]

    assert projection[
        "as_of"
    ] == inputs["as_of"]

    assert projection[
        "source_cutoff"
    ] == inputs["source_cutoff"]

    assert projection[
        "build_status"
    ] == inputs["build_status"]

    assert projection[
        "sections"
    ][
        "compounder_opportunities"
    ] != projection[
        "sections"
    ][
        "catalyst_opportunities"
    ]

    # Caller-owned mutable inputs must not be shared with the result.
    inputs[
        "source_references"
    ].append(
        "source:after-build"
    )

    inputs[
        "scope"
    ][
        "unexpected"
    ] = "after-build"

    inputs[
        "sections"
    ][
        "attention"
    ][
        "source_references"
    ].append(
        "source:after-build"
    )

    assert (
        "source:after-build"
        not in projection[
            "source_references"
        ]
    )

    assert (
        "unexpected"
        not in projection["scope"]
    )

    assert (
        "source:after-build"
        not in projection[
            "sections"
        ][
            "attention"
        ][
            "source_references"
        ]
    )

    # Mutating the returned projection must not mutate caller input.
    projection[
        "scope"
    ][
        "projection_only"
    ] = True

    assert (
        "projection_only"
        not in inputs["scope"]
    )

    # Same explicit inputs => same in-memory business/read-model content.
    deterministic_inputs = valid_inputs()

    first = build_command_center_projection(
        **deterministic_inputs
    )
    second = build_command_center_projection(
        **deterministic_inputs
    )

    assert first == second

    # No default/current timestamp may be invented.
    assert first[
        "materialized_at"
    ] == deterministic_inputs[
        "materialized_at"
    ]
    assert first["as_of"] == (
        deterministic_inputs["as_of"]
    )
    assert first[
        "source_cutoff"
    ] == deterministic_inputs[
        "source_cutoff"
    ]

    # Missing/unknown portfolio information must remain unavailable,
    # not be converted to an empty portfolio or numeric default.
    portfolio = first[
        "sections"
    ][
        "portfolio_relevance"
    ]

    assert portfolio[
        "availability"
    ] == "UNAVAILABLE"
    assert portfolio[
        "freshness"
    ] == "UNKNOWN"
    assert portfolio[
        "source_as_of"
    ] is None

    # Invalid caller-supplied status must be rejected, not repaired.
    invalid_status = valid_inputs()
    invalid_status[
        "sections"
    ][
        "attention"
    ][
        "availability"
    ] = "GOOD"

    try:
        build_command_center_projection(
            **invalid_status
        )
    except ProjectionValidationError as exc:
        assert (
            "invalid_section_availability"
            in issue_codes(exc)
        )
    else:
        raise AssertionError(
            "Invalid availability must fail"
        )

    # Missing required section remains missing and must fail policy.
    missing_required = valid_inputs()

    try:
        build_command_center_projection(
            **missing_required,
            required_sections={
                "executive_decision_summary",
            },
        )
    except ProjectionValidationError as exc:
        assert (
            "missing_required_section"
            in issue_codes(exc)
        )
    else:
        raise AssertionError(
            "Missing required section must fail"
        )

    # A required source reference may not be synthesized.
    missing_source = valid_inputs()
    missing_source[
        "sections"
    ][
        "attention"
    ][
        "source_references"
    ] = []

    try:
        build_command_center_projection(
            **missing_source,
            required_source_sections={
                "attention",
            },
        )
    except ProjectionValidationError as exc:
        assert (
            "missing_required_source_reference"
            in issue_codes(exc)
        )
    else:
        raise AssertionError(
            "Missing source reference must fail"
        )

    # Personal scope must remain explicit.
    invalid_personal = valid_inputs()
    invalid_personal["scope"] = {
        "kind": "PERSONAL",
    }

    try:
        build_command_center_projection(
            **invalid_personal
        )
    except ProjectionValidationError as exc:
        assert (
            "missing_personal_scope_id"
            in issue_codes(exc)
        )
    else:
        raise AssertionError(
            "Missing personal scope id must fail"
        )

    # Naive timestamp must fail instead of receiving an implicit timezone.
    invalid_timestamp = valid_inputs()
    invalid_timestamp["as_of"] = (
        "2026-09-02T12:00:00"
    )

    try:
        build_command_center_projection(
            **invalid_timestamp
        )
    except ProjectionValidationError as exc:
        assert (
            "invalid_timestamp"
            in issue_codes(exc)
        )
    else:
        raise AssertionError(
            "Naive timestamp must fail"
        )

    # Required construction metadata has no hidden defaults.
    sig = signature(
        build_command_center_projection
    )

    required_names = {
        "command_center_projection_id",
        "presentation_policy_version",
        "materialized_at",
        "as_of",
        "source_cutoff",
        "source_references",
        "scope",
        "build_status",
        "sections",
    }

    for name in required_names:
        parameter = sig.parameters[name]
        assert (
            parameter.default
            is parameter.empty
        )

    print("projection_build_valid: PASS")
    print("schema_identity_added: PASS")
    print("caller_inputs_not_mutated: PASS")
    print("defensive_copy_isolation: PASS")
    print("deterministic_same_inputs: PASS")
    print("timestamps_not_invented: PASS")
    print("missing_portfolio_not_defaulted: PASS")
    print("invalid_status_not_repaired: PASS")
    print("required_section_not_invented: PASS")
    print("source_reference_not_invented: PASS")
    print("personal_scope_not_invented: PASS")
    print("timezone_not_invented: PASS")
    print("construction_metadata_explicit: PASS")
    print(
        "command_center_projection_builder_test: OK"
    )


if __name__ == "__main__":
    run_test()
