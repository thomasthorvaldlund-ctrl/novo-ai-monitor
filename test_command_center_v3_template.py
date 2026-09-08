"""Slice 6c: synthetic presentation tests; never import the production app.

TemplateTests can run without business modules. AdapterIntegrationTests uses
real locked 6a/6b code on the server. Neither class registers a V3 route.
Browser layout/accessibility review remains separate from these DOM tests.
"""
from copy import deepcopy
from pathlib import Path
import re
import unittest

from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader, StrictUndefined, UndefinedError, meta, nodes, select_autoescape
from markupsafe import Markup

ROOT = Path(__file__).resolve().parent
TEMPLATE = "command_center_v3.html"
ORDER = (
    "page_context", "attention", "executive_decision_summary",
    "compounder_opportunities", "catalyst_opportunities", "portfolio_relevance",
    "what_changed", "market_context", "trust_data_system_state",
)
LIST_SECTIONS = tuple(k for k in ORDER if k not in (
    "page_context", "executive_decision_summary",
))
POLICY = "command_center_presentation:v1"
PAYLOAD_VERSION = "command_center_presentation_payload:v1"
VIEW_VERSION = "command_center_presentation_view_model:v1"
STAMP = "2026-09-07T16:59:00+00:00"


def fixture_view():
    """Explicit synthetic values, not fetched or inferred business data."""
    def item():
        return dict(item_id="fixture:item", title="Materialiseret punkt",
                    text="Eksempeltekst", source_references=["fixture:item-source"])

    def card(profile):
        return dict(opportunity_id="fixture:" + profile, opportunity_profile=profile,
                    instrument_id="fixture:instrument", instrument_label="Eksempel",
                    lifecycle=None, opportunity_score=None, ai_confidence=None,
                    data_confidence=None, why_now=None, critical_blockers=None,
                    source_references=["fixture:case-source"])

    payloads = {
        "page_context": dict(title="Command Center V3", description="Materialiseret overblik."),
        "attention": [item()],
        "executive_decision_summary": dict(points=["Materialiseret opsummering."], source_references=[]),
        "compounder_opportunities": [card("COMPOUNDER")],
        "catalyst_opportunities": [card("CATALYST")],
        "portfolio_relevance": [dict(item(), instrument_id=None, opportunity_id=None, portfolio_fit=None)],
        "what_changed": [dict(item(), record_reference=None)],
        "market_context": [item()], "trust_data_system_state": [item()],
    }
    return dict(
        view_model_version=VIEW_VERSION, payload_version=PAYLOAD_VERSION,
        presentation_policy_version=POLICY,
        projection=dict(command_center_projection_id="fixture:projection",
                        schema_version="command_center_projection:v1",
                        presentation_policy_version=POLICY,
                        materialized_at="2026-09-07T17:00:00+00:00",
                        as_of="2026-09-07T17:00:00+00:00", source_cutoff=STAMP,
                        source_references=["fixture:projection-source"],
                        scope={"kind": "GLOBAL"}, build_status="COMPLETE"),
        section_order=list(ORDER),
        sections={key: dict(availability="AVAILABLE", freshness="CURRENT",
                            source_as_of_present=True, source_as_of=STAMP,
                            source_references_present=True, source_references=["fixture:" + key],
                            payload_present=True, payload=payloads[key], has_content=True)
                  for key in ORDER},
        verification_warnings=[],
    )


def template_env():
    # Deliberately not the production Flask environment.
    env = Environment(loader=FileSystemLoader(str(ROOT / "templates")),
                      autoescape=select_autoescape(("html",)), undefined=StrictUndefined)

    def static_url(endpoint, *, filename):
        if (endpoint, filename) != ("static", "css/command_center_v3.css"):
            raise AssertionError("Template requested an unexpected route")
        return "/static/" + filename

    env.globals["url_for"] = static_url
    return env


def rendered(view):
    before = deepcopy(view)
    html = template_env().get_template(TEMPLATE).render(vm=view)
    if view != before:
        raise AssertionError("Template changed its input")
    return html, BeautifulSoup(html, "html.parser")


def section(soup, key):
    return soup.select_one('[data-section="' + key + '"]')


