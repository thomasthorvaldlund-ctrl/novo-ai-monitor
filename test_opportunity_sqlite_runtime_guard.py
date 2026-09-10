from __future__ import annotations

import ast
from contextlib import ExitStack
import inspect
from pathlib import Path
import unittest
from unittest.mock import patch

import opportunity_sqlite_runtime_guard as guard


class OpportunitySQLiteRuntimeGuardTests(unittest.TestCase):
    def accept(self, version):
        with patch.object(guard.sqlite3, "sqlite_version_info", version):
            self.assertIs(guard.require_sqlite_wal_reset_fix(), version)

    def reject(self, version):
        with patch.object(guard.sqlite3, "sqlite_version_info", version):
            with self.assertRaises(guard.OpportunitySQLiteRuntimeError):
                guard.require_sqlite_wal_reset_fix()

    def test_release_policy_identifier(self):
        self.assertEqual(
            guard.SQLITE_WAL_RESET_RELEASE_POLICY,
            "sqlite_wal_reset_release:v1",
        )

    def test_current_aureum_runtime_is_rejected(self):
        self.reject((3, 45, 1))

    def test_documented_mainline_fix_floor(self):
        for version in ((3, 51, 3), (3, 51, 4), (3, 53, 0), (3, 53, 1)):
            with self.subTest(version=version):
                self.accept(version)

    def test_documented_backport_branches(self):
        for version in ((3, 44, 6), (3, 44, 7), (3, 50, 7), (3, 50, 8)):
            with self.subTest(version=version):
                self.accept(version)

    def test_versions_below_each_fix_floor_are_rejected(self):
        for version in ((3, 44, 5), (3, 50, 6), (3, 51, 2), (3, 40, 1)):
            with self.subTest(version=version):
                self.reject(version)

    def test_backport_floor_is_not_applied_to_other_branches(self):
        for version in ((3, 45, 99), (3, 46, 99), (3, 49, 99)):
            with self.subTest(version=version):
                self.reject(version)

    def test_withdrawn_branch_is_not_accepted(self):
        self.reject((3, 52, 0))
        self.reject((3, 52, 1))

    def test_other_major_versions_are_not_guessed_compatible(self):
        self.reject((2, 99, 99))
        self.reject((4, 0, 0))

    def test_malformed_metadata_fails_with_controlled_error(self):
        for version in (
            None, False, 3051003, "3.51.3", [3, 51, 3], {}, (),
            (3, 51), (3, 51, 3, 0), (3, 51, True),
            (3, 51, "3"), (3, 51, 3.0), (3, -1, 3), (3, 51, []),
        ):
            with self.subTest(version=repr(version)):
                self.reject(version)

    def test_runtime_metadata_is_read_at_each_call(self):
        with patch.object(guard.sqlite3, "sqlite_version_info", (3, 53, 1)):
            self.assertEqual(guard.require_sqlite_wal_reset_fix(), (3, 53, 1))
            guard.sqlite3.sqlite_version_info = (3, 45, 1)
            with self.assertRaises(guard.OpportunitySQLiteRuntimeError):
                guard.require_sqlite_wal_reset_fix()

    def test_public_gate_has_no_caller_version_or_bypass_argument(self):
        self.assertEqual(
            list(inspect.signature(guard.require_sqlite_wal_reset_fix).parameters),
            [],
        )
        with self.assertRaises(TypeError):
            guard.require_sqlite_wal_reset_fix(version=(3, 53, 1))
        with self.assertRaises(TypeError):
            guard.require_sqlite_wal_reset_fix(allow_unpatched=True)

    def test_gate_has_no_database_filesystem_or_process_calls(self):
        blocked = (
            "sqlite3.connect", "builtins.open", "os.open", "os.mkdir",
            "os.chmod", "os.replace", "subprocess.run",
            "subprocess.check_output", "pathlib.Path.open",
        )
        with ExitStack() as stack:
            mocks = [
                stack.enter_context(patch(name, side_effect=AssertionError(name)))
                for name in blocked
            ]
            self.accept((3, 53, 1))
            self.reject((3, 45, 1))
            for mock in mocks:
                mock.assert_not_called()

    def test_source_has_only_expected_imports_and_calls(self):
        source = Path(guard.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.add(node.module)
        self.assertEqual(imports, {"__future__", "sqlite3"})
        calls = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                self.assertIsInstance(node.func, ast.Name)
                calls.append(node.func.id)
        self.assertEqual(set(calls), {
            "type", "len", "any", "_documented_fixed_release",
            "OpportunitySQLiteRuntimeError",
        })


if __name__ == "__main__":
    unittest.main(verbosity=2)
