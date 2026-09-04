"""
Pure non-serving V3 Command Center projection verifier.

Slice 4 verifies presentation/read-model invariants that can be established
from an already materialized projection without fetching business data.

It does not:
- fetch canonical records
- call providers or OpenAI
- publish projections
- choose a production path
- integrate routes/templates/cache/cron
- validate a concrete deep-link destination contract

Deep-link destination validation remains deferred until the dedicated
navigation/deep-link slice installs a concrete semantic target contract.

This verifier also does not claim that a source-reference string proves
canonical business evidence. It only verifies auditable read-model
references and executive opportunity presentation invariants.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from types import MappingProxyType

from command_center_projection_contract import (
    validate_command_center_projection,
)


COMMAND_CENTER_PROJECTION_VERIFICATION_VERSION = (
    "command_center_projection_verification:v1"
)


_EXECUTIVE_OPPORTUNITY_PROFILES = {
    "compounder_opportunities": "COMPOUNDER",
    "catalyst_opportunities": "CATALYST",
}


@dataclass(frozen=True)
class ProjectionVerificationPolicy:
    """
    Explicit presentation-policy inputs used by the verifier.

    The verifier does not infer ceilings from schema version and does not
    silently apply one presentation policy to another version.

    Each supported version is bound to one registered policy definition;
    callers cannot redefine the meaning of an existing version.
    """

    presentation_policy_version: str
    compounder_max_cases: int
    catalyst_max_cases: int


COMMAND_CENTER_PRESENTATION_POLICY_V1 = (
    ProjectionVerificationPolicy(
        presentation_policy_version=(
            "command_center_presentation:v1"
        ),
        compounder_max_cases=2,
        catalyst_max_cases=2,
    )
)


_KNOWN_PRESENTATION_POLICIES = MappingProxyType({
    (
        COMMAND_CENTER_PRESENTATION_POLICY_V1
        .presentation_policy_version
    ): COMMAND_CENTER_PRESENTATION_POLICY_V1,
})


@dataclass(frozen=True)
class ProjectionVerificationIssue:
    code: str
    path: str
    message: str
    severity: str = "ERROR"


class ProjectionVerificationError(ValueError):
    def __init__(
        self,
        issues: Iterable[
            ProjectionVerificationIssue
        ],
    ) -> None:
        self.issues = tuple(
            issues
        )

        super().__init__(
            "; ".join(
                (
                    f"{issue.code} "
                    f"at {issue.path}: "
                    f"{issue.message}"
                )
                for issue in self.issues
            )
        )


def _issue(
    issues: list[
        ProjectionVerificationIssue
    ],
    code: str,
    path: str,
    message: str,
    *,
    severity: str = "ERROR",
) -> None:
    issues.append(
        ProjectionVerificationIssue(
            code=code,
            path=path,
            message=message,
            severity=severity,
        )
    )


def _non_empty_string(
    value: object,
) -> bool:
    return (
        isinstance(value, str)
        and bool(value.strip())
    )


def _validate_verification_policy(
    policy: ProjectionVerificationPolicy,
) -> None:
    if not isinstance(
        policy,
        ProjectionVerificationPolicy,
    ):
        raise TypeError(
            "presentation_policy must be "
            "ProjectionVerificationPolicy"
        )

    if not _non_empty_string(
        policy.presentation_policy_version
    ):
        raise ValueError(
            "presentation policy version "
            "must be non-empty"
        )

    for field_name, value in (
        (
            "compounder_max_cases",
            policy.compounder_max_cases,
        ),
        (
            "catalyst_max_cases",
            policy.catalyst_max_cases,
        ),
    ):
        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or value < 0
        ):
            raise ValueError(
                f"{field_name} must be a "
                "non-negative integer"
            )

    expected_policy = (
        _KNOWN_PRESENTATION_POLICIES.get(
            policy.presentation_policy_version
        )
    )

    if expected_policy is None:
        raise ValueError(
            "unsupported presentation policy version"
        )

    if policy != expected_policy:
        raise ValueError(
            "presentation policy definition does "
            "not match the registered definition "
            "for its version"
        )


def _verify_opportunity_section(
    *,
    section_name: str,
    section: Mapping[str, object],
    max_cases: int,
    seen_opportunity_ids: dict[
        str,
        tuple[str, str],
    ],
    issues: list[
        ProjectionVerificationIssue
    ],
) -> None:
    expected_profile = (
        _EXECUTIVE_OPPORTUNITY_PROFILES[
            section_name
        ]
    )

    section_path = (
        f"sections.{section_name}"
    )

    availability = section.get(
        "availability"
    )

    if availability not in {
        "AVAILABLE",
        "PARTIAL",
        "UNAVAILABLE",
    }:
        # The Slice-1 contract reports the malformed
        # availability. Avoid duplicate speculative errors.
        return

    payload_present = (
        "payload" in section
    )
    payload = section.get(
        "payload"
    )

    if availability == "UNAVAILABLE":
        if (
            payload_present
            and payload not in (
                None,
                [],
            )
        ):
            _issue(
                issues,
                "unavailable_opportunity_section_has_cases",
                f"{section_path}.payload",
                (
                    "UNAVAILABLE opportunity section "
                    "must not expose executive cases"
                ),
            )

        return

    if not payload_present:
        _issue(
            issues,
            "missing_opportunity_payload",
            f"{section_path}.payload",
            (
                "AVAILABLE/PARTIAL opportunity "
                "section must explicitly materialize "
                "its executive case list"
            ),
        )
        return

    if not isinstance(
        payload,
        list,
    ):
        _issue(
            issues,
            "invalid_opportunity_payload",
            f"{section_path}.payload",
            (
                "executive opportunity payload "
                "must be a list"
            ),
        )
        return

    if len(payload) > max_cases:
        _issue(
            issues,
            "executive_opportunity_limit_exceeded",
            f"{section_path}.payload",
            (
                f"{expected_profile} executive "
                f"section may contain at most "
                f"{max_cases} cases"
            ),
        )

    for index, item in enumerate(
        payload
    ):
        item_path = (
            f"{section_path}.payload[{index}]"
        )

        if not isinstance(
            item,
            Mapping,
        ):
            _issue(
                issues,
                "invalid_opportunity_case",
                item_path,
                (
                    "executive opportunity case "
                    "must be an object"
                ),
            )
            continue

        opportunity_id = item.get(
            "opportunity_id"
        )

        if not _non_empty_string(
            opportunity_id
        ):
            _issue(
                issues,
                "missing_opportunity_id",
                f"{item_path}.opportunity_id",
                (
                    "executive opportunity case "
                    "requires a stable opportunity_id"
                ),
            )
        else:
            previous = (
                seen_opportunity_ids.get(
                    opportunity_id
                )
            )

            if previous is not None:
                (
                    previous_section,
                    previous_path,
                ) = previous

                if (
                    previous_section
                    != section_name
                ):
                    _issue(
                        issues,
                        (
                            "cross_profile_"
                            "opportunity_identity_collision"
                        ),
                        (
                            f"{item_path}."
                            "opportunity_id"
                        ),
                        (
                            "same opportunity_id cannot "
                            "identify both Compounder and "
                            "Catalyst executive cases; "
                            f"first seen at {previous_path}"
                        ),
                    )
                else:
                    _issue(
                        issues,
                        (
                            "duplicate_executive_"
                            "opportunity_id"
                        ),
                        (
                            f"{item_path}."
                            "opportunity_id"
                        ),
                        (
                            "same opportunity_id should "
                            "not occupy multiple peer "
                            "slots in one executive group; "
                            f"first seen at {previous_path}"
                        ),
                        severity="WARNING",
                    )
            else:
                seen_opportunity_ids[
                    opportunity_id
                ] = (
                    section_name,
                    (
                        f"{item_path}."
                        "opportunity_id"
                    ),
                )

        opportunity_profile = item.get(
            "opportunity_profile"
        )

        if (
            opportunity_profile
            != expected_profile
        ):
            _issue(
                issues,
                "opportunity_profile_mismatch",
                (
                    f"{item_path}."
                    "opportunity_profile"
                ),
                (
                    f"{section_name} requires "
                    f"opportunity_profile "
                    f"{expected_profile}"
                ),
            )


def verify_command_center_projection(
    projection: object,
    *,
    presentation_policy: ProjectionVerificationPolicy,
    required_sections: Iterable[str] = (),
    required_source_sections: Iterable[
        str
    ] = (),
) -> tuple[
    ProjectionVerificationIssue,
    ...,
]:
    """
    Verify one already materialized projection without side effects.

    This is a read-model verification layer, not a business engine.
    """

    _validate_verification_policy(
        presentation_policy
    )

    required_sections = tuple(
        required_sections
    )
    required_source_sections = tuple(
        required_source_sections
    )

    issues: list[
        ProjectionVerificationIssue
    ] = []

    contract_issues = (
        validate_command_center_projection(
            projection,
            required_sections=(
                required_sections
            ),
            required_source_sections=(
                required_source_sections
            ),
        )
    )

    for contract_issue in contract_issues:
        _issue(
            issues,
            (
                "contract."
                f"{contract_issue.code}"
            ),
            contract_issue.path,
            contract_issue.message,
        )

    if not isinstance(
        projection,
        Mapping,
    ):
        return tuple(
            issues
        )

    projection_policy_version = (
        projection.get(
            "presentation_policy_version"
        )
    )

    if (
        _non_empty_string(
            projection_policy_version
        )
        and projection_policy_version
        != presentation_policy.presentation_policy_version
    ):
        _issue(
            issues,
            "presentation_policy_version_mismatch",
            "presentation_policy_version",
            (
                "projection presentation-policy "
                "version does not match the "
                "explicit verification policy"
            ),
        )

    sections = projection.get(
        "sections"
    )

    if not isinstance(
        sections,
        Mapping,
    ):
        return tuple(
            issues
        )

    seen_opportunity_ids: dict[
        str,
        tuple[str, str],
    ] = {}

    for section_name in (
        "compounder_opportunities",
        "catalyst_opportunities",
    ):
        section = sections.get(
            section_name
        )

        if section is None:
            continue

        if not isinstance(
            section,
            Mapping,
        ):
            # Slice-1 contract reports malformed
            # sections.
            continue

        _verify_opportunity_section(
            section_name=section_name,
            section=section,
            max_cases=(
                presentation_policy.compounder_max_cases
                if section_name
                == "compounder_opportunities"
                else presentation_policy.catalyst_max_cases
            ),
            seen_opportunity_ids=(
                seen_opportunity_ids
            ),
            issues=issues,
        )

    return tuple(
        issues
    )


def assert_verified_command_center_projection(
    projection: object,
    *,
    presentation_policy: ProjectionVerificationPolicy,
    required_sections: Iterable[str] = (),
    required_source_sections: Iterable[
        str
    ] = (),
) -> None:
    issues = verify_command_center_projection(
        projection,
        presentation_policy=presentation_policy,
        required_sections=(
            required_sections
        ),
        required_source_sections=(
            required_source_sections
        ),
    )

    blocking_issues = tuple(
        issue
        for issue in issues
        if issue.severity == "ERROR"
    )

    if blocking_issues:
        raise ProjectionVerificationError(
            blocking_issues
        )
