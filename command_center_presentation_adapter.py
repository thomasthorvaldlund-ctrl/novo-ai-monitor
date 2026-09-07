"""Pure V3 Command Center presentation adapter.

The adapter converts one verified/materialized Command Center projection
into a deterministic template view model.

It may:
- enforce the existing Slice-1/Slice-4 projection verification boundary
- enforce the Slice-6a payload-shape contract
- preserve explicit presentation metadata
- expose only explicitly allowlisted projection metadata
- derive the non-business `has_content` display helper
- expose verifier warnings without changing their meaning

It must not:
- build, publish, refresh or persist projections
- call providers, business services or OpenAI
- rank, filter, deduplicate or truncate opportunity cases
- invent fallback facts or empty-state data
- alter score, confidence, lifecycle, Portfolio Fit or freshness
- resolve canonical evidence
- create deep links
- render HTML
"""
from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass

from command_center_presentation_payload_contract import (
    MISSING_PAYLOAD,
    PRESENTATION_PAYLOAD_VERSION,
    PresentationPayloadIssue,
    validate_presentation_payload,
)
from command_center_projection_contract import (
    SECTION_KEYS,
)
from command_center_projection_verifier import (
    ProjectionVerificationIssue,
    ProjectionVerificationPolicy,
    verify_command_center_projection,
)


PRESENTATION_VIEW_MODEL_VERSION = (
    "command_center_presentation_view_model:v1"
)

SECTION_PRESENTATION_ORDER = (
    "page_context",
    "attention",
    "executive_decision_summary",
    "compounder_opportunities",
    "catalyst_opportunities",
    "portfolio_relevance",
    "what_changed",
    "market_context",
    "trust_data_system_state",
)


PROJECTION_PRESENTATION_METADATA_KEYS = (
    'command_center_projection_id',
    'schema_version',
    'presentation_policy_version',
    'materialized_at',
    'as_of',
    'source_cutoff',
    'source_references',
    'scope',
    'build_status',
)


if frozenset(
    SECTION_PRESENTATION_ORDER
) != SECTION_KEYS:
    raise RuntimeError(
        "presentation section order no longer matches "
        "the projection section contract"
    )


@dataclass(frozen=True)
class PresentationAdapterIssue:
    layer: str
    code: str
    path: str
    message: str
    severity: str


class PresentationAdapterError(ValueError):
    def __init__(
        self,
        issues,
    ):
        self.issues = tuple(
            issues
        )

        super().__init__(
            "; ".join(
                (
                    f"{issue.layer}:"
                    f"{issue.path}: "
                    f"{issue.message}"
                )
                for issue in self.issues
            )
        )


def _projection_issue(
    issue: ProjectionVerificationIssue,
) -> PresentationAdapterIssue:
    return PresentationAdapterIssue(
        layer="projection",
        code=issue.code,
        path=issue.path,
        message=issue.message,
        severity=issue.severity,
    )


def _payload_issue(
    issue: PresentationPayloadIssue,
) -> PresentationAdapterIssue:
    return PresentationAdapterIssue(
        layer="payload",
        code=issue.code,
        path=issue.path,
        message=issue.message,
        severity="ERROR",
    )


def _has_content(
    section_key: str,
    *,
    availability: str,
    payload_present: bool,
    payload: object,
) -> bool:
    """
    Derive only whether materialized display content exists.

    This is not investment/business meaning and does not alter
    availability or freshness.
    """
    if availability == "UNAVAILABLE":
        return False

    if (
        not payload_present
        or payload is None
    ):
        return False

    if section_key == "page_context":
        return True

    if (
        section_key
        == "executive_decision_summary"
    ):
        return bool(
            payload["points"]
        )

    return bool(
        payload
    )


