"""Pure V3 opportunity-detail resolution contract.

This module defines only the read-source outcome consumed by a later detail
route. Authorization, persistence, routing, templates, business logic,
providers, OpenAI, refresh and identity fallback are outside this contract.

FOUND/NOT_FOUND/UNAVAILABLE are read-path states, never lifecycle or
investment states. NOT_FOUND may only be returned by a source that
authoritatively established absence; source failure/unavailability is
UNAVAILABLE.
"""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass
from types import MappingProxyType
from typing import cast

from opportunity_navigation_contract import (
    OpportunityNavigationIdentity,
    assert_opportunity_navigation_identity,
)


OPPORTUNITY_DETAIL_RESOLUTION_CONTRACT_VERSION = "opportunity_detail_resolution:v1"
FOUND = "FOUND"
NOT_FOUND = "NOT_FOUND"
UNAVAILABLE = "UNAVAILABLE"
OPPORTUNITY_DETAIL_RESOLUTION_STATUSES = frozenset({FOUND, NOT_FOUND, UNAVAILABLE})


@dataclass(frozen=True)
class OpportunityDetailResolutionIssue:
    code: str
    path: str
    message: str


@dataclass(frozen=True)
class OpportunityDetailResolution:
    status: str
    identity: OpportunityNavigationIdentity
    canonical_opportunity: Mapping[str, object] | None

    def __post_init__(self) -> None:
        if self.canonical_opportunity is None:
            return
        object.__setattr__(
            self,
            "canonical_opportunity",
            cast(
                Mapping[str, object],
                _freeze_payload_value(self.canonical_opportunity),
            ),
        )


class OpportunityDetailResolutionError(ValueError):
    def __init__(self, issues: tuple[OpportunityDetailResolutionIssue, ...]) -> None:
        self.issues = issues
        super().__init__("; ".join(f"{x.path}: {x.message}" for x in issues))


def _freeze_payload_value(value: object) -> object:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {
                deepcopy(key): _freeze_payload_value(item)
                for key, item in value.items()
            }
        )
    if isinstance(value, list):
        return tuple(_freeze_payload_value(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze_payload_value(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze_payload_value(item) for item in value)
    if isinstance(value, frozenset):
        return frozenset(_freeze_payload_value(item) for item in value)
    return deepcopy(value)


def validate_opportunity_detail_resolution(
    resolution: object,
) -> tuple[OpportunityDetailResolutionIssue, ...]:
    if not isinstance(resolution, OpportunityDetailResolution):
        return (
            OpportunityDetailResolutionIssue(
                "invalid_resolution_type",
                "resolution",
                "resolution must be OpportunityDetailResolution",
            ),
        )

    issues: list[OpportunityDetailResolutionIssue] = []

    if not isinstance(resolution.identity, OpportunityNavigationIdentity):
        issues.append(
            OpportunityDetailResolutionIssue(
                "invalid_identity_type",
                "identity",
                "identity must be OpportunityNavigationIdentity",
            )
        )
    else:
        try:
            assert_opportunity_navigation_identity(
                opportunity_id=resolution.identity.opportunity_id,
                opportunity_profile=resolution.identity.opportunity_profile,
            )
        except Exception:
            issues.append(
                OpportunityDetailResolutionIssue(
                    "invalid_navigation_identity",
                    "identity",
                    "identity violates the locked navigation contract",
                )
            )

    if (
        not isinstance(resolution.status, str)
        or resolution.status not in OPPORTUNITY_DETAIL_RESOLUTION_STATUSES
    ):
        issues.append(
            OpportunityDetailResolutionIssue(
                "unknown_resolution_status",
                "status",
                "unknown detail-resolution status",
            )
        )
        return tuple(issues)

    payload = resolution.canonical_opportunity

    if resolution.status == FOUND:
        if not isinstance(payload, Mapping):
            issues.append(
                OpportunityDetailResolutionIssue(
                    "found_requires_payload",
                    "canonical_opportunity",
                    "FOUND requires a canonical opportunity mapping",
                )
            )
            return tuple(issues)

        if isinstance(resolution.identity, OpportunityNavigationIdentity):
            if payload.get("opportunity_id") != resolution.identity.opportunity_id:
                issues.append(
                    OpportunityDetailResolutionIssue(
                        "opportunity_id_mismatch",
                        "canonical_opportunity.opportunity_id",
                        "payload identity must match requested opportunity_id",
                    )
                )
            if (
                payload.get("opportunity_profile")
                != resolution.identity.opportunity_profile
            ):
                issues.append(
                    OpportunityDetailResolutionIssue(
                        "opportunity_profile_mismatch",
                        "canonical_opportunity.opportunity_profile",
                        "payload profile must match requested profile",
                    )
                )
    elif payload is not None:
        issues.append(
            OpportunityDetailResolutionIssue(
                "non_found_status_has_payload",
                "canonical_opportunity",
                "NOT_FOUND/UNAVAILABLE must not carry opportunity data",
            )
        )

    return tuple(issues)


def assert_opportunity_detail_resolution(
    resolution: object,
) -> OpportunityDetailResolution:
    issues = validate_opportunity_detail_resolution(resolution)
    if issues:
        raise OpportunityDetailResolutionError(issues)
    return cast(OpportunityDetailResolution, resolution)


def build_opportunity_detail_resolution(
    *,
    status: str,
    identity: OpportunityNavigationIdentity,
    canonical_opportunity: Mapping[str, object] | None = None,
) -> OpportunityDetailResolution:
    payload = (
        None
        if canonical_opportunity is None
        else cast(
            Mapping[str, object],
            _freeze_payload_value(canonical_opportunity),
        )
    )
    return assert_opportunity_detail_resolution(
        OpportunityDetailResolution(
            status=status,
            identity=identity,
            canonical_opportunity=payload,
        )
    )
