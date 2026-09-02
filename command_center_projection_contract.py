"""
Pure V3 Command Center projection contract.

Slice 1 intentionally contains no filesystem I/O, provider calls,
OpenAI calls, route integration, cache publication or business mutation.

The module validates only the read-model envelope and section-status
semantics locked by V3-D009. Business payload, deep-link and publication
semantics are added in later isolated slices.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Mapping


COMMAND_CENTER_PROJECTION_SCHEMA_VERSION = (
    "command_center_projection:v1"
)

AVAILABILITY_VALUES = frozenset({
    "AVAILABLE",
    "PARTIAL",
    "UNAVAILABLE",
})

FRESHNESS_VALUES = frozenset({
    "CURRENT",
    "STALE",
    "UNKNOWN",
})

SCOPE_KINDS = frozenset({
    "GLOBAL",
    "PERSONAL",
})

SECTION_KEYS = frozenset({
    "page_context",
    "attention",
    "executive_decision_summary",
    "compounder_opportunities",
    "catalyst_opportunities",
    "portfolio_relevance",
    "what_changed",
    "market_context",
    "trust_data_system_state",
})

_REQUIRED_FIELDS = (
    "command_center_projection_id",
    "schema_version",
    "presentation_policy_version",
    "materialized_at",
    "as_of",
    "source_cutoff",
    "source_references",
    "scope",
    "build_status",
    "sections",
)


@dataclass(frozen=True)
class ProjectionValidationIssue:
    code: str
    path: str
    message: str


class ProjectionValidationError(ValueError):
    def __init__(
        self,
        issues: Iterable[ProjectionValidationIssue],
    ) -> None:
        self.issues = tuple(issues)

        summary = "; ".join(
            f"{issue.path}: {issue.message}"
            for issue in self.issues
        )

        super().__init__(
            summary
            or "Command Center projection is invalid."
        )


def _non_empty_string(value: object) -> bool:
    return (
        isinstance(value, str)
        and bool(value.strip())
    )


def _aware_iso_timestamp(value: object) -> bool:
    if not _non_empty_string(value):
        return False

    text = str(value).strip()

    if text.endswith("Z"):
        text = text[:-1] + "+00:00"

    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return False

    return (
        parsed.tzinfo is not None
        and parsed.utcoffset() is not None
    )


def _string_list(value: object) -> bool:
    if not isinstance(value, list):
        return False

    return all(
        _non_empty_string(item)
        for item in value
    )


def _issue(
    issues: list[ProjectionValidationIssue],
    code: str,
    path: str,
    message: str,
) -> None:
    issues.append(
        ProjectionValidationIssue(
            code=code,
            path=path,
            message=message,
        )
    )


def _validate_scope(
    value: object,
    issues: list[ProjectionValidationIssue],
) -> None:
    if not isinstance(value, Mapping):
        _issue(
            issues,
            "invalid_scope",
            "scope",
            "scope must be an object",
        )
        return

    kind = value.get("kind")

    if kind not in SCOPE_KINDS:
        _issue(
            issues,
            "invalid_scope_kind",
            "scope.kind",
            "scope kind must be GLOBAL or PERSONAL",
        )
        return

    if kind == "PERSONAL":
        scope_id = value.get("scope_id")

        if not _non_empty_string(scope_id):
            _issue(
                issues,
                "missing_personal_scope_id",
                "scope.scope_id",
                "PERSONAL scope requires an opaque scope_id",
            )


def _validate_section(
    section_name: str,
    value: object,
    issues: list[ProjectionValidationIssue],
    *,
    source_reference_required: bool,
) -> None:
    path = f"sections.{section_name}"

    if not isinstance(value, Mapping):
        _issue(
            issues,
            "invalid_section",
            path,
            "section must be an object",
        )
        return

    availability = value.get("availability")
    freshness = value.get("freshness")

    if availability not in AVAILABILITY_VALUES:
        _issue(
            issues,
            "invalid_section_availability",
            f"{path}.availability",
            "availability must be AVAILABLE, PARTIAL or UNAVAILABLE",
        )

    if freshness not in FRESHNESS_VALUES:
        _issue(
            issues,
            "invalid_section_freshness",
            f"{path}.freshness",
            "freshness must be CURRENT, STALE or UNKNOWN",
        )

    source_as_of = value.get("source_as_of")

    if freshness in {"CURRENT", "STALE"}:
        if not _aware_iso_timestamp(source_as_of):
            _issue(
                issues,
                "invalid_section_source_as_of",
                f"{path}.source_as_of",
                "CURRENT/STALE section requires timezone-aware source_as_of",
            )

    elif (
        source_as_of is not None
        and not _aware_iso_timestamp(source_as_of)
    ):
        _issue(
            issues,
            "invalid_section_source_as_of",
            f"{path}.source_as_of",
            "source_as_of must be timezone-aware when present",
        )

    references = value.get(
        "source_references",
        [],
    )

    if not _string_list(references):
        _issue(
            issues,
            "invalid_section_source_references",
            f"{path}.source_references",
            "source_references must be a list of non-empty strings",
        )

    elif (
        source_reference_required
        and not references
    ):
        _issue(
            issues,
            "missing_required_source_reference",
            f"{path}.source_references",
            "required section has no source reference",
        )


def validate_command_center_projection(
    projection: object,
    *,
    required_sections: Iterable[str] = (),
    required_source_sections: Iterable[str] = (),
) -> tuple[ProjectionValidationIssue, ...]:
    """
    Validate the D009 projection envelope without side effects.

    `required_sections` and `required_source_sections` are explicit
    caller policy inputs. This keeps presentation policy separate from
    the schema contract and avoids inventing hidden business semantics.
    """

    issues: list[ProjectionValidationIssue] = []

    required_section_set = frozenset(
        required_sections
    )
    required_source_set = frozenset(
        required_source_sections
    )

    unknown_required = (
        required_section_set
        | required_source_set
    ) - SECTION_KEYS

    if unknown_required:
        raise ValueError(
            "Unknown required section policy: "
            + ", ".join(sorted(unknown_required))
        )

    if not isinstance(projection, Mapping):
        _issue(
            issues,
            "invalid_projection",
            "$",
            "projection must be an object",
        )
        return tuple(issues)

    for field in _REQUIRED_FIELDS:
        if field not in projection:
            _issue(
                issues,
                "missing_required_field",
                field,
                "required projection field is missing",
            )

    if not _non_empty_string(
        projection.get(
            "command_center_projection_id"
        )
    ):
        _issue(
            issues,
            "invalid_projection_id",
            "command_center_projection_id",
            "projection id must be a non-empty string",
        )

    schema_version = projection.get(
        "schema_version"
    )

    if (
        schema_version
        != COMMAND_CENTER_PROJECTION_SCHEMA_VERSION
    ):
        _issue(
            issues,
            "unknown_schema_version",
            "schema_version",
            "schema version is not supported",
        )

    if not _non_empty_string(
        projection.get(
            "presentation_policy_version"
        )
    ):
        _issue(
            issues,
            "invalid_presentation_policy_version",
            "presentation_policy_version",
            "presentation policy version must be non-empty",
        )

    for field in (
        "materialized_at",
        "as_of",
        "source_cutoff",
    ):
        if not _aware_iso_timestamp(
            projection.get(field)
        ):
            _issue(
                issues,
                "invalid_timestamp",
                field,
                "timestamp must be timezone-aware ISO-8601",
            )

    references = projection.get(
        "source_references"
    )

    if not _string_list(references):
        _issue(
            issues,
            "invalid_source_references",
            "source_references",
            "source_references must be a list of non-empty strings",
        )

    if not _non_empty_string(
        projection.get("build_status")
    ):
        _issue(
            issues,
            "invalid_build_status",
            "build_status",
            "build status must be a non-empty string",
        )

    _validate_scope(
        projection.get("scope"),
        issues,
    )

    sections = projection.get("sections")

    if not isinstance(sections, Mapping):
        _issue(
            issues,
            "invalid_sections",
            "sections",
            "sections must be an object",
        )
        return tuple(issues)

    unknown_sections = (
        set(sections)
        - SECTION_KEYS
    )

    for section_name in sorted(
        unknown_sections
    ):
        _issue(
            issues,
            "unknown_section",
            f"sections.{section_name}",
            "section is not part of the D009 executive projection contract",
        )

    missing_sections = (
        required_section_set
        - set(sections)
    )

    for section_name in sorted(
        missing_sections
    ):
        _issue(
            issues,
            "missing_required_section",
            f"sections.{section_name}",
            "required section is missing",
        )

    for section_name, value in sections.items():
        if section_name not in SECTION_KEYS:
            continue

        _validate_section(
            section_name,
            value,
            issues,
            source_reference_required=(
                section_name
                in required_source_set
            ),
        )

    return tuple(issues)


def assert_valid_command_center_projection(
    projection: object,
    *,
    required_sections: Iterable[str] = (),
    required_source_sections: Iterable[str] = (),
) -> None:
    issues = validate_command_center_projection(
        projection,
        required_sections=required_sections,
        required_source_sections=required_source_sections,
    )

    if issues:
        raise ProjectionValidationError(
            issues
        )
