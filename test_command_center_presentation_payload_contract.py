"""Synthetic payload fixtures only; no application or business services."""
from copy import deepcopy
import unittest

import command_center_presentation_payload_contract as contract


def text_item():
    return {"item_id": "fixture:item:1", "title": "Materialiseret tekst",
            "text": None, "source_references": ["fixture:source:1"]}


def card(profile="COMPOUNDER"):
    return {
        "opportunity_id": f"fixture:case:{profile.lower()}", "opportunity_profile": profile,
        "instrument_id": "fixture:instrument:1", "instrument_label": "Eksempel",
        "lifecycle": None, "opportunity_score": None, "ai_confidence": None,
        "data_confidence": None, "why_now": None, "critical_blockers": None,
        "source_references": ["fixture:source:1"],
    }


def fixtures():
    return {
        "page_context": {"title": "Command Center", "description": None},
        "attention": [text_item()],
        "executive_decision_summary": {
            "points": ["Allerede materialiseret tekst."], "source_references": [],
        },
        "compounder_opportunities": [card()],
        "catalyst_opportunities": [card("CATALYST")],
        "portfolio_relevance": [dict(text_item(), instrument_id=None,
                                     opportunity_id=None, portfolio_fit=None)],
        "what_changed": [dict(text_item(), record_reference=None)],
        "market_context": [text_item()],
        "trust_data_system_state": [text_item()],
    }


def verify(key, payload, **overrides):
    configuration = dict(
        availability="AVAILABLE",
        payload_version=contract.PRESENTATION_PAYLOAD_VERSION,
        presentation_policy_version=contract.SUPPORTED_PRESENTATION_POLICY_VERSION,
    )
    configuration.update(overrides)
    return contract.validate_presentation_payload(key, payload, **configuration)