def build_command_center_presentation_view_model(
    projection: Mapping[str, object],
    *,
    presentation_policy: ProjectionVerificationPolicy,
    payload_version: str,
) -> dict[str, object]:
    """
    Build a deterministic template view model from one projection.

    Projection verification remains authoritative for profile identity,
    opportunity limits and warning/error severity. This adapter never
    repairs a projection that fails those checks.

    Slice-6a remains authoritative for payload field shape. A malformed
    display payload fails closed rather than being rewritten.

    The result contains plain Python/JSON values only. Jinja escaping
    remains the responsibility of the later template layer.
    """
    verification_issues = (
        verify_command_center_projection(
            projection,
            presentation_policy=(
                presentation_policy
            ),
            required_sections=(
                SECTION_PRESENTATION_ORDER
            ),
        )
    )

    unknown_severity = tuple(
        issue
        for issue in verification_issues
        if issue.severity
        not in {
            "ERROR",
            "WARNING",
        }
    )

    if unknown_severity:
        raise PresentationAdapterError(
            _projection_issue(
                issue
            )
            for issue in unknown_severity
        )

    blocking = tuple(
        issue
        for issue in verification_issues
        if issue.severity == "ERROR"
    )

    if blocking:
        raise PresentationAdapterError(
            _projection_issue(
                issue
            )
            for issue in blocking
        )

    sections = projection[
        "sections"
    ]

    payload_issues = []

    for section_key in (
        SECTION_PRESENTATION_ORDER
    ):
        section = sections[
            section_key
        ]

        payload_present = (
            "payload" in section
        )

        payload = (
            section["payload"]
            if payload_present
            else MISSING_PAYLOAD
        )

        current_issues = (
            validate_presentation_payload(
                section_key,
                payload,
                availability=section[
                    "availability"
                ],
                payload_version=(
                    payload_version
                ),
                presentation_policy_version=(
                    projection[
                        "presentation_policy_version"
                    ]
                ),
            )
        )

        payload_issues.extend(
            _payload_issue(
                issue
            )
            for issue in current_issues
        )

    if payload_issues:
        raise PresentationAdapterError(
            payload_issues
        )

    view_sections = {}

    for section_key in (
        SECTION_PRESENTATION_ORDER
    ):
        section = sections[
            section_key
        ]

        payload_present = (
            "payload" in section
        )

        payload = (
            deepcopy(
                section["payload"]
            )
            if payload_present
            else None
        )

        source_as_of_present = (
            "source_as_of" in section
        )

        source_references_present = (
            "source_references"
            in section
        )

        view_sections[
            section_key
        ] = {
            "availability": (
                section["availability"]
            ),
            "freshness": (
                section["freshness"]
            ),
            "source_as_of_present": (
                source_as_of_present
            ),
            "source_as_of": (
                deepcopy(
                    section[
                        "source_as_of"
                    ]
                )
                if source_as_of_present
                else None
            ),
            "source_references_present": (
                source_references_present
            ),
            "source_references": (
                deepcopy(
                    section[
                        "source_references"
                    ]
                )
                if source_references_present
                else None
            ),
            "payload_present": (
                payload_present
            ),
            "payload": payload,
            "has_content": (
                _has_content(
                    section_key,
                    availability=section[
                        "availability"
                    ],
                    payload_present=(
                        payload_present
                    ),
                    payload=payload,
                )
            ),
        }

    projection_meta = deepcopy(
        {
            key: projection[key]
            for key
            in PROJECTION_PRESENTATION_METADATA_KEYS
            if key in projection
        }
    )

    warnings = [
        {
            "code": issue.code,
            "path": issue.path,
            "message": issue.message,
            "severity": issue.severity,
        }
        for issue in verification_issues
        if issue.severity == "WARNING"
    ]

    return {
        "view_model_version": (
            PRESENTATION_VIEW_MODEL_VERSION
        ),
        "payload_version": (
            payload_version
        ),
        "presentation_policy_version": (
            projection[
                "presentation_policy_version"
            ]
        ),
        "projection": (
            projection_meta
        ),
        "section_order": list(
            SECTION_PRESENTATION_ORDER
        ),
        "sections": (
            view_sections
        ),
        "verification_warnings": (
            warnings
        ),
    }
