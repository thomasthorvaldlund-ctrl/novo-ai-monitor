from copy import deepcopy

from command_center_projection_contract import (
    COMMAND_CENTER_PROJECTION_SCHEMA_VERSION,
    ProjectionValidationError,
    assert_valid_command_center_projection,
    validate_command_center_projection,
)


def valid_projection():
    return {
        "command_center_projection_id":
            "projection-2026-09-02T10:00:00Z",
        "schema_version":
            COMMAND_CENTER_PROJECTION_SCHEMA_VERSION,
        "presentation_policy_version":
            "command_center_presentation:v1",
        "materialized_at":
            "2026-09-02T10:00:00+00:00",
        "as_of":
            "2026-09-02T10:00:00+00:00",
        "source_cutoff":
            "2026-09-02T09:59:00+00:00",
        "source_references": [
            "source:opportunities:123",
            "source:alerts:456",
        ],
        "scope": {
            "kind": "GLOBAL",
        },
        "build_status": "COMPLETE",
        "sections": {
            "page_context": {
                "availability": "AVAILABLE",
                "freshness": "CURRENT",
                "source_as_of":
                    "2026-09-02T10:00:00+00:00",
                "source_references": [
                    "source:page-context:1",
                ],
            },
            "attention": {
                "availability": "AVAILABLE",
                "freshness": "CURRENT",
                "source_as_of":
                    "2026-09-02T09:59:00+00:00",
                "source_references": [
                    "source:alerts:456",
                ],
            },
            "market_context": {
                "availability": "PARTIAL",
                "freshness": "STALE",
                "source_as_of":
                    "2026-09-02T09:30:00+00:00",
                "source_references": [
                    "source:market:789",
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


def issue_codes(projection, **kwargs):
    return {
        issue.code
        for issue in validate_command_center_projection(
            projection,
            **kwargs,
        )
    }


def run_test():
    projection = valid_projection()

    assert (
        validate_command_center_projection(
            projection
        )
        == ()
    )

    assert_valid_command_center_projection(
        projection
    )

    unknown_schema = deepcopy(
        projection
    )
    unknown_schema["schema_version"] = (
        "command_center_projection:v999"
    )

    assert (
        "unknown_schema_version"
        in issue_codes(unknown_schema)
    )

    missing_identity = deepcopy(
        projection
    )
    del missing_identity[
        "command_center_projection_id"
    ]

    codes = issue_codes(
        missing_identity
    )

    assert "missing_required_field" in codes
    assert "invalid_projection_id" in codes

    naive_timestamp = deepcopy(
        projection
    )
    naive_timestamp["as_of"] = (
        "2026-09-02T10:00:00"
    )

    assert (
        "invalid_timestamp"
        in issue_codes(naive_timestamp)
    )

    bad_availability = deepcopy(
        projection
    )
    bad_availability[
        "sections"
    ][
        "attention"
    ][
        "availability"
    ] = "GOOD"

    assert (
        "invalid_section_availability"
        in issue_codes(
            bad_availability
        )
    )

    bad_freshness = deepcopy(
        projection
    )
    bad_freshness[
        "sections"
    ][
        "attention"
    ][
        "freshness"
    ] = "LIVE"

    assert (
        "invalid_section_freshness"
        in issue_codes(
            bad_freshness
        )
    )

    stale_without_timestamp = deepcopy(
        projection
    )
    stale_without_timestamp[
        "sections"
    ][
        "market_context"
    ][
        "source_as_of"
    ] = None

    assert (
        "invalid_section_source_as_of"
        in issue_codes(
            stale_without_timestamp
        )
    )

    personal_without_scope = deepcopy(
        projection
    )
    personal_without_scope["scope"] = {
        "kind": "PERSONAL",
    }

    assert (
        "missing_personal_scope_id"
        in issue_codes(
            personal_without_scope
        )
    )

    personal = deepcopy(
        projection
    )
    personal["scope"] = {
        "kind": "PERSONAL",
        "scope_id": "principal-scope-123",
    }

    assert (
        validate_command_center_projection(
            personal
        )
        == ()
    )

    unknown_section = deepcopy(
        projection
    )
    unknown_section[
        "sections"
    ][
        "hidden_business_score"
    ] = {
        "availability": "AVAILABLE",
        "freshness": "CURRENT",
        "source_as_of":
            "2026-09-02T10:00:00+00:00",
        "source_references": [
            "source:hidden:1",
        ],
    }

    assert (
        "unknown_section"
        in issue_codes(
            unknown_section
        )
    )

    required_missing = issue_codes(
        projection,
        required_sections={
            "executive_decision_summary",
        },
    )

    assert (
        "missing_required_section"
        in required_missing
    )

    required_source = deepcopy(
        projection
    )
    required_source[
        "sections"
    ][
        "attention"
    ][
        "source_references"
    ] = []

    assert (
        "missing_required_source_reference"
        in issue_codes(
            required_source,
            required_source_sections={
                "attention",
            },
        )
    )

    try:
        assert_valid_command_center_projection(
            unknown_schema
        )
    except ProjectionValidationError as exc:
        assert exc.issues
        assert any(
            issue.code
            == "unknown_schema_version"
            for issue in exc.issues
        )
    else:
        raise AssertionError(
            "Expected ProjectionValidationError"
        )

    try:
        validate_command_center_projection(
            projection,
            required_sections={
                "not_a_real_section",
            },
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Unknown policy section must fail"
        )

    print(
        "valid_projection: PASS"
    )
    print(
        "unknown_schema_rejected: PASS"
    )
    print(
        "required_identity_rejected: PASS"
    )
    print(
        "timezone_aware_timestamp_enforced: PASS"
    )
    print(
        "availability_freshness_separate: PASS"
    )
    print(
        "personal_scope_isolated: PASS"
    )
    print(
        "unknown_section_rejected: PASS"
    )
    print(
        "required_section_policy: PASS"
    )
    print(
        "required_source_reference_policy: PASS"
    )
    print(
        "assertion_api: PASS"
    )
    print(
        "command_center_projection_contract_test: OK"
    )


if __name__ == "__main__":
    run_test()
