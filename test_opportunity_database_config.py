from __future__ import annotations

from contextlib import ExitStack
from copy import deepcopy
import os
from pathlib import Path
import unittest
from unittest.mock import patch

import opportunity_database_config as config


class OpportunityDatabaseConfigTests(unittest.TestCase):
    def test_locked_database_name_and_override_key(self):
        self.assertEqual(config.V3_DATABASE_FILENAME, "aureum_v3.sqlite3")
        self.assertEqual(config.V3_DATABASE_PATH_ENV, "AUREUM_V3_DB_PATH")

    def test_default_comes_from_state_path(self):
        expected = Path("/example/private-state/aureum_v3.sqlite3")
        with patch.object(config, "state_path", return_value=expected) as default:
            self.assertEqual(
                config.resolve_opportunity_database_path(environ={}), expected
            )
        default.assert_called_once_with("aureum_v3.sqlite3")

    def test_explicit_override_does_not_read_default(self):
        with patch.object(config, "state_path") as default:
            actual = config.resolve_opportunity_database_path(
                environ={"AUREUM_V3_DB_PATH": "/example/override/store.sqlite3"}
            )
        self.assertEqual(actual, Path("/example/override/store.sqlite3"))
        default.assert_not_called()

    def test_explicit_blank_override_fails_without_fallback(self):
        with patch.object(config, "state_path") as default:
            for value in ("", " ", "\t\n"):
                with self.subTest(value=repr(value)):
                    with self.assertRaises(config.OpportunityDatabaseConfigurationError):
                        config.resolve_opportunity_database_path(
                            environ={"AUREUM_V3_DB_PATH": value}
                        )
        default.assert_not_called()

    def test_relative_tilde_and_uri_overrides_fail(self):
        with patch.object(config, "state_path") as default:
            for value in (
                "aureum_v3.sqlite3", "./store.sqlite3", "../store.sqlite3",
                "~/store.sqlite3", "file:/example/store.sqlite3?mode=ro",
            ):
                with self.subTest(value=value):
                    with self.assertRaises(config.OpportunityDatabaseConfigurationError):
                        config.resolve_opportunity_database_path(
                            environ={"AUREUM_V3_DB_PATH": value}
                        )
        default.assert_not_called()

    def test_invalid_override_value_types_fail(self):
        with patch.object(config, "state_path") as default:
            for value in (None, False, 123, b"/example/store", [], {}, Path("/example/store")):
                with self.subTest(value=repr(value)):
                    with self.assertRaises(config.OpportunityDatabaseConfigurationError):
                        config.resolve_opportunity_database_path(
                            environ={"AUREUM_V3_DB_PATH": value}
                        )
        default.assert_not_called()

    def test_injected_environment_must_be_mapping(self):
        for value in (False, 123, "", [], set()):
            with self.subTest(value=repr(value)):
                with self.assertRaises(config.OpportunityDatabaseConfigurationError):
                    config.resolve_opportunity_database_path(environ=value)

    def test_invalid_state_path_default_fails(self):
        for value in (None, "", Path("relative.sqlite3"), Path("/")):
            with self.subTest(value=repr(value)):
                with patch.object(config, "state_path", return_value=value):
                    with self.assertRaises(config.OpportunityDatabaseConfigurationError):
                        config.resolve_opportunity_database_path(environ={})

    def test_nul_and_root_overrides_fail(self):
        for value in ("/", "/example/bad\x00name.sqlite3"):
            with self.subTest(value=repr(value)):
                with self.assertRaises(config.OpportunityDatabaseConfigurationError):
                    config.resolve_opportunity_database_path(
                        environ={"AUREUM_V3_DB_PATH": value}
                    )

    def test_spaces_unicode_and_percent_are_not_reinterpreted(self):
        value = "/example/æøå data/v3%20#?.sqlite3"
        self.assertEqual(
            str(config.resolve_opportunity_database_path(
                environ={"AUREUM_V3_DB_PATH": value}
            )),
            value,
        )

    def test_environment_is_read_at_call_time(self):
        with patch.dict(os.environ, {"AUREUM_V3_DB_PATH": "/example/first.sqlite3"}):
            first = config.resolve_opportunity_database_path()
            os.environ["AUREUM_V3_DB_PATH"] = "/example/second.sqlite3"
            second = config.resolve_opportunity_database_path()
        self.assertEqual(first, Path("/example/first.sqlite3"))
        self.assertEqual(second, Path("/example/second.sqlite3"))

    def test_input_is_unchanged_and_resolution_is_deterministic(self):
        environment = {"AUREUM_V3_DB_PATH": "/example/v3.sqlite3", "OTHER": "kept"}
        before = deepcopy(environment)
        first = config.resolve_opportunity_database_path(environ=environment)
        second = config.resolve_opportunity_database_path(environ=environment)
        self.assertEqual(first, second)
        self.assertEqual(environment, before)

    def test_resolution_performs_no_filesystem_or_database_calls(self):
        blocked_calls = (
            "builtins.open", "os.open", "os.mkdir", "os.chmod",
            "os.stat", "os.lstat", "os.readlink", "os.replace",
            "pathlib.Path.open", "pathlib.Path.mkdir", "pathlib.Path.resolve",
            "pathlib.Path.stat", "pathlib.Path.exists", "sqlite3.connect",
        )
        with ExitStack() as stack:
            for name in blocked_calls:
                stack.enter_context(patch(name, side_effect=AssertionError(name)))
            stack.enter_context(patch.object(
                config, "state_path", return_value=Path("/example/state/aureum_v3.sqlite3")
            ))
            default = config.resolve_opportunity_database_path(environ={})
            explicit = config.resolve_opportunity_database_path(
                environ={"AUREUM_V3_DB_PATH": "/example/override.sqlite3"}
            )
        self.assertEqual(default, Path("/example/state/aureum_v3.sqlite3"))
        self.assertEqual(explicit, Path("/example/override.sqlite3"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
