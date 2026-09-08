"""Tests for the pure V3 opportunity navigation identity contract."""
from __future__ import annotations

import ast
from pathlib import Path
from urllib.parse import urlsplit
import unittest

from opportunity_navigation_contract import (
    OPPORTUNITY_DETAIL_PATH,
    OPPORTUNITY_ID_QUERY_KEY,
    OPPORTUNITY_NAVIGATION_CONTRACT_VERSION,
    OPPORTUNITY_PROFILE_QUERY_KEY,
    OPPORTUNITY_PROFILES,
    OpportunityNavigationError,
    OpportunityNavigationIdentity,
    assert_opportunity_navigation_identity,
    build_opportunity_detail_href,
    parse_opportunity_detail_href,
    parse_opportunity_detail_query,
    validate_opportunity_navigation_identity,
)


class OpportunityNavigationContractTests(unittest.TestCase):
    def test_locked_v1_constants(self):
        self.assertEqual(
            OPPORTUNITY_NAVIGATION_CONTRACT_VERSION,
            "opportunity_navigation:v1",
        )
        self.assertEqual(OPPORTUNITY_DETAIL_PATH, "/opportunities/detail")
        self.assertEqual(OPPORTUNITY_ID_QUERY_KEY, "opportunity_id")
        self.assertEqual(
            OPPORTUNITY_PROFILE_QUERY_KEY,
            "opportunity_profile",
        )
        self.assertEqual(
            OPPORTUNITY_PROFILES,
            frozenset({"COMPOUNDER", "CATALYST"}),
        )

    def test_both_profiles_are_valid(self):
        for profile in ("COMPOUNDER", "CATALYST"):
            with self.subTest(profile=profile):
                identity = assert_opportunity_navigation_identity(
                    opportunity_id="opportunity:123",
                    opportunity_profile=profile,
                )
                self.assertEqual(
                    identity,
                    OpportunityNavigationIdentity(
                        opportunity_id="opportunity:123",
                        opportunity_profile=profile,
                    ),
                )

    def test_profile_is_not_normalized(self):
        issues = validate_opportunity_navigation_identity(
            opportunity_id="case-1",
            opportunity_profile="compounder",
        )
        self.assertEqual(
            [issue.code for issue in issues],
            ["invalid_opportunity_profile"],
        )
        with self.assertRaises(OpportunityNavigationError):
            build_opportunity_detail_href(
                opportunity_id="case-1",
                opportunity_profile="compounder",
            )

    def test_blank_identity_rejected_without_repair(self):
        for value in ("", " ", "\t", "\n"):
            with self.subTest(opportunity_id=repr(value)):
                with self.assertRaises(OpportunityNavigationError):
                    build_opportunity_detail_href(
                        opportunity_id=value,
                        opportunity_profile="COMPOUNDER",
                    )

    def test_ticker_or_instrument_alone_is_not_identity(self):
        for query in (
            "ticker=NOVO-B",
            "instrument_id=DK0062498333",
            "instrument_id=fixture%3A1&opportunity_profile=COMPOUNDER",
            "ticker=NOVO-B&opportunity_id=case-1",
        ):
            with self.subTest(query=query):
                with self.assertRaises(OpportunityNavigationError):
                    parse_opportunity_detail_query(query)

    def test_reserved_unicode_identity_roundtrip(self):
        opportunity_id = "case:abc/def?x=1 & æøå ü %"
        href = build_opportunity_detail_href(
            opportunity_id=opportunity_id,
            opportunity_profile="CATALYST",
        )
        self.assertTrue(href.startswith("/opportunities/detail?"))
        for token in ("%2F", "%3F", "%26", "%20", "%C3%A6", "%25"):
            self.assertIn(token, href)
        self.assertEqual(
            parse_opportunity_detail_href(href),
            OpportunityNavigationIdentity(
                opportunity_id=opportunity_id,
                opportunity_profile="CATALYST",
            ),
        )

    def test_builder_is_deterministic_and_ordered(self):
        kwargs = {
            "opportunity_id": "case:1",
            "opportunity_profile": "COMPOUNDER",
        }
        first = build_opportunity_detail_href(**kwargs)
        second = build_opportunity_detail_href(**kwargs)
        self.assertEqual(first, second)
        self.assertEqual(
            first,
            (
                "/opportunities/detail?"
                "opportunity_id=case%3A1"
                "&opportunity_profile=COMPOUNDER"
            ),
        )

    def test_query_order_does_not_change_identity(self):
        query = (
            "opportunity_profile=CATALYST"
            "&opportunity_id=case%3A2"
        )
        self.assertEqual(
            parse_opportunity_detail_query(query),
            OpportunityNavigationIdentity(
                opportunity_id="case:2",
                opportunity_profile="CATALYST",
            ),
        )

    def test_duplicate_identity_key_fails_closed(self):
        for query in (
            (
                "opportunity_id=a&opportunity_id=b"
                "&opportunity_profile=COMPOUNDER"
            ),
            (
                "opportunity_id=a&opportunity_profile=COMPOUNDER"
                "&opportunity_profile=CATALYST"
            ),
        ):
            with self.subTest(query=query):
                with self.assertRaises(OpportunityNavigationError) as caught:
                    parse_opportunity_detail_query(query)
                self.assertIn(
                    "duplicate_query_key",
                    {issue.code for issue in caught.exception.issues},
                )

    def test_unknown_query_key_fails_closed(self):
        with self.assertRaises(OpportunityNavigationError) as caught:
            parse_opportunity_detail_query(
                "opportunity_id=case-1"
                "&opportunity_profile=COMPOUNDER"
                "&ticker=NOVO-B"
            )
        self.assertIn(
            "unknown_query_key",
            {issue.code for issue in caught.exception.issues},
        )

    def test_missing_identity_key_fails_closed(self):
        for query in (
            "",
            "opportunity_id=case-1",
            "opportunity_profile=CATALYST",
        ):
            with self.subTest(query=query):
                with self.assertRaises(OpportunityNavigationError) as caught:
                    parse_opportunity_detail_query(query)
                self.assertIn(
                    "missing_query_key",
                    {issue.code for issue in caught.exception.issues},
                )

    def test_malformed_percent_encoding_fails_closed(self):
        for query in (
            "opportunity_id=%&opportunity_profile=COMPOUNDER",
            "opportunity_id=%2&opportunity_profile=COMPOUNDER",
            "opportunity_id=%ZZ&opportunity_profile=COMPOUNDER",
        ):
            with self.subTest(query=query):
                with self.assertRaises(OpportunityNavigationError) as caught:
                    parse_opportunity_detail_query(query)
                self.assertEqual(
                    caught.exception.issues[0].code,
                    "invalid_percent_encoding",
                )

    def test_invalid_utf8_percent_encoding_fails_closed(self):
        with self.assertRaises(OpportunityNavigationError) as caught:
            parse_opportunity_detail_query(
                "opportunity_id=%FF&opportunity_profile=COMPOUNDER"
            )
        self.assertEqual(
            caught.exception.issues[0].code,
            "invalid_query_string",
        )

    def test_non_ascii_raw_bytes_fail_closed(self):
        with self.assertRaises(OpportunityNavigationError) as caught:
            parse_opportunity_detail_query(
                b"opportunity_id="
                + bytes((0xFF,))
                + b"&opportunity_profile=COMPOUNDER"
            )
        self.assertEqual(
            caught.exception.issues[0].code,
            "non_ascii_query_bytes",
        )

    def test_wrong_path_external_url_and_fragment_rejected(self):
        hrefs = (
            (
                "/wrong?opportunity_id=x"
                "&opportunity_profile=COMPOUNDER"
            ),
            (
                "https://example.invalid/opportunities/detail?"
                "opportunity_id=x&opportunity_profile=COMPOUNDER"
            ),
            (
                "/opportunities/detail?opportunity_id=x"
                "&opportunity_profile=COMPOUNDER#current"
            ),
        )
        for href in hrefs:
            with self.subTest(href=href):
                with self.assertRaises(OpportunityNavigationError):
                    parse_opportunity_detail_href(href)

    def test_parser_does_not_accept_path_identity_alias(self):
        with self.assertRaises(OpportunityNavigationError):
            parse_opportunity_detail_href(
                "/opportunities/COMPOUNDER/case-1"
            )

    def test_no_hidden_business_or_network_dependency(self):
        path = Path("opportunity_navigation_contract.py")
        tree = ast.parse(
            path.read_text(encoding="utf-8"),
            filename=str(path),
        )
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module or "")
        self.assertEqual(
            set(imports),
            {"__future__", "dataclasses", "urllib.parse"},
        )
        blocked_import_fragments = (
            "openai",
            "requests",
            "yfinance",
            "provider",
            "sqlite",
            "flask",
        )
        for imported in imports:
            lowered = imported.lower()
            self.assertFalse(
                any(
                    fragment in lowered
                    for fragment in blocked_import_fragments
                ),
                imported,
            )

        blocked_calls = {
            "open",
            "exec",
            "eval",
            "redirect",
            "render_template",
        }
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Name):
                self.assertNotIn(node.func.id, blocked_calls)

    def test_builder_does_not_accept_business_alias_arguments(self):
        with self.assertRaises(TypeError):
            build_opportunity_detail_href(
                opportunity_id="case-1",
                opportunity_profile="COMPOUNDER",
                ticker="NOVO-B",
            )
        with self.assertRaises(TypeError):
            build_opportunity_detail_href(
                opportunity_id="case-1",
                opportunity_profile="COMPOUNDER",
                instrument_id="fixture:1",
            )

    def test_url_contains_only_two_identity_query_keys(self):
        href = build_opportunity_detail_href(
            opportunity_id="case-1",
            opportunity_profile="COMPOUNDER",
        )
        parts = urlsplit(href)
        self.assertEqual(parts.path, OPPORTUNITY_DETAIL_PATH)
        self.assertEqual(parts.fragment, "")
        self.assertEqual(
            parts.query.split("&"),
            [
                "opportunity_id=case-1",
                "opportunity_profile=COMPOUNDER",
            ],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