class PresentationPayloadTests(unittest.TestCase):
    def test_all_nine_shapes(self):
        data = fixtures()
        self.assertEqual(set(data), contract.PRESENTATION_SECTION_KEYS)
        for key, payload in data.items():
            for status in ("AVAILABLE", "PARTIAL"):
                with self.subTest(section=key, availability=status):
                    self.assertEqual(verify(key, payload, availability=status), ())

    def test_no_input_mutation_or_reordering(self):
        payload = [dict(text_item(), item_id="second"), text_item()]
        before = deepcopy(payload)
        first = verify("attention", payload)
        self.assertEqual(first, verify("attention", payload))
        self.assertEqual(payload, before)

    def test_missing_is_not_empty(self):
        for value in (None, contract.MISSING_PAYLOAD):
            self.assertTrue(verify("portfolio_relevance", value))
            self.assertEqual(verify("portfolio_relevance", value,
                                    availability="UNAVAILABLE"), ())
        self.assertEqual(verify("portfolio_relevance", []), ())

    def test_unavailable_does_not_expose_content(self):
        for key, payload in fixtures().items():
            with self.subTest(section=key):
                self.assertEqual(verify(key, None, availability="UNAVAILABLE"), ())
                self.assertTrue(verify(key, payload, availability="UNAVAILABLE"))

    def test_missing_fields_are_not_filled(self):
        for key, payload in fixtures().items():
            obj = payload if type(payload) is dict else payload[0]
            for field in tuple(obj):
                candidate = deepcopy(payload)
                target = candidate if type(candidate) is dict else candidate[0]
                del target[field]
                with self.subTest(section=key, field=field):
                    codes = {x.code for x in verify(key, candidate)}
                    self.assertIn("missing_payload_field", codes)
                    self.assertNotIn(field, target)

    def test_zero_and_null_remain_distinct(self):
        for value in (0, 0.0, None, "Høj"):
            payload = [dict(card(), opportunity_score=value, ai_confidence=value,
                            data_confidence=value)]
            before = deepcopy(payload)
            self.assertEqual(verify("compounder_opportunities", payload), ())
            self.assertEqual(payload, before)
            self.assertIs(type(payload[0]["opportunity_score"]), type(value))

    def test_booleans_and_nonfinite_values_rejected(self):
        for value in (True, False, float("nan"), float("inf"), float("-inf")):
            for field in ("opportunity_score", "ai_confidence", "data_confidence"):
                payload = [dict(card(), **{field: value})]
                with self.subTest(field=field, value=value):
                    self.assertTrue(verify("compounder_opportunities", payload))

    def test_no_alias_guessing(self):
        payload = [card()]
        payload[0]["score"] = payload[0].pop("opportunity_score")
        codes = {x.code for x in verify("compounder_opportunities", payload)}
        self.assertIn("unexpected_payload_field", codes)
        self.assertIn("missing_payload_field", codes)

    def test_summary_v1_limit_no_truncation(self):
        for count in (0, 1, 3, 4):
            payload = {"points": ["Punkt"] * count, "source_references": []}
            before = deepcopy(payload)
            self.assertEqual(bool(verify("executive_decision_summary", payload)), count > 3)
            self.assertEqual(payload, before)

    def test_future_versions_not_silently_supported(self):
        for override in (
            {"payload_version": "future:v2"},
            {"presentation_policy_version": "command_center_presentation:v2"},
            {"availability": "UNKNOWN"},
        ):
            with self.subTest(override=override), self.assertRaises(ValueError):
                verify("attention", [], **override)
        with self.assertRaises(ValueError):
            verify("not_a_section", [])

    def test_bad_shapes_and_keys(self):
        for payload in ({}, "text", 0, False):
            self.assertTrue(verify("attention", payload))
        for payload in ([None], [{1: "bad"}], [{"item_id": []}]):
            self.assertTrue(verify("attention", payload))
        self.assertTrue(verify("attention", [dict(text_item(), title=None)]))

    def test_blockers_unknown_not_same_as_none_reported(self):
        for value in (None, [], ["Materialiseret blocker"]):
            payload = [dict(card(), critical_blockers=value)]
            before = deepcopy(payload)
            self.assertEqual(verify("compounder_opportunities", payload), ())
            self.assertEqual(payload, before)

    def test_portfolio_fit_separate(self):
        payload = fixtures()["portfolio_relevance"]
        for value in (None, 0, "Høj"):
            payload[0]["portfolio_fit"] = value
            self.assertEqual(verify("portfolio_relevance", payload), ())
        self.assertTrue(verify("compounder_opportunities", [dict(card(), portfolio_fit=0)]))

    def test_source_references_not_resolved_or_rewritten(self):
        payload = [dict(text_item(), source_references=["section:independent-source"])]
        before = deepcopy(payload)
        self.assertEqual(verify("attention", payload), ())
        self.assertEqual(payload, before)
        payload[0]["source_references"] = []
        self.assertEqual(verify("attention", payload), ())
        payload[0]["source_references"] = [""]
        self.assertTrue(verify("attention", payload))

    def test_duplicate_policy_not_reimplemented(self):
        payload = [card(), card()]
        self.assertEqual(verify("compounder_opportunities", payload), ())

    def test_text_is_not_marked_as_safe_html(self):
        payload = [dict(text_item(), title='<script>alert("fixture")</script>')]
        before = deepcopy(payload)
        self.assertEqual(verify("attention", payload), ())
        self.assertEqual(payload, before)
        # Rendering/escaping belongs to the later HTML implementation.

    def test_assertion_api(self):
        with self.assertRaises(contract.PresentationPayloadError) as caught:
            contract.assert_valid_presentation_payload(
                "attention", [{}], availability="AVAILABLE",
                payload_version=contract.PRESENTATION_PAYLOAD_VERSION,
                presentation_policy_version=contract.SUPPORTED_PRESENTATION_POLICY_VERSION,
            )
        self.assertTrue(caught.exception.issues)


if __name__ == "__main__":
    unittest.main(verbosity=2)
