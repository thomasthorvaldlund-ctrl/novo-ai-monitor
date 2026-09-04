from copy import deepcopy

import command_center_projection_verifier as verifier_module

from command_center_projection_builder import (
    build_command_center_projection,
)
from command_center_projection_verifier import (
    COMMAND_CENTER_PRESENTATION_POLICY_V1,
    COMMAND_CENTER_PROJECTION_VERIFICATION_VERSION,
    ProjectionVerificationError,
    ProjectionVerificationPolicy,
    assert_verified_command_center_projection,
    verify_command_center_projection,
)


GLOBAL_SCOPE = {
    "kind": "GLOBAL",
}

POLICY_V1 = (
    COMMAND_CENTER_PRESENTATION_POLICY_V1
)


def valid_projection(
    *,
    policy_version=(
        "command_center_presentation:v1"
    ),
):
    return build_command_center_projection(
        command_center_projection_id=(
            "slice4-verifier-test"
        ),
        presentation_policy_version=(
            policy_version
        ),
        materialized_at=(
            "2026-09-04T20:00:00+00:00"
        ),
        as_of=(
            "2026-09-04T20:00:00+00:00"
        ),
        source_cutoff=(
            "2026-09-04T19:59:00+00:00"
        ),
        source_references=[
            "source:projection:v1",
        ],
        scope=GLOBAL_SCOPE,
        build_status="COMPLETE",
        sections={
            "compounder_opportunities": {
                "availability": "AVAILABLE",
                "freshness": "CURRENT",
                "source_as_of": (
                    "2026-09-04T19:59:00+00:00"
                ),
                "source_references": [
                    "source:compounder:v1",
                ],
                "payload": [
                    {
                        "opportunity_id": (
                            "compounder-1"
                        ),
                        "opportunity_profile": (
                            "COMPOUNDER"
                        ),
                    },
                    {
                        "opportunity_id": (
                            "compounder-2"
                        ),
                        "opportunity_profile": (
                            "COMPOUNDER"
                        ),
                    },
                ],
            },
            "catalyst_opportunities": {
                "availability": "AVAILABLE",
                "freshness": "CURRENT",
                "source_as_of": (
                    "2026-09-04T19:58:00+00:00"
                ),
                "source_references": [
                    "source:catalyst:v1",
                ],
                "payload": [
                    {
                        "opportunity_id": (
                            "catalyst-1"
                        ),
                        "opportunity_profile": (
                            "CATALYST"
                        ),
                    },
                    {
                        "opportunity_id": (
                            "catalyst-2"
                        ),
                        "opportunity_profile": (
                            "CATALYST"
                        ),
                    },
                ],
            },
        },
    )


def verify(
    projection,
    *,
    policy=POLICY_V1,
    **kwargs,
):
    return verify_command_center_projection(
        projection,
        presentation_policy=policy,
        **kwargs,
    )


def assert_verified(
    projection,
    *,
    policy=POLICY_V1,
    **kwargs,
):
    return assert_verified_command_center_projection(
        projection,
        presentation_policy=policy,
        **kwargs,
    )


def codes(
    issues,
    *,
    severity=None,
):
    return {
        issue.code
        for issue in issues
        if (
            severity is None
            or issue.severity == severity
        )
    }