class TemplateTests(unittest.TestCase):
    def test_document_and_order(self):
        _, soup = rendered(fixture_view())
        self.assertEqual(soup.html["lang"], "da")
        self.assertEqual(len(soup.select("main")), 1)
        self.assertEqual(len(soup.select("h1")), 1)
        self.assertEqual([x["data-section"] for x in soup.select("[data-section]")], list(ORDER))
        for key in ORDER:
            self.assertIsNotNone(section(soup, key))

    def test_heading_ids_and_accessibility_references(self):
        vm = fixture_view()
        cases = vm["sections"]["compounder_opportunities"]["payload"]
        cases.append(deepcopy(cases[0]))
        _, soup = rendered(vm)
        ids = [tag["id"] for tag in soup.select("[id]")]
        self.assertEqual(len(ids), len(set(ids)))
        for tag in soup.select("[aria-labelledby], [aria-describedby]"):
            for attr in ("aria-labelledby", "aria-describedby"):
                for ref in tag.get(attr, "").split():
                    self.assertIn(ref, ids)
        self.assertEqual(soup.select_one(".cc-v3-skip")["href"], "#cc-v3-main")

    def test_profile_groups_and_order_are_not_ranked(self):
        vm = fixture_view()
        for key in ("compounder_opportunities", "catalyst_opportunities"):
            item = vm["sections"][key]["payload"][0]
            vm["sections"][key]["payload"] = [dict(item, opportunity_id="z-" + key), dict(item, opportunity_id="a-" + key)]
        _, soup = rendered(vm)
        for key in ("compounder_opportunities", "catalyst_opportunities"):
            cases = section(soup, key).select(".cc-v3-case")
            self.assertEqual([x["data-opportunity-id"] for x in cases], ["z-" + key, "a-" + key])
        self.assertEqual(len(soup.select(".cc-v3-case")), 4)

    def test_none_zero_labels_and_negative_zero(self):
        for v, expected in ((None, "Ikke oplyst"), (0, "0"), (0.0, "0.0"), (-0.0, "-0.0"), ("Høj", "Høj")):
            vm = fixture_view()
            card = vm["sections"]["compounder_opportunities"]["payload"][0]
            for name in ("opportunity_score", "ai_confidence", "data_confidence"):
                card[name] = v
            vm["sections"]["portfolio_relevance"]["payload"][0]["portfolio_fit"] = v
            _, soup = rendered(vm)
            for name in ("opportunity_score", "ai_confidence", "data_confidence", "portfolio_fit"):
                with self.subTest(field=name, value=v):
                    self.assertEqual(soup.select_one('[data-field="' + name + '"]').get_text(strip=True), expected)

    def test_lifecycle_and_confidences_remain_separate(self):
        vm = fixture_view()
        vm["sections"]["compounder_opportunities"]["payload"][0].update(
            lifecycle="DATA_HOLD", opportunity_score=71, ai_confidence="Moderat", data_confidence="Lav")
        _, soup = rendered(vm)
        card = section(soup, "compounder_opportunities").select_one(".cc-v3-case")
        for name, expected in (("lifecycle", "DATA_HOLD"), ("opportunity_score", "71"), ("ai_confidence", "Moderat"), ("data_confidence", "Lav")):
            self.assertEqual(card.select_one('[data-field="' + name + '"]').get_text(strip=True), expected)
        self.assertFalse(card.select('[data-field="portfolio_fit"]'))

    def test_blocker_states_are_distinct_and_visible(self):
        for value, state in ((None, "unknown"), ([], "empty"), (["DATA_HOLD: kilde mangler"], "present")):
            vm = fixture_view()
            vm["sections"]["compounder_opportunities"]["payload"][0]["critical_blockers"] = value
            _, soup = rendered(vm)
            tag = section(soup, "compounder_opportunities").select_one("[data-blockers]")
            self.assertEqual(tag["data-blockers"], state)
            self.assertIsNone(tag.find_parent("details"))
            if value:
                self.assertIn(value[0], tag.get_text())

    def test_all_section_status_combinations(self):
        labels = {"AVAILABLE": "Tilgængelig", "PARTIAL": "Delvist tilgængelig", "UNAVAILABLE": "Utilgængelig"}
        fresh = {"CURRENT": "Aktuel", "STALE": "Forældet", "UNKNOWN": "Aktualitet ukendt"}
        for key in ORDER:
            for av in labels:
                for fr in fresh:
                    vm = fixture_view()
                    s = vm["sections"][key]
                    s.update(availability=av, freshness=fr)
                    if av == "UNAVAILABLE":
                        s.update(payload=None, has_content=False)
                    _, soup = rendered(vm)
                    node = section(soup, key)
                    with self.subTest(section=key, availability=av, freshness=fr):
                        self.assertEqual(node["data-availability"], av)
                        self.assertEqual(node["data-freshness"], fr)
                        self.assertEqual(node.select_one('[data-axis="availability"]').get_text(strip=True), labels[av])
                        self.assertEqual(node.select_one('[data-axis="freshness"]').get_text(strip=True), fresh[fr])
                        self.assertEqual(bool(node.select('[data-notice="stale"]')), fr == "STALE")
                        self.assertEqual(bool(node.select('[data-notice="partial"]')), av == "PARTIAL")
                        self.assertEqual(bool(node.select('[data-state="unavailable"]')), av == "UNAVAILABLE")

    def test_unavailable_never_exposes_payload(self):
        vm = fixture_view()
        for s in vm["sections"].values():
            s.update(availability="UNAVAILABLE", freshness="UNKNOWN", has_content=True,
                     payload={"title": "MUST_NOT_RENDER", "text": "MUST_NOT_RENDER"})
        html, soup = rendered(vm)
        self.assertNotIn("MUST_NOT_RENDER", html)
        self.assertEqual(len(soup.select('[data-state="unavailable"]')), 9)

    def test_portfolio_unavailable_keeps_objective_cases(self):
        vm = fixture_view()
        vm["sections"]["portfolio_relevance"].update(availability="UNAVAILABLE", payload=None, has_content=False)
        _, soup = rendered(vm)
        self.assertEqual(len(soup.select(".cc-v3-case")), 2)
        node = section(soup, "portfolio_relevance")
        self.assertIn("Det siger ikke, om du har beholdninger", node.get_text())
        self.assertFalse(node.select('[data-field="portfolio_fit"]'))

    def test_empty_lists_and_summary_do_not_generate_items(self):
        vm = fixture_view()
        for key in LIST_SECTIONS:
            vm["sections"][key].update(payload=[], has_content=False)
        vm["sections"]["executive_decision_summary"]["payload"]["points"] = []
        vm["sections"]["executive_decision_summary"]["has_content"] = False
        _, soup = rendered(vm)
        self.assertEqual(len(soup.select('[data-state="empty"]')), 8)
        self.assertFalse(soup.select(".cc-v3-case, [data-item-id], .cc-v3-summary li"))
        self.assertIn("ikke en opgørelse", section(soup, "portfolio_relevance").get_text())

    def test_summary_points_exact_order_and_no_truncation(self):
        vm = fixture_view()
        points = ["Z: første punkt", "A: andet punkt", "M: tredje punkt"]
        vm["sections"]["executive_decision_summary"]["payload"]["points"] = points
        _, soup = rendered(vm)
        self.assertEqual([n.get_text(strip=True) for n in soup.select(".cc-v3-summary li")], points)

    def test_timestamps_are_not_recomputed_or_shared(self):
        vm = fixture_view()
        for i, key in enumerate(ORDER):
            vm["sections"][key]["source_as_of"] = f"2026-09-07T0{i}:00:00+02:00"
        _, soup = rendered(vm)
        for key in ORDER:
            tag = section(soup, key).select_one("time")
            self.assertEqual(tag["datetime"], vm["sections"][key]["source_as_of"])
            self.assertEqual(tag.get_text(), tag["datetime"])
        self.assertIn(vm["projection"]["as_of"], soup.get_text())

    def test_missing_source_metadata_differs_from_explicit_empty(self):
        vm = fixture_view()
        s = vm["sections"]["market_context"]
        s.update(freshness="UNKNOWN", source_as_of_present=False, source_as_of=None,
                 source_references_present=False, source_references=None)
        _, soup = rendered(vm)
        text = section(soup, "market_context").get_text()
        self.assertIn("Kildetidspunkt mangler", text)
        self.assertIn("Kildereferencer mangler", text)
        s.update(source_as_of_present=True, source_references_present=True, source_references=[])
        _, soup = rendered(vm)
        text = section(soup, "market_context").get_text()
        self.assertIn("Kildetidspunkt ikke oplyst", text)
        self.assertIn("Ingen kildereferencer angivet", text)

    def test_warnings_remain_visible_when_trust_is_unavailable(self):
        vm = fixture_view()
        vm["sections"]["trust_data_system_state"].update(availability="UNAVAILABLE", payload=None, has_content=False)
        vm["verification_warnings"] = [dict(code="duplicate_executive_opportunity_id", path="sections.fixture", message="Syntetisk advarsel", severity="WARNING")]
        _, soup = rendered(vm)
        warning = soup.select_one("[data-verification-warnings]")
        self.assertIn("Syntetisk advarsel", warning.get_text())
        self.assertIsNone(warning.find_parent("details"))
        self.assertIn("WARNING", warning.get_text())

    def test_text_and_attribute_injection_is_escaped(self):
        evil = '\"><img src=x onerror=alert(1)><script>alert(2)</script>&'
        vm = fixture_view()
        vm["sections"]["page_context"]["payload"].update(title=evil, description=evil)
        vm["sections"]["attention"]["payload"][0].update(item_id=evil, title=evil, text=evil, source_references=[evil])
        vm["sections"]["compounder_opportunities"]["payload"][0].update(opportunity_id=evil, instrument_label=evil, why_now=evil, critical_blockers=[evil])
        vm["projection"]["command_center_projection_id"] = evil
        vm["verification_warnings"] = [dict(code=evil, path=evil, message=evil, severity="WARNING")]
        html, soup = rendered(vm)
        self.assertFalse(soup.select("img, script, iframe, object, svg"))
        self.assertIn(evil, soup.h1.get_text())
        self.assertEqual(soup.select_one(".cc-v3-case")["data-opportunity-id"], evil)
        self.assertIn("&lt;script&gt;", html)
        for node in soup.find_all(True):
            self.assertFalse(any(name.lower().startswith("on") for name in node.attrs))

    def test_markup_objects_are_not_trusted_as_html(self):
        vm = fixture_view()
        vm["sections"]["attention"]["payload"][0]["title"] = Markup("<b>Not trusted markup</b>")
        _, soup = rendered(vm)
        self.assertFalse(section(soup, "attention").select("b"))
        self.assertIn("<b>Not trusted markup</b>", section(soup, "attention").get_text())

    def test_unknown_metadata_and_scope_ids_are_not_dumped(self):
        vm = fixture_view()
        vm["projection"]["future_internal_extension"] = "SECRET_SENTINEL"
        vm["projection"]["scope"] = dict(kind="PERSONAL", scope_id="SECRET_SENTINEL", internal="SECRET_SENTINEL")
        vm["sections"]["attention"]["future_extension"] = "SECRET_SENTINEL"
        html, _ = rendered(vm)
        self.assertNotIn("SECRET_SENTINEL", html)

    def test_missing_or_future_view_model_is_unavailable(self):
        for field in ("view_model_version", "payload_version", "presentation_policy_version"):
            vm = fixture_view()
            vm[field] = "future:v999"
            _, soup = rendered(vm)
            self.assertIsNotNone(soup.select_one('[data-page-state="unavailable"]'))
            self.assertFalse(soup.select("[data-section], .cc-v3-case"))
        _, soup = rendered(None)
        self.assertIsNotNone(soup.select_one('[data-page-state="unavailable"]'))

    def test_strict_render_fails_on_missing_required_field(self):
        vm = fixture_view()
        del vm["sections"]["compounder_opportunities"]["payload"][0]["opportunity_score"]
        with self.assertRaises(UndefinedError):
            rendered(vm)

    def test_deterministic_render_and_input_preserved(self):
        vm = fixture_view()
        before = deepcopy(vm)
        self.assertEqual(rendered(vm)[0], rendered(vm)[0])
        self.assertEqual(vm, before)

    def test_no_dynamic_or_business_navigation(self):
        _, soup = rendered(fixture_view())
        self.assertFalse(soup.select("script, form, input, button, iframe"))
        self.assertEqual([a["href"] for a in soup.select("a")], ["#cc-v3-main"])
        self.assertEqual([x["href"] for x in soup.select('link[rel="stylesheet"]')], ["/static/css/command_center_v3.css"])
        self.assertFalse(soup.select('meta[http-equiv="refresh"]'))
        self.assertTrue(soup.select("details > summary"))

    def test_jinja_has_no_business_selection_or_unsafe_filters(self):
        tree = template_env().parse((ROOT / "templates" / TEMPLATE).read_text())
        self.assertEqual(meta.find_undeclared_variables(tree), {"vm"})
        for cls in (nodes.Extends, nodes.Include, nodes.Import, nodes.FromImport):
            self.assertFalse(list(tree.find_all(cls)))
        self.assertEqual({n.name for n in tree.find_all(nodes.Filter)}, {"forceescape"})
        for call in tree.find_all(nodes.Call):
            self.assertIsInstance(call.node, nodes.Name)
            self.assertIn(call.node.name, {"value", "field", "refs", "url_for"})
            if call.node.name == "url_for":
                self.assertEqual(call.args[0].value, "static")
        self.assertFalse(list(tree.find_all(nodes.Slice)))

    def test_css_has_mobile_single_column_without_reordering(self):
        css = (ROOT / "static/css/command_center_v3.css").read_text()
        self.assertIn("@media (max-width: 760px)", css)
        self.assertIn("grid-template-columns: minmax(0, 1fr)", css)
        self.assertIn(":focus-visible", css)
        self.assertIn("overflow-wrap: anywhere", css)
        self.assertNotRegex(css, r"(?m)(?:^|[;{])\s*order\s*:")
        self.assertNotRegex(css, r"grid-auto-flow\s*:[^;]*dense")
        self.assertNotIn("@import", css)
        self.assertNotIn("url(", css)


