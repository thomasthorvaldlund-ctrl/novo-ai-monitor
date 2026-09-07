"""Proposed Slice-6a presentation payload contract, version 1.

This is shape validation, not a new canonical/business model. Field names
below are implementation choices. Existing envelope, scope, freshness,
profile-identity and evidence checks remain authoritative upstream.

Values are never calculated, formatted, renamed, defaulted or mutated.
item_id is a presentation identifier, not a substitute for a canonical event
identity. References are opaque supplied strings; they are not resolved here.
This module does not build a projection, resolve evidence, select visible
cases or integrate with the store, HTTP route or templates.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

PRESENTATION_PAYLOAD_VERSION = "command_center_presentation_payload:v1"
SUPPORTED_PRESENTATION_POLICY_VERSION = "command_center_presentation:v1"
MISSING_PAYLOAD = object()

# Tuples keep this proposed v1 field contract read-only by ordinary use.
_TEXT_ITEM = (
    ("item_id", "text"),
    ("title", "nullable_text"),
    ("text", "nullable_text"),
    ("source_references", "references"),
)
_CARD = (
    ("opportunity_id", "text"),
    ("opportunity_profile", "text"),
    ("instrument_id", "text"),
    ("instrument_label", "nullable_text"),
    ("lifecycle", "nullable_text"),
    ("opportunity_score", "nullable_value"),
    ("ai_confidence", "nullable_value"),
    ("data_confidence", "nullable_value"),
    ("why_now", "nullable_text"),
    ("critical_blockers", "nullable_references"),
    ("source_references", "references"),
)
_SCHEMAS = (
    ("page_context", "object", (
        ("title", "text"), ("description", "nullable_text"),
    )),
    ("attention", "items", _TEXT_ITEM),
    ("executive_decision_summary", "object", (
        ("points", "references"),
        ("source_references", "references"),
    )),
    ("compounder_opportunities", "items", _CARD),
    ("catalyst_opportunities", "items", _CARD),
    ("portfolio_relevance", "items", _TEXT_ITEM + (
        ("instrument_id", "nullable_text"),
        ("opportunity_id", "nullable_text"),
        ("portfolio_fit", "nullable_value"),
    )),
    ("what_changed", "items", _TEXT_ITEM + (
        ("record_reference", "nullable_text"),
    )),
    ("market_context", "items", _TEXT_ITEM),
    ("trust_data_system_state", "items", _TEXT_ITEM),
)
PRESENTATION_SECTION_KEYS = frozenset(row[0] for row in _SCHEMAS)


@dataclass(frozen=True)
class PresentationPayloadIssue:
    code: str
    path: str
    message: str


class PresentationPayloadError(ValueError):
    def __init__(self, issues):
        self.issues = tuple(issues)
        super().__init__("; ".join(
            f"{issue.path}: {issue.message}" for issue in self.issues
        ))


def _text(value):
    return type(value) is str and bool(value.strip())


def _value_matches(kind, value):
    if kind.startswith("nullable_"):
        if value is None:
            return True
        kind = kind[len("nullable_"):]
    if kind == "text":
        return _text(value)
    if kind == "references":
        # Empty is explicit lack of references, NOT proof of evidence.
        return type(value) is list and all(_text(x) for x in value)
    if kind == "value":
        # Do not invent confidence scales or convert labels into numbers.
        return (_text(value) or type(value) is int
                or (type(value) is float and isfinite(value)))
    raise ValueError("Unknown internal field type")


def _check_object(value, fields, path, issues):
    def add(code, suffix, message):
        issues.append(PresentationPayloadIssue(code, path + suffix, message))

    if type(value) is not dict:
        add("invalid_payload_object", "", "Expected a JSON object")
        return
    if any(type(key) is not str for key in value):
        add("non_string_payload_key", "", "Object keys must be strings")
        return
    names = frozenset(name for name, _ in fields)
    for key in sorted(set(value) - names):
        add("unexpected_payload_field", "." + key,
            "Field is not part of this presentation payload version")
    for name, kind in fields:
        if name not in value:
            add("missing_payload_field", "." + name,
                "Required field is absent; use explicit null where allowed")
        elif not _value_matches(kind, value[name]):
            add("invalid_payload_field", "." + name,
                f"Expected {kind}; values are not coerced")
    if ("title" in names and "text" in names
            and value.get("title") is None and value.get("text") is None):
        add("empty_text_item", "", "Supply a title or text, not a blank item")


def validate_presentation_payload(
    section_key: str,
    payload: object,
    *,
    availability: str,
    payload_version: str,
    presentation_policy_version: str,
) -> tuple[PresentationPayloadIssue, ...]:
    """Validate one present section's payload without changing its data.

    Missing sections are handled by the future presentation adapter, not
    inferred here. Pass MISSING_PAYLOAD when a present section has no payload.
    This v1 supports only the initial v1 presentation policy. A future policy
    requires explicit support; it is never silently interpreted as v1.

    A successful result does NOT establish authorization, source validity,
    freshness eligibility, canonical lifecycle or full D009 compliance.
    """
    if payload_version != PRESENTATION_PAYLOAD_VERSION:
        raise ValueError("Unsupported presentation payload version")
    if presentation_policy_version != SUPPORTED_PRESENTATION_POLICY_VERSION:
        raise ValueError("Unsupported presentation policy version")
    if type(section_key) is not str or section_key not in PRESENTATION_SECTION_KEYS:
        raise ValueError("Unknown presentation section")
    if type(availability) is not str or availability not in (
        "AVAILABLE", "PARTIAL", "UNAVAILABLE",
    ):
        raise ValueError("Unknown section availability")

    _, shape, fields = next(row for row in _SCHEMAS if row[0] == section_key)
    path = f"sections.{section_key}.payload"
    issues = []
    if availability == "UNAVAILABLE":
        empty_container = (
            (type(payload) is list and not payload)
            or (shape == "object" and type(payload) is dict and not payload)
        )
        if payload is not MISSING_PAYLOAD and payload is not None and not empty_container:
            issues.append(PresentationPayloadIssue(
                "unavailable_payload_has_content", path,
                "Unavailable content must not be offered as displayable facts",
            ))
        return tuple(issues)

    if payload is MISSING_PAYLOAD or payload is None:
        return (PresentationPayloadIssue(
            "missing_display_payload", path,
            "An available/partial section needs its explicitly materialized payload",
        ),)
    if shape == "object":
        _check_object(payload, fields, path, issues)
        if (section_key == "executive_decision_summary" and type(payload) is dict
                and type(payload.get("points")) is list and len(payload["points"]) > 3):
            issues.append(PresentationPayloadIssue(
                "summary_v1_limit_exceeded", path + ".points",
                "Presentation policy v1 permits at most three summary points",
            ))
    elif type(payload) is not list:
        issues.append(PresentationPayloadIssue(
            "invalid_payload_list", path, "Expected an explicitly materialized list",
        ))
    else:
        for index, item in enumerate(payload):
            _check_object(item, fields, f"{path}[{index}]", issues)

    # Case counts, profile identity and duplicate severity are intentionally
    # NOT reimplemented here: the Slice-4 verifier remains authoritative.
    return tuple(issues)


def assert_valid_presentation_payload(section_key, payload, **configuration):
    issues = validate_presentation_payload(section_key, payload, **configuration)
    if issues:
        raise PresentationPayloadError(issues)