def run_test():
    assert (
        COMMAND_CENTER_PROJECTION_VERIFICATION_VERSION
        == "command_center_projection_verification:v1"
    )

    assert (
        POLICY_V1.presentation_policy_version
        == "command_center_presentation:v1"
    )
    assert (
        POLICY_V1.compounder_max_cases
        == 2
    )
    assert (
        POLICY_V1.catalyst_max_cases
        == 2
    )

    print("locked_v1_policy_definition: PASS")

    #
    # The registered meaning of v1 must not be mutable at runtime.
    #
    registry = (
        verifier_module._KNOWN_PRESENTATION_POLICIES
    )

    try:
        registry[
            "command_center_presentation:v1"
        ] = ProjectionVerificationPolicy(
            presentation_policy_version=(
                "command_center_presentation:v1"
            ),
            compounder_max_cases=999,
            catalyst_max_cases=999,
        )
    except TypeError:
        pass
    else:
        raise AssertionError(
            "Presentation policy registry "
            "must be runtime read-only"
        )

    assert (
        registry[
            "command_center_presentation:v1"
        ]
        == POLICY_V1
    )

    print("policy_registry_runtime_immutable: PASS")

    projection = valid_projection()
    before = deepcopy(
        projection
    )

    assert (
        verify(
            projection,
            required_sections={
                "compounder_opportunities",
                "catalyst_opportunities",
            },
            required_source_sections={
                "compounder_opportunities",
                "catalyst_opportunities",
            },
        )
        == ()
    )

    assert projection == before

    print("valid_projection_verified: PASS")
    print("caller_projection_not_mutated: PASS")

    #
    # Initial V3 v1 policy is immutably 2+2.
    #
    too_many_v1 = valid_projection()

    too_many_v1[
        "sections"
    ][
        "compounder_opportunities"
    ][
        "payload"
    ].append(
        {
            "opportunity_id": "compounder-3",
            "opportunity_profile": "COMPOUNDER",
        }
    )

    assert (
        "executive_opportunity_limit_exceeded"
        in codes(
            verify(
                too_many_v1
            ),
            severity="ERROR",
        )
    )

    print("v1_two_case_ceiling_enforced: PASS")

    #
    # Caller may not relabel a changed definition as the same v1.
    #
    dishonest_v1 = ProjectionVerificationPolicy(
        presentation_policy_version=(
            "command_center_presentation:v1"
        ),
        compounder_max_cases=3,
        catalyst_max_cases=99,
    )

    try:
        verify(
            too_many_v1,
            policy=dishonest_v1,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Caller redefined locked v1 policy"
        )

    print("v1_policy_redefinition_rejected: PASS")

    #
    # Future versions are not invented by Slice 4.
    # They must be explicitly registered when actually defined.
    #
    future_projection = valid_projection(
        policy_version=(
            "command_center_presentation:v2"
        ),
    )

    future_policy = ProjectionVerificationPolicy(
        presentation_policy_version=(
            "command_center_presentation:v2"
        ),
        compounder_max_cases=3,
        catalyst_max_cases=2,
    )

    try:
        verify(
            future_projection,
            policy=future_policy,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Unknown future policy version "
            "must fail closed"
        )

    print("unknown_future_policy_fails_closed: PASS")

    #
    # Projection identity and supplied policy version must agree.
    #
    mismatched_projection = valid_projection(
        policy_version=(
            "command_center_presentation:v2"
        ),
    )

    mismatch_issues = verify(
        mismatched_projection,
        policy=POLICY_V1,
    )

    assert (
        "presentation_policy_version_mismatch"
        in codes(
            mismatch_issues,
            severity="ERROR",
        )
    )

    print("projection_policy_version_bound: PASS")

    #
    # No invented top-level/section source-ref subset rule.
    #
    section_specific = valid_projection()

    section_specific[
        "source_references"
    ] = [
        "source:projection-only",
    ]

    section_specific[
        "sections"
    ][
        "compounder_opportunities"
    ][
        "source_references"
    ] = [
        "source:section-specific",
    ]

    assert (
        verify(
            section_specific
        )
        == ()
    )

    print(
        "section_ref_need_not_be_top_level_subset: PASS"
    )

    #
    # Source-reference requirement remains explicit caller policy
    # delegated to Slice 1.
    #
    missing_source = valid_projection()

    missing_source[
        "sections"
    ][
        "compounder_opportunities"
    ][
        "source_references"
    ] = []

    assert (
        "contract.missing_required_source_reference"
        in codes(
            verify(
                missing_source,
                required_source_sections={
                    "compounder_opportunities",
                },
            ),
            severity="ERROR",
        )
    )

    print(
        "source_reference_requirement_explicit: PASS"
    )

    #
    # Same-profile duplicate is advisory, matching "bør ikke".
    #
    duplicate_same_profile = valid_projection()

    duplicate_same_profile[
        "sections"
    ][
        "compounder_opportunities"
    ][
        "payload"
    ][1][
        "opportunity_id"
    ] = "compounder-1"

    duplicate_issues = verify(
        duplicate_same_profile
    )

    assert (
        "duplicate_executive_opportunity_id"
        in codes(
            duplicate_issues,
            severity="WARNING",
        )
    )

    assert_verified(
        duplicate_same_profile
    )

    print("same_profile_duplicate_is_warning: PASS")
    print("warning_does_not_block_assertion: PASS")

    #
    # Warning cannot hide a blocking verification error.
    #
    warning_and_error = deepcopy(
        duplicate_same_profile
    )

    warning_and_error[
        "sections"
    ][
        "compounder_opportunities"
    ][
        "payload"
    ][1][
        "opportunity_profile"
    ] = "CATALYST"

    combined_issues = verify(
        warning_and_error
    )

    assert (
        "duplicate_executive_opportunity_id"
        in codes(
            combined_issues,
            severity="WARNING",
        )
    )

    assert (
        "opportunity_profile_mismatch"
        in codes(
            combined_issues,
            severity="ERROR",
        )
    )

    try:
        assert_verified(
            warning_and_error
        )
    except ProjectionVerificationError as exc:
        assert exc.issues
        assert all(
            issue.severity == "ERROR"
            for issue in exc.issues
        )
    else:
        raise AssertionError(
            "Blocking error was masked by warning"
        )

    print("warning_does_not_mask_error: PASS")

    #
    # Same opportunity identity crossing profile groups is blocking.
    #
    cross_profile_collision = valid_projection()

    cross_profile_collision[
        "sections"
    ][
        "catalyst_opportunities"
    ][
        "payload"
    ][0][
        "opportunity_id"
    ] = "compounder-1"

    collision_issues = verify(
        cross_profile_collision
    )

    assert (
        (
            "cross_profile_"
            "opportunity_identity_collision"
        )
        in codes(
            collision_issues,
            severity="ERROR",
        )
    )

    try:
        assert_verified(
            cross_profile_collision
        )
    except ProjectionVerificationError:
        pass
    else:
        raise AssertionError(
            "Cross-profile identity collision "
            "must block verification"
        )

    print(
        "cross_profile_identity_collision_blocked: PASS"
    )

    #
    # Profile field must match section.
    #
    profile_mix = valid_projection()

    profile_mix[
        "sections"
    ][
        "compounder_opportunities"
    ][
        "payload"
    ][0][
        "opportunity_profile"
    ] = "CATALYST"

    assert (
        "opportunity_profile_mismatch"
        in codes(
            verify(
                profile_mix
            ),
            severity="ERROR",
        )
    )

    print("profile_mismatch_rejected: PASS")

    #
    # Stable opportunity identity required.
    #
    missing_identity = valid_projection()

    del (
        missing_identity[
            "sections"
        ][
            "compounder_opportunities"
        ][
            "payload"
        ][0][
            "opportunity_id"
        ]
    )

    assert (
        "missing_opportunity_id"
        in codes(
            verify(
                missing_identity
            ),
            severity="ERROR",
        )
    )

    print("missing_opportunity_id_rejected: PASS")

    #
    # AVAILABLE/PARTIAL explicitly materializes its case list.
    #
    missing_payload = valid_projection()

    del (
        missing_payload[
            "sections"
        ][
            "compounder_opportunities"
        ][
            "payload"
        ]
    )

    assert (
        "missing_opportunity_payload"
        in codes(
            verify(
                missing_payload
            ),
            severity="ERROR",
        )
    )

    malformed_payload = valid_projection()

    malformed_payload[
        "sections"
    ][
        "compounder_opportunities"
    ][
        "payload"
    ] = {}

    assert (
        "invalid_opportunity_payload"
        in codes(
            verify(
                malformed_payload
            ),
            severity="ERROR",
        )
    )

    print("missing_case_list_rejected: PASS")
    print("malformed_case_list_rejected: PASS")

    #
    # Explicit zero-result state is valid.
    #
    empty = valid_projection()

    empty[
        "sections"
    ][
        "compounder_opportunities"
    ][
        "payload"
    ] = []

    empty[
        "sections"
    ][
        "catalyst_opportunities"
    ][
        "payload"
    ] = []

    assert verify(empty) == ()

    print("zero_qualified_cases_valid: PASS")

    #
    # UNAVAILABLE section cannot expose active cases.
    #
    unavailable = valid_projection()

    unavailable_section = (
        unavailable[
            "sections"
        ][
            "catalyst_opportunities"
        ]
    )

    unavailable_section[
        "availability"
    ] = "UNAVAILABLE"
    unavailable_section[
        "freshness"
    ] = "UNKNOWN"
    unavailable_section[
        "source_as_of"
    ] = None
    unavailable_section[
        "source_references"
    ] = []
    unavailable_section[
        "payload"
    ] = []

    assert verify(unavailable) == ()

    unavailable_section[
        "payload"
    ] = [
        {
            "opportunity_id": "stale-catalyst",
            "opportunity_profile": "CATALYST",
        },
    ]

    assert (
        "unavailable_opportunity_section_has_cases"
        in codes(
            verify(
                unavailable
            ),
            severity="ERROR",
        )
    )

    print("unavailable_empty_section_valid: PASS")
    print("unavailable_section_cases_rejected: PASS")

    #
    # Slice-1 contract issues remain visible.
    #
    invalid_schema = valid_projection()

    invalid_schema[
        "schema_version"
    ] = "unknown:v999"

    assert (
        "contract.unknown_schema_version"
        in codes(
            verify(
                invalid_schema
            ),
            severity="ERROR",
        )
    )

    print("slice1_contract_issue_preserved: PASS")

    #
    # Caller-required section policy remains explicit.
    #
    missing_required = valid_projection()

    del (
        missing_required[
            "sections"
        ][
            "catalyst_opportunities"
        ]
    )

    assert (
        "contract.missing_required_section"
        in codes(
            verify(
                missing_required,
                required_sections=(
                    item
                    for item in [
                        "catalyst_opportunities",
                    ]
                ),
            ),
            severity="ERROR",
        )
    )

    print(
        "one_shot_required_section_policy_preserved: PASS"
    )

    #
    # Structurally invalid policy fails closed.
    #
    invalid_policy = ProjectionVerificationPolicy(
        presentation_policy_version=(
            "command_center_presentation:v1"
        ),
        compounder_max_cases=-1,
        catalyst_max_cases=2,
    )

    try:
        verify(
            projection,
            policy=invalid_policy,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Invalid verification policy must fail"
        )

    print("invalid_verification_policy_rejected: PASS")

    #
    # Deterministic and side-effect free.
    #
    before_collision = deepcopy(
        cross_profile_collision
    )

    first = verify(
        cross_profile_collision
    )
    second = verify(
        cross_profile_collision
    )

    assert first == second
    assert (
        cross_profile_collision
        == before_collision
    )

    print("deterministic_same_projection: PASS")
    print("verifier_does_not_mutate_projection: PASS")

    print("deep_link_destination_contract: DEFERRED")
    print("canonical_evidence_resolution: NOT_CLAIMED")
    print(
        "command_center_projection_verifier_test: OK"
    )


if __name__ == "__main__":
    run_test()
