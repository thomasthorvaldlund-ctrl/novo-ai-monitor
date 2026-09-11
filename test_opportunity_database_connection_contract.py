from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
import inspect
from pathlib import Path
import unittest

import opportunity_database_connection_contract as contract


class OpportunityDatabaseConnectionContractTests(unittest.TestCase):
    def policy(self, **changes):
        values = {
            "required_write_schema_version": 5,
            "minimum_read_schema_version": 4,
            "maximum_read_schema_version": 6,
        }
        values.update(changes)
        return contract.SchemaCompatibilityPolicy(**values)

    def write_only_policy(self, **changes):
        values = {
            "required_write_schema_version": 5,
            "minimum_read_schema_version": None,
            "maximum_read_schema_version": None,
        }
        values.update(changes)
        return contract.SchemaCompatibilityPolicy(**values)

    def observation(self, **changes):
        values = {
            "foreign_keys": 1,
            "journal_mode": "wal",
            "busy_timeout_ms": 15000,
            "synchronous": 2,
            "read_uncommitted": 0,
            "row_mapping_is_unambiguous": True,
            "user_version": 5,
        }
        values.update(changes)
        return contract.ConnectionStateObservation(**values)

    _UNSET = object()

    def assert_rejected(
        self,
        observation=_UNSET,
        *,
        access_mode=_UNSET,
        policy=_UNSET,
    ):
        if observation is self._UNSET:
            observation = self.observation()
        if access_mode is self._UNSET:
            access_mode = contract.READ_ONLY_ACCESS
        if policy is self._UNSET:
            policy = self.policy()
        with self.assertRaises(contract.OpportunityDatabaseConnectionContractError):
            contract.assert_connection_settings_compatible(
                observation,
                access_mode=access_mode,
                schema_policy=policy,
            )

    def test_locked_contract_constants(self):
        self.assertEqual(
            contract.CONNECTION_STATE_CONTRACT_VERSION,
            "opportunity_connection_state:v1",
        )
        self.assertEqual(contract.READ_ONLY_ACCESS, "READ_ONLY")
        self.assertEqual(contract.CANONICAL_WRITE_ACCESS, "CANONICAL_WRITE")
        self.assertEqual(contract.EXPECTED_FOREIGN_KEYS, 1)
        self.assertEqual(contract.EXPECTED_JOURNAL_MODE, "wal")
        self.assertEqual(contract.EXPECTED_BUSY_TIMEOUT_MS, 15000)
        self.assertEqual(contract.EXPECTED_WRITE_SYNCHRONOUS, 2)
        self.assertEqual(
            contract.KNOWN_SYNCHRONOUS_VALUES,
            frozenset({0, 1, 2, 3}),
        )
        self.assertEqual(contract.EXPECTED_READ_UNCOMMITTED, 0)

    def test_read_only_accepts_each_explicit_read_range_boundary(self):
        policy = self.policy()
        for version in (4, 5, 6):
            for synchronous in (0, 1, 2, 3):
                with self.subTest(version=version, synchronous=synchronous):
                    observation = self.observation(
                        user_version=version,
                        synchronous=synchronous,
                    )
                    self.assertIs(
                        contract.assert_connection_settings_compatible(
                            observation,
                            access_mode=contract.READ_ONLY_ACCESS,
                            schema_policy=policy,
                        ),
                        observation,
                    )

    def test_write_only_policy_does_not_invent_read_compatibility(self):
        policy = self.write_only_policy()
        observation = self.observation(user_version=5)
        self.assertIs(
            contract.assert_connection_settings_compatible(
                observation,
                access_mode=contract.CANONICAL_WRITE_ACCESS,
                schema_policy=policy,
            ),
            observation,
        )
        self.assert_rejected(
            observation,
            access_mode=contract.READ_ONLY_ACCESS,
            policy=policy,
        )

    def test_canonical_write_requires_exact_write_version(self):
        policy = self.policy()
        observation = self.observation(user_version=5)
        self.assertIs(
            contract.assert_connection_settings_compatible(
                observation,
                access_mode=contract.CANONICAL_WRITE_ACCESS,
                schema_policy=policy,
            ),
            observation,
        )
        for version in (4, 6):
            with self.subTest(version=version):
                self.assert_rejected(
                    self.observation(user_version=version),
                    access_mode=contract.CANONICAL_WRITE_ACCESS,
                    policy=policy,
                )

    def test_read_only_never_guesses_outside_explicit_range(self):
        policy = self.policy()
        for version in (0, 1, 3, 7, 999):
            with self.subTest(version=version):
                self.assert_rejected(
                    self.observation(user_version=version),
                    access_mode=contract.READ_ONLY_ACCESS,
                    policy=policy,
                )

    def test_common_normal_connection_settings_fail_closed(self):
        bad = (
            {"foreign_keys": 0},
            {"journal_mode": "delete"},
            {"journal_mode": "WAL"},
            {"busy_timeout_ms": 14999},
            {"busy_timeout_ms": 15001},
            {"read_uncommitted": 1},
            {"row_mapping_is_unambiguous": False},
        )
        for changes in bad:
            with self.subTest(changes=changes):
                self.assert_rejected(self.observation(**changes))

    def test_canonical_write_requires_synchronous_full(self):
        for synchronous in (0, 1, 3):
            with self.subTest(synchronous=synchronous):
                self.assert_rejected(
                    self.observation(synchronous=synchronous),
                    access_mode=contract.CANONICAL_WRITE_ACCESS,
                )

    def test_required_write_schema_version_must_be_positive_exact_int(self):
        for value in (None, False, True, 0, -1, 5.0, "5"):
            with self.subTest(value=repr(value)):
                with self.assertRaises(
                    contract.OpportunityDatabaseConnectionContractError
                ):
                    self.policy(required_write_schema_version=value)

    def test_read_range_is_optional_but_must_be_complete_and_valid(self):
        contract.SchemaCompatibilityPolicy(required_write_schema_version=5)

        invalid = (
            (None, 6),
            (4, None),
            (0, 6),
            (4, 0),
            (-1, 6),
            (4, -1),
            (4.0, 6),
            (4, "6"),
            (True, 6),
            (4, False),
        )
        for minimum, maximum in invalid:
            with self.subTest(minimum=repr(minimum), maximum=repr(maximum)):
                with self.assertRaises(
                    contract.OpportunityDatabaseConnectionContractError
                ):
                    contract.SchemaCompatibilityPolicy(
                        required_write_schema_version=5,
                        minimum_read_schema_version=minimum,
                        maximum_read_schema_version=maximum,
                    )

    def test_declared_read_range_must_include_write_version_and_be_ordered(self):
        invalid = (
            (7, 6),
            (6, 7),
            (3, 4),
        )
        for minimum_read, maximum_read in invalid:
            with self.subTest(
                minimum_read=minimum_read,
                maximum_read=maximum_read,
            ):
                with self.assertRaises(
                    contract.OpportunityDatabaseConnectionContractError
                ):
                    contract.SchemaCompatibilityPolicy(
                        required_write_schema_version=5,
                        minimum_read_schema_version=minimum_read,
                        maximum_read_schema_version=maximum_read,
                    )

    def test_observation_metadata_types_fail_closed(self):
        invalid = (
            ("foreign_keys", None),
            ("foreign_keys", True),
            ("journal_mode", None),
            ("journal_mode", b"wal"),
            ("journal_mode", ""),
            ("busy_timeout_ms", False),
            ("busy_timeout_ms", 15000.0),
            ("synchronous", True),
            ("synchronous", 4),
            ("read_uncommitted", False),
            ("row_mapping_is_unambiguous", 1),
            ("user_version", False),
            ("user_version", -1),
            ("user_version", "5"),
        )
        for field, value in invalid:
            with self.subTest(field=field, value=repr(value)):
                with self.assertRaises(
                    contract.OpportunityDatabaseConnectionContractError
                ):
                    self.observation(**{field: value})

    def test_access_mode_is_exact_and_not_normalized(self):
        for value in (None, False, "read_only", "READ", "CANONICAL_WRITE ", 1):
            with self.subTest(value=repr(value)):
                self.assert_rejected(access_mode=value)

    def test_wrong_contract_object_types_are_rejected(self):
        self.assert_rejected(observation=object())
        self.assert_rejected(policy=object())

    def test_contract_subclasses_cannot_spoof_gate_values(self):
        class SpoofedObservation(contract.ConnectionStateObservation):
            def __getattribute__(self, name):
                if name == "foreign_keys":
                    return 1
                return super().__getattribute__(name)

        spoofed_observation = SpoofedObservation(
            foreign_keys=0,
            journal_mode="wal",
            busy_timeout_ms=15000,
            synchronous=2,
            read_uncommitted=0,
            row_mapping_is_unambiguous=True,
            user_version=5,
        )

        stored_foreign_keys = contract.ConnectionStateObservation.__dict__[
            "foreign_keys"
        ].__get__(
            spoofed_observation,
            contract.ConnectionStateObservation,
        )
        self.assertEqual(stored_foreign_keys, 0)

        self.assert_rejected(
            spoofed_observation,
            access_mode=contract.CANONICAL_WRITE_ACCESS,
        )

        class SpoofedPolicy(contract.SchemaCompatibilityPolicy):
            def __getattribute__(self, name):
                if name == "required_write_schema_version":
                    return 5
                return super().__getattribute__(name)

        spoofed_policy = SpoofedPolicy(
            required_write_schema_version=7,
        )

        stored_required_write = contract.SchemaCompatibilityPolicy.__dict__[
            "required_write_schema_version"
        ].__get__(
            spoofed_policy,
            contract.SchemaCompatibilityPolicy,
        )
        self.assertEqual(stored_required_write, 7)

        self.assert_rejected(
            access_mode=contract.CANONICAL_WRITE_ACCESS,
            policy=spoofed_policy,
        )

    def test_contract_records_are_immutable(self):
        observation = self.observation()
        policy = self.policy()
        with self.assertRaises(FrozenInstanceError):
            observation.user_version = 6
        with self.assertRaises(FrozenInstanceError):
            policy.required_write_schema_version = 6

    def test_same_inputs_are_deterministic_and_not_mutated(self):
        observation = self.observation()
        policy = self.policy()
        before_observation = repr(observation)
        before_policy = repr(policy)
        for _ in range(5):
            self.assertIs(
                contract.assert_connection_settings_compatible(
                    observation,
                    access_mode=contract.READ_ONLY_ACCESS,
                    schema_policy=policy,
                ),
                observation,
            )
        self.assertEqual(repr(observation), before_observation)
        self.assertEqual(repr(policy), before_policy)

    def test_public_gate_has_no_bypass_or_default_policy(self):
        signature = inspect.signature(
            contract.assert_connection_settings_compatible
        )
        self.assertEqual(
            list(signature.parameters),
            ["observation", "access_mode", "schema_policy"],
        )
        self.assertIs(
            signature.parameters["access_mode"].default,
            inspect._empty,
        )
        self.assertIs(
            signature.parameters["schema_policy"].default,
            inspect._empty,
        )
        with self.assertRaises(TypeError):
            contract.assert_connection_settings_compatible(
                self.observation(),
                access_mode=contract.READ_ONLY_ACCESS,
                schema_policy=self.policy(),
                allow_unsupported=True,
            )

    def test_source_is_pure_and_does_not_claim_full_admission(self):
        source = Path(contract.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = set()
        call_attributes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.add(node.module)
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                call_attributes.append(ast.unparse(node.func))

        self.assertEqual(imports, {"__future__", "dataclasses"})
        self.assertEqual(call_attributes, [])

        forbidden = (
            "sqlite3.connect",
            "Path(",
            "open(",
            "os.",
            "subprocess",
            "socket",
            "requests",
        )
        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIn("NOT full V3 database admission", source)
        self.assertIn("schema_migrations", source)
        self.assertIn("migration checksums", source)
        self.assertIn("row_mapping_is_unambiguous", source)
        self.assertNotIn("row_mapping_is_sqlite_row", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
