"""Synthetic tests for the pure V3 presentation adapter."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import json
import unittest

from command_center_presentation_adapter import (
    PRESENTATION_VIEW_MODEL_VERSION,
    PROJECTION_PRESENTATION_METADATA_KEYS,
    SECTION_PRESENTATION_ORDER,
    PresentationAdapterError,
    build_command_center_presentation_view_model,
)
from command_center_presentation_payload_contract import (
    PRESENTATION_PAYLOAD_VERSION,
)
from command_center_projection_builder import (
    build_command_center_projection,
)
from command_center_projection_contract import (
    SECTION_KEYS,
)
from command_center_projection_verifier import (
    COMMAND_CENTER_PRESENTATION_POLICY_V1,
)
from test_command_center_presentation_payload_contract import (
    fixtures,
)


POLICY = (
    COMMAND_CENTER_PRESENTATION_POLICY_V1
)


def make_projection(
    *,
    scope=None,
):
    sections = {
        key: {
            "availability": (
                "AVAILABLE"
            ),
            "freshness": (
                "CURRENT"
            ),
            "source_as_of": (
                "2026-09-07T16:59:00+00:00"
            ),
            "source_references": [
                f"fixture:section:{key}"
            ],
            "payload": payload,
        }
        for key, payload
        in fixtures().items()
    }

    return build_command_center_projection(
        command_center_projection_id=(
            "slice6b:synthetic"
        ),
        presentation_policy_version=(
            POLICY.presentation_policy_version
        ),
        materialized_at=(
            "2026-09-07T17:00:00+00:00"
        ),
        as_of=(
            "2026-09-07T17:00:00+00:00"
        ),
        source_cutoff=(
            "2026-09-07T16:59:00+00:00"
        ),
        source_references=[
            "fixture:projection"
        ],
        scope=(
            scope
            or {
                "kind": "GLOBAL",
            }
        ),
        build_status="COMPLETE",
        sections=sections,
    )


def adapt(
    projection,
    *,
    policy=POLICY,
    payload_version=(
        PRESENTATION_PAYLOAD_VERSION
    ),
):
    return (
        build_command_center_presentation_view_model(
            projection,
            presentation_policy=policy,
            payload_version=(
                payload_version
            ),
        )
    )


class PresentationAdapterTests(
    unittest.TestCase
):
    def test_valid_projection_builds_view_model(
        self,
    ):
        projection = make_projection()

        result = adapt(
            projection
        )

        self.assertEqual(
            result[
                "view_model_version"
            ],
            PRESENTATION_VIEW_MODEL_VERSION,
        )

        self.assertEqual(
            result[
                "payload_version"
            ],
            PRESENTATION_PAYLOAD_VERSION,
        )

        self.assertEqual(
            result[
                "section_order"
            ],
            list(
                SECTION_PRESENTATION_ORDER
            ),
        )

        self.assertEqual(
            set(
                result["sections"]
            ),
            SECTION_KEYS,
        )

        self.assertEqual(
            result[
                "verification_warnings"
            ],
            [],
        )

    def test_adapter_does_not_mutate_projection(
        self,
    ):
        projection = make_projection()
        before = deepcopy(
            projection
        )

        adapt(
            projection
        )

        self.assertEqual(
            projection,
            before,
        )

    def test_deterministic_same_projection(
        self,
    ):
        projection = make_projection()

        first = adapt(
            projection
        )
        second = adapt(
            projection
        )

        self.assertEqual(
            first,
            second,
        )

    def test_case_order_preserved_without_truncation(
        self,
    ):
        projection = make_projection()

        first = projection[
            "sections"
        ][
            "compounder_opportunities"
        ][
            "payload"
        ][0]

        second = deepcopy(
            first
        )

        second[
            "opportunity_id"
        ] = "fixture:case:second"

        projection[
            "sections"
        ][
            "compounder_opportunities"
        ][
            "payload"
        ] = [
            first,
            second,
        ]

        result = adapt(
            projection
        )

        observed = [
            item[
                "opportunity_id"
            ]
            for item in result[
                "sections"
            ][
                "compounder_opportunities"
            ][
                "payload"
            ]
        ]

        self.assertEqual(
            observed,
            [
                first[
                    "opportunity_id"
                ],
                second[
                    "opportunity_id"
                ],
            ],
        )

    def test_three_cases_remain_slice4_error(
        self,
    ):
        projection = make_projection()

        base = projection[
            "sections"
        ][
            "compounder_opportunities"
        ][
            "payload"
        ][0]

        projection[
            "sections"
        ][
            "compounder_opportunities"
        ][
            "payload"
        ] = [
            dict(
                base,
                opportunity_id=(
                    f"fixture:case:{index}"
                ),
            )
            for index in range(3)
        ]

        with self.assertRaises(
            PresentationAdapterError
        ) as caught:
            adapt(
                projection
            )

        self.assertIn(
            "executive_opportunity_limit_exceeded",
            {
                issue.code
                for issue
                in caught.exception.issues
            },
        )

    def test_profile_mismatch_remains_blocking(
        self,
    ):
        projection = make_projection()

        projection[
            "sections"
        ][
            "compounder_opportunities"
        ][
            "payload"
        ][0][
            "opportunity_profile"
        ] = "CATALYST"

        with self.assertRaises(
            PresentationAdapterError
        ) as caught:
            adapt(
                projection
            )

        self.assertIn(
            "opportunity_profile_mismatch",
            {
                issue.code
                for issue
                in caught.exception.issues
            },
        )

    def test_cross_profile_collision_blocked(
        self,
    ):
        projection = make_projection()

        opportunity_id = (
            projection[
                "sections"
            ][
                "compounder_opportunities"
            ][
                "payload"
            ][0][
                "opportunity_id"
            ]
        )

        projection[
            "sections"
        ][
            "catalyst_opportunities"
        ][
            "payload"
        ][0][
            "opportunity_id"
        ] = opportunity_id

        with self.assertRaises(
            PresentationAdapterError
        ) as caught:
            adapt(
                projection
            )

        self.assertIn(
            (
                "cross_profile_"
                "opportunity_identity_collision"
            ),
            {
                issue.code
                for issue
                in caught.exception.issues
            },
        )

    def test_same_profile_duplicate_not_silently_deduped(
        self,
    ):
        projection = make_projection()

        item = projection[
            "sections"
        ][
            "compounder_opportunities"
        ][
            "payload"
        ][0]

        projection[
            "sections"
        ][
            "compounder_opportunities"
        ][
            "payload"
        ].append(
            deepcopy(
                item
            )
        )

        result = adapt(
            projection
        )

        self.assertEqual(
            len(
                result[
                    "sections"
                ][
                    "compounder_opportunities"
                ][
                    "payload"
                ]
            ),
            2,
        )

        self.assertIn(
            "duplicate_executive_opportunity_id",
            {
                warning["code"]
                for warning
                in result[
                    "verification_warnings"
                ]
            },
        )

    def test_payload_shape_error_fails_closed(
        self,
    ):
        projection = make_projection()

        del projection[
            "sections"
        ][
            "compounder_opportunities"
        ][
            "payload"
        ][0][
            "instrument_label"
        ]

        with self.assertRaises(
            PresentationAdapterError
        ) as caught:
            adapt(
                projection
            )

        self.assertIn(
            "missing_payload_field",
            {
                issue.code
                for issue
                in caught.exception.issues
            },
        )

        self.assertTrue(
            all(
                issue.layer == "payload"
                for issue
                in caught.exception.issues
            )
        )

    def test_unavailable_missing_payload_preserved(
        self,
    ):
        projection = make_projection()

        section = projection[
            "sections"
        ][
            "market_context"
        ]

        section[
            "availability"
        ] = "UNAVAILABLE"
        section[
            "freshness"
        ] = "UNKNOWN"
        section[
            "source_as_of"
        ] = None
        section[
            "source_references"
        ] = []

        del section[
            "payload"
        ]

        result = adapt(
            projection
        )

        view = result[
            "sections"
        ][
            "market_context"
        ]

        self.assertFalse(
            view[
                "payload_present"
            ]
        )

        self.assertIsNone(
            view["payload"]
        )

        self.assertFalse(
            view[
                "has_content"
            ]
        )

        self.assertEqual(
            view[
                "availability"
            ],
            "UNAVAILABLE",
        )

    def test_explicit_null_payload_remains_distinguishable(
        self,
    ):
        projection = make_projection()

        section = projection[
            "sections"
        ][
            "portfolio_relevance"
        ]

        section[
            "availability"
        ] = "UNAVAILABLE"
        section[
            "freshness"
        ] = "UNKNOWN"
        section[
            "source_as_of"
        ] = None
        section[
            "source_references"
        ] = []
        section[
            "payload"
        ] = None

        result = adapt(
            projection
        )

        view = result[
            "sections"
        ][
            "portfolio_relevance"
        ]

        self.assertTrue(
            view[
                "payload_present"
            ]
        )

        self.assertIsNone(
            view["payload"]
        )

        self.assertFalse(
            view[
                "has_content"
            ]
        )

    def test_stale_state_and_timestamp_preserved(
        self,
    ):
        projection = make_projection()

        section = projection[
            "sections"
        ][
            "attention"
        ]

        section[
            "freshness"
        ] = "STALE"

        before = deepcopy(
            section
        )

        result = adapt(
            projection
        )

        view = result[
            "sections"
        ][
            "attention"
        ]

        self.assertEqual(
            view[
                "freshness"
            ],
            "STALE",
        )

        self.assertEqual(
            view[
                "source_as_of"
            ],
            before[
                "source_as_of"
            ],
        )

    def test_partial_state_not_interpreted_as_business_state(
        self,
    ):
        projection = make_projection()

        projection[
            "sections"
        ][
            "attention"
        ][
            "availability"
        ] = "PARTIAL"

        result = adapt(
            projection
        )

        self.assertEqual(
            result[
                "sections"
            ][
                "attention"
            ][
                "availability"
            ],
            "PARTIAL",
        )

        self.assertTrue(
            result[
                "sections"
            ][
                "attention"
            ][
                "has_content"
            ],
        )

    def test_zero_cases_are_empty_not_generated(
        self,
    ):
        projection = make_projection()

        for key in (
            "compounder_opportunities",
            "catalyst_opportunities",
        ):
            projection[
                "sections"
            ][key][
                "payload"
            ] = []

        result = adapt(
            projection
        )

        for key in (
            "compounder_opportunities",
            "catalyst_opportunities",
        ):
            view = result[
                "sections"
            ][key]

            self.assertEqual(
                view["payload"],
                [],
            )

            self.assertFalse(
                view[
                    "has_content"
                ]
            )

    def test_empty_summary_is_not_filled(
        self,
    ):
        projection = make_projection()

        projection[
            "sections"
        ][
            "executive_decision_summary"
        ][
            "payload"
        ][
            "points"
        ] = []

        result = adapt(
            projection
        )

        view = result[
            "sections"
        ][
            "executive_decision_summary"
        ]

        self.assertEqual(
            view[
                "payload"
            ][
                "points"
            ],
            [],
        )

        self.assertFalse(
            view[
                "has_content"
            ]
        )

    def test_personal_scope_preserved(
        self,
    ):
        projection = make_projection(
            scope={
                "kind": "PERSONAL",
                "scope_id": (
                    "fixture:principal:1"
                ),
            }
        )

        result = adapt(
            projection
        )

        self.assertEqual(
            result[
                "projection"
            ][
                "scope"
            ],
            {
                "kind": "PERSONAL",
                "scope_id": (
                    "fixture:principal:1"
                ),
            },
        )

    def test_unknown_top_level_projection_metadata_not_exposed(
        self,
    ):
        projection = make_projection()

        expected_metadata = {
            key
            for key
            in PROJECTION_PRESENTATION_METADATA_KEYS
            if key in projection
        }

        projection[
            "fixture_internal_extension"
        ] = {
            "opaque": (
                "must-not-become-template-data"
            ),
        }

        result = adapt(
            projection
        )

        self.assertNotIn(
            "fixture_internal_extension",
            result[
                "projection"
            ],
        )

        self.assertEqual(
            set(
                result[
                    "projection"
                ]
            ),
            expected_metadata,
        )

    def test_unknown_section_metadata_not_exposed(
        self,
    ):
        projection = make_projection()

        projection[
            "sections"
        ][
            "attention"
        ][
            "fixture_internal_extension"
        ] = (
            "must-not-become-template-data"
        )

        result = adapt(
            projection
        )

        self.assertNotIn(
            "fixture_internal_extension",
            result[
                "sections"
            ][
                "attention"
            ],
        )

    def test_future_payload_version_fails_closed(
        self,
    ):
        projection = make_projection()

        with self.assertRaises(
            ValueError
        ):
            adapt(
                projection,
                payload_version=(
                    "command_center_"
                    "presentation_payload:v2"
                ),
            )

    def test_invalid_presentation_policy_fails_closed(
        self,
    ):
        projection = make_projection()

        future = replace(
            POLICY,
            presentation_policy_version=(
                "command_center_"
                "presentation:v2"
            ),
        )

        with self.assertRaises(
            ValueError
        ):
            adapt(
                projection,
                policy=future,
            )

    def test_view_model_json_safe(
        self,
    ):
        result = adapt(
            make_projection()
        )

        encoded = json.dumps(
            result,
            sort_keys=True,
            allow_nan=False,
        )

        self.assertTrue(
            encoded
        )

    def test_html_like_text_remains_plain_data(
        self,
    ):
        projection = make_projection()

        value = (
            '<script>'
            'alert("fixture")'
            '</script>'
        )

        projection[
            "sections"
        ][
            "attention"
        ][
            "payload"
        ][0][
            "title"
        ] = value

        result = adapt(
            projection
        )

        observed = result[
            "sections"
        ][
            "attention"
        ][
            "payload"
        ][0][
            "title"
        ]

        self.assertIs(
            type(
                observed
            ),
            str,
        )

        self.assertEqual(
            observed,
            value,
        )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )
