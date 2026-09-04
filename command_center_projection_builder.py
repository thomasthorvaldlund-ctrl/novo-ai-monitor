"""
Pure in-memory V3 Command Center projection builder.

Slice 2 assembles an explicitly supplied candidate projection and validates
it through the Slice-1 contract.

It performs no filesystem I/O, cache publication, provider/OpenAI calls,
route integration or business mutation. It also does not derive rankings,
scores, confidence, lifecycle, freshness, timestamps or fallback values.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Iterable, Mapping

from command_center_projection_contract import (
    COMMAND_CENTER_PROJECTION_SCHEMA_VERSION,
    assert_valid_command_center_projection,
)


def build_command_center_projection(
    *,
    command_center_projection_id: str,
    presentation_policy_version: str,
    materialized_at: str,
    as_of: str,
    source_cutoff: str,
    source_references: list[str],
    scope: Mapping[str, object],
    build_status: str,
    sections: Mapping[str, object],
    required_sections: Iterable[str] = (),
    required_source_sections: Iterable[str] = (),
) -> dict[str, object]:
    """
    Build and validate one V1 projection entirely in memory.

    All business/presentation facts are supplied by the caller.
    This function only assembles a defensive copy of those inputs,
    adds the locked schema identity and validates the resulting envelope.
    """

    projection: dict[str, object] = {
        "command_center_projection_id":
            deepcopy(
                command_center_projection_id
            ),
        "schema_version":
            COMMAND_CENTER_PROJECTION_SCHEMA_VERSION,
        "presentation_policy_version":
            deepcopy(
                presentation_policy_version
            ),
        "materialized_at":
            deepcopy(materialized_at),
        "as_of":
            deepcopy(as_of),
        "source_cutoff":
            deepcopy(source_cutoff),
        "source_references":
            deepcopy(source_references),
        "scope":
            deepcopy(scope),
        "build_status":
            deepcopy(build_status),
        "sections":
            deepcopy(sections),
    }

    assert_valid_command_center_projection(
        projection,
        required_sections=required_sections,
        required_source_sections=(
            required_source_sections
        ),
    )

    return projection