class AdapterIntegrationTests(unittest.TestCase):
    def test_real_adapter_output_renders_without_production_app(self):
        from test_command_center_presentation_adapter import adapt, make_projection
        projection = make_projection()
        before = deepcopy(projection)
        vm = adapt(projection)
        from flask import Flask, render_template
        app = Flask("slice6c-real-flask-test", template_folder=str(ROOT / "templates"),
                    static_folder=str(ROOT / "static"))
        app.testing = True
        app.jinja_env.undefined = StrictUndefined
        with app.test_request_context("/slice6c-template-test"):
            html = render_template(TEMPLATE, vm=vm)
        soup = BeautifulSoup(html, "html.parser")
        self.assertEqual({r.endpoint for r in app.url_map.iter_rules()}, {"static"})
        self.assertEqual([x["data-section"] for x in soup.select("[data-section]")], list(ORDER))
        self.assertEqual(projection, before)

    def test_adapter_errors_block_before_rendering(self):
        from command_center_presentation_adapter import PresentationAdapterError
        from test_command_center_presentation_adapter import adapt, make_projection
        for failure in ("profile", "limit", "summary", "payload"):
            p = make_projection()
            cases = p["sections"]["compounder_opportunities"]["payload"]
            if failure == "profile":
                cases[0]["opportunity_profile"] = "CATALYST"
            elif failure == "limit":
                p["sections"]["compounder_opportunities"]["payload"] = [dict(cases[0], opportunity_id=str(i)) for i in range(3)]
            elif failure == "summary":
                p["sections"]["executive_decision_summary"]["payload"]["points"] = ["punkt"] * 4
            else:
                del cases[0]["data_confidence"]
            with self.subTest(failure=failure), self.assertRaises(PresentationAdapterError):
                adapt(p)

    def test_real_partial_stale_and_portfolio_unavailable(self):
        from test_command_center_presentation_adapter import adapt, make_projection
        p = make_projection()
        p["sections"]["attention"].update(availability="PARTIAL", freshness="STALE")
        p["sections"]["portfolio_relevance"].update(availability="UNAVAILABLE", freshness="UNKNOWN", source_as_of=None, source_references=[], payload=None)
        _, soup = rendered(adapt(p))
        self.assertIsNotNone(section(soup, "attention").select_one('[data-notice="stale"]'))
        self.assertEqual(len(soup.select(".cc-v3-case")), 2)
        self.assertIsNotNone(section(soup, "portfolio_relevance").select_one('[data-state="unavailable"]'))

    def test_real_duplicate_warning_is_not_hidden(self):
        from test_command_center_presentation_adapter import adapt, make_projection
        p = make_projection()
        cases = p["sections"]["compounder_opportunities"]["payload"]
        cases.append(deepcopy(cases[0]))
        _, soup = rendered(adapt(p))
        self.assertEqual(len(section(soup, "compounder_opportunities").select(".cc-v3-case")), 2)
        self.assertIn("duplicate_executive_opportunity_id", soup.select_one("[data-verification-warnings]").get_text())


if __name__ == "__main__":
    unittest.main(verbosity=2)
