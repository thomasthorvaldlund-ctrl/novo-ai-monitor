from __future__ import annotations

import ast
from pathlib import Path
import unittest

from opportunity_navigation_contract import (
    build_opportunity_detail_href,
    parse_opportunity_detail_href,
)
from opportunity_detail_resolution_contract import (
    FOUND,
    NOT_FOUND,
    UNAVAILABLE,
    OPPORTUNITY_DETAIL_RESOLUTION_CONTRACT_VERSION,
    OPPORTUNITY_DETAIL_RESOLUTION_STATUSES,
    OpportunityDetailResolution,
    OpportunityDetailResolutionError,
    assert_opportunity_detail_resolution,
    build_opportunity_detail_resolution,
    validate_opportunity_detail_resolution,
)


def identity(opportunity_id="case:one", profile="COMPOUNDER"):
    return parse_opportunity_detail_href(
        build_opportunity_detail_href(
            opportunity_id=opportunity_id,
            opportunity_profile=profile,
        )
    )


class OpportunityDetailResolutionTests(unittest.TestCase):
    def test_locked_v1_constants(self):
        self.assertEqual(
            OPPORTUNITY_DETAIL_RESOLUTION_CONTRACT_VERSION,
            "opportunity_detail_resolution:v1",
        )
        self.assertEqual(
            OPPORTUNITY_DETAIL_RESOLUTION_STATUSES,
            frozenset({"FOUND", "NOT_FOUND", "UNAVAILABLE"}),
        )
        self.assertNotIn("UNAUTHORIZED", OPPORTUNITY_DETAIL_RESOLUTION_STATUSES)

    def test_found_matching_identity(self):
        result = build_opportunity_detail_resolution(
            status=FOUND,
            identity=identity(),
            canonical_opportunity={
                "opportunity_id": "case:one",
                "opportunity_profile": "COMPOUNDER",
                "lifecycle_status": "CANDIDATE",
            },
        )
        self.assertEqual(result.status, FOUND)
        self.assertEqual(
            result.canonical_opportunity["lifecycle_status"],
            "CANDIDATE",
        )

    def test_compounder_and_catalyst_remain_separate(self):
        results = []
        for profile in ("COMPOUNDER", "CATALYST"):
            case_id = f"case:{profile.lower()}"
            results.append(
                build_opportunity_detail_resolution(
                    status=FOUND,
                    identity=identity(case_id, profile),
                    canonical_opportunity={
                        "opportunity_id": case_id,
                        "opportunity_profile": profile,
                    },
                )
            )
        self.assertNotEqual(results[0].identity, results[1].identity)

    def test_found_rejects_missing_or_wrong_identity_payload(self):
        cases = (
            None,
            {
                "opportunity_id": "other",
                "opportunity_profile": "COMPOUNDER",
            },
            {
                "opportunity_id": "case:one",
                "opportunity_profile": "CATALYST",
            },
        )
        for payload in cases:
            with self.subTest(payload=payload):
                with self.assertRaises(OpportunityDetailResolutionError):
                    build_opportunity_detail_resolution(
                        status=FOUND,
                        identity=identity(),
                        canonical_opportunity=payload,
                    )

    def test_not_found_and_unavailable_are_payload_free(self):
        for status in (NOT_FOUND, UNAVAILABLE):
            with self.subTest(status=status):
                result = build_opportunity_detail_resolution(
                    status=status,
                    identity=identity(),
                )
                self.assertIsNone(result.canonical_opportunity)
                with self.assertRaises(OpportunityDetailResolutionError):
                    build_opportunity_detail_resolution(
                        status=status,
                        identity=identity(),
                        canonical_opportunity={
                            "opportunity_id": "case:one",
                            "opportunity_profile": "COMPOUNDER",
                        },
                    )

    def test_malformed_nonstring_status_rejected_without_crash(self):
        for status in (None, 123, [], {}, set()):
            with self.subTest(status=repr(status)):
                raw = OpportunityDetailResolution(
                    status=status,
                    identity=identity(),
                    canonical_opportunity=None,
                )
                codes = {
                    issue.code
                    for issue in validate_opportunity_detail_resolution(raw)
                }
                self.assertIn("unknown_resolution_status", codes)

                with self.assertRaises(OpportunityDetailResolutionError):
                    build_opportunity_detail_resolution(
                        status=status,
                        identity=identity(),
                    )

    def test_unknown_authorization_like_status_rejected(self):
        for status in ("UNAUTHORIZED", "FORBIDDEN", "MISSING"):
            with self.subTest(status=status):
                with self.assertRaises(OpportunityDetailResolutionError):
                    build_opportunity_detail_resolution(
                        status=status,
                        identity=identity(),
                    )

    def test_caller_payload_mutation_isolated(self):
        payload = {
            "opportunity_id": "case:one",
            "opportunity_profile": "COMPOUNDER",
            "nested": {"value": 1},
        }
        result = build_opportunity_detail_resolution(
            status=FOUND,
            identity=identity(),
            canonical_opportunity=payload,
        )
        payload["nested"]["value"] = 999
        self.assertEqual(
            result.canonical_opportunity["nested"]["value"],
            1,
        )

    def test_returned_payload_nested_containers_are_immutable(self):
        result = build_opportunity_detail_resolution(
            status=FOUND,
            identity=identity(),
            canonical_opportunity={
                "opportunity_id": "case:one",
                "opportunity_profile": "COMPOUNDER",
                "nested": {
                    "items": [{"value": 1}],
                    "tags": {"alpha", "beta"},
                },
            },
        )

        with self.assertRaises(TypeError):
            result.canonical_opportunity["new"] = "blocked"

        with self.assertRaises(TypeError):
            result.canonical_opportunity[
                "nested"
            ]["items"][0]["value"] = 2

        with self.assertRaises(AttributeError):
            result.canonical_opportunity[
                "nested"
            ]["items"].append({"value": 2})

        with self.assertRaises(AttributeError):
            result.canonical_opportunity[
                "nested"
            ]["tags"].add("gamma")

        self.assertEqual(
            result.canonical_opportunity[
                "nested"
            ]["items"][0]["value"],
            1,
        )

    def test_direct_construction_freezes_payload_before_validation(self):
        payload = {
            "opportunity_id": "case:one",
            "opportunity_profile": "COMPOUNDER",
            "nested": {"value": 1},
        }
        raw = OpportunityDetailResolution(
            status=FOUND,
            identity=identity(),
            canonical_opportunity=payload,
        )

        self.assertEqual(
            validate_opportunity_detail_resolution(raw),
            (),
        )
        self.assertIs(
            assert_opportunity_detail_resolution(raw),
            raw,
        )

        payload["nested"]["value"] = 999
        self.assertEqual(
            raw.canonical_opportunity["nested"]["value"],
            1,
        )

        with self.assertRaises(TypeError):
            raw.canonical_opportunity[
                "nested"
            ]["value"] = 2

    def test_validator_reports_cross_entity_mismatch(self):
        raw = OpportunityDetailResolution(
            status=FOUND,
            identity=identity(),
            canonical_opportunity={
                "opportunity_id": "other",
                "opportunity_profile": "CATALYST",
            },
        )
        codes = {
            issue.code
            for issue in validate_opportunity_detail_resolution(raw)
        }
        self.assertEqual(
            codes,
            {"opportunity_id_mismatch", "opportunity_profile_mismatch"},
        )

    def test_no_hidden_route_network_or_business_dependency(self):
        tree = ast.parse(
            Path("opportunity_detail_resolution_contract.py").read_text(
                encoding="utf-8"
            )
        )
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module or "")
        joined = "\n".join(imports).lower()
        for forbidden in (
            "flask",
            "openai",
            "requests",
            "yfinance",
            "feedparser",
            "portfolio",
            "command_center",
        ):
            self.assertNotIn(forbidden, joined)

    def test_contract_does_not_choose_http_status(self):
        text = Path(
            "opportunity_detail_resolution_contract.py"
        ).read_text(encoding="utf-8")
        for literal in ("400", "401", "403", "404", "410", "503"):
            self.assertNotIn(literal, text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
