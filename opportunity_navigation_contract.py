"""Pure V3 opportunity deep-link/navigation identity contract.

Slice 7a defines only the canonical read-navigation identity surface needed
before Command Center links can be added.

It does not:
- implement an opportunity store or detail page
- authorize access to an opportunity
- infer identity from ticker or instrument_id
- normalize/fallback to another opportunity
- perform redirects, writes, provider calls or OpenAI calls
- define Command Center navigation or production serving

A later destination route must revalidate the returned identity against the
authoritative opportunity source and enforce authorization.
"""
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import parse_qsl, quote, urlencode, urlsplit

OPPORTUNITY_NAVIGATION_CONTRACT_VERSION = "opportunity_navigation:v1"
OPPORTUNITY_DETAIL_PATH = "/opportunities/detail"
OPPORTUNITY_ID_QUERY_KEY = "opportunity_id"
OPPORTUNITY_PROFILE_QUERY_KEY = "opportunity_profile"
OPPORTUNITY_PROFILES = frozenset({"COMPOUNDER", "CATALYST"})
_CANONICAL_QUERY_KEYS = frozenset({
    OPPORTUNITY_ID_QUERY_KEY,
    OPPORTUNITY_PROFILE_QUERY_KEY,
})
_HEX_DIGITS = frozenset("0123456789abcdefABCDEF")


@dataclass(frozen=True)
class OpportunityNavigationIdentity:
    opportunity_id: str
    opportunity_profile: str


@dataclass(frozen=True)
class OpportunityNavigationIssue:
    code: str
    field: str
    message: str


class OpportunityNavigationError(ValueError):
    def __init__(self, issues):
        self.issues = tuple(issues)
        super().__init__(
            "; ".join(
                f"{issue.field}: {issue.message}"
                for issue in self.issues
            )
        )


def validate_opportunity_navigation_identity(
    *,
    opportunity_id,
    opportunity_profile,
) -> tuple[OpportunityNavigationIssue, ...]:
    """Validate syntax only; do not claim canonical existence."""
    issues = []

    if not isinstance(opportunity_id, str) or not opportunity_id.strip():
        issues.append(
            OpportunityNavigationIssue(
                code="invalid_opportunity_id",
                field=OPPORTUNITY_ID_QUERY_KEY,
                message="opportunity_id must be a non-empty string",
            )
        )

    if (
        not isinstance(opportunity_profile, str)
        or opportunity_profile not in OPPORTUNITY_PROFILES
    ):
        issues.append(
            OpportunityNavigationIssue(
                code="invalid_opportunity_profile",
                field=OPPORTUNITY_PROFILE_QUERY_KEY,
                message=(
                    "opportunity_profile must be COMPOUNDER or CATALYST"
                ),
            )
        )

    return tuple(issues)


def assert_opportunity_navigation_identity(
    *,
    opportunity_id,
    opportunity_profile,
) -> OpportunityNavigationIdentity:
    """Return exact identity values or fail closed; never repair them."""
    issues = validate_opportunity_navigation_identity(
        opportunity_id=opportunity_id,
        opportunity_profile=opportunity_profile,
    )
    if issues:
        raise OpportunityNavigationError(issues)

    return OpportunityNavigationIdentity(
        opportunity_id=opportunity_id,
        opportunity_profile=opportunity_profile,
    )


def build_opportunity_detail_href(
    *,
    opportunity_id,
    opportunity_profile,
) -> str:
    """Build one deterministic internal href from canonical identity."""
    identity = assert_opportunity_navigation_identity(
        opportunity_id=opportunity_id,
        opportunity_profile=opportunity_profile,
    )
    query = urlencode(
        (
            (OPPORTUNITY_ID_QUERY_KEY, identity.opportunity_id),
            (OPPORTUNITY_PROFILE_QUERY_KEY, identity.opportunity_profile),
        ),
        doseq=False,
        safe="",
        quote_via=quote,
    )
    return f"{OPPORTUNITY_DETAIL_PATH}?{query}"


def _validate_percent_encoding(query_string: str) -> None:
    index = 0
    while index < len(query_string):
        if query_string[index] != "%":
            index += 1
            continue
        if (
            index + 2 >= len(query_string)
            or query_string[index + 1] not in _HEX_DIGITS
            or query_string[index + 2] not in _HEX_DIGITS
        ):
            raise OpportunityNavigationError((
                OpportunityNavigationIssue(
                    code="invalid_percent_encoding",
                    field="query",
                    message="query contains malformed percent encoding",
                ),
            ))
        index += 3


def parse_opportunity_detail_query(
    query_string: str | bytes,
) -> OpportunityNavigationIdentity:
    """Parse exactly the v1 canonical identity query, fail closed otherwise."""
    if isinstance(query_string, bytes):
        try:
            query_string = query_string.decode("ascii")
        except UnicodeDecodeError as exc:
            raise OpportunityNavigationError((
                OpportunityNavigationIssue(
                    code="non_ascii_query_bytes",
                    field="query",
                    message="raw query bytes must be ASCII/percent-encoded",
                ),
            )) from exc

    if not isinstance(query_string, str):
        raise TypeError("query_string must be str or bytes")

    _validate_percent_encoding(query_string)

    try:
        pairs = parse_qsl(
            query_string,
            keep_blank_values=True,
            strict_parsing=True,
            encoding="utf-8",
            errors="strict",
            separator="&",
        )
    except (UnicodeDecodeError, ValueError) as exc:
        raise OpportunityNavigationError((
            OpportunityNavigationIssue(
                code="invalid_query_string",
                field="query",
                message="query string is malformed",
            ),
        )) from exc

    values = {}
    issues = []

    for key, value in pairs:
        if key not in _CANONICAL_QUERY_KEYS:
            issues.append(
                OpportunityNavigationIssue(
                    code="unknown_query_key",
                    field=key,
                    message=(
                        "query key is not part of opportunity_navigation:v1"
                    ),
                )
            )
            continue
        if key in values:
            issues.append(
                OpportunityNavigationIssue(
                    code="duplicate_query_key",
                    field=key,
                    message="canonical identity key must appear exactly once",
                )
            )
            continue
        values[key] = value

    for key in (
        OPPORTUNITY_ID_QUERY_KEY,
        OPPORTUNITY_PROFILE_QUERY_KEY,
    ):
        if key not in values:
            issues.append(
                OpportunityNavigationIssue(
                    code="missing_query_key",
                    field=key,
                    message="canonical identity key is required",
                )
            )

    if issues:
        raise OpportunityNavigationError(issues)

    return assert_opportunity_navigation_identity(
        opportunity_id=values[OPPORTUNITY_ID_QUERY_KEY],
        opportunity_profile=values[OPPORTUNITY_PROFILE_QUERY_KEY],
    )


def parse_opportunity_detail_href(
    href: str,
) -> OpportunityNavigationIdentity:
    """Parse an internal opportunity-detail href without redirects."""
    if not isinstance(href, str):
        raise TypeError("href must be str")

    parts = urlsplit(href)
    issues = []

    if parts.scheme or parts.netloc:
        issues.append(
            OpportunityNavigationIssue(
                code="external_href_not_allowed",
                field="href",
                message="canonical detail href must be internal",
            )
        )
    if parts.path != OPPORTUNITY_DETAIL_PATH:
        issues.append(
            OpportunityNavigationIssue(
                code="invalid_detail_path",
                field="href",
                message="href does not use the canonical detail path",
            )
        )
    if parts.fragment:
        issues.append(
            OpportunityNavigationIssue(
                code="fragment_not_allowed",
                field="href",
                message="canonical detail href must not contain a fragment",
            )
        )

    if issues:
        raise OpportunityNavigationError(issues)

    return parse_opportunity_detail_query(parts.query)
