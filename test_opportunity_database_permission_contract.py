from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
import inspect
from pathlib import Path
import unittest

import opportunity_database_permission_contract as contract


class OpportunityDatabasePermissionContractTests(unittest.TestCase):
    def observation(self, **changes):
        values = {
            "database_mode": 0o600,
            "wal_mode": 0o600,
            "shm_mode": 0o600,
        }
        values.update(changes)
        return contract.RuntimePermissionObservation(**values)

    def assert_rejected(self, observation):
        with self.assertRaises(
            contract.OpportunityDatabasePermissionContractError
        ):
            contract.assert_runtime_permissions_compatible(observation)

    def test_locked_contract_constants(self):
        self.assertEqual(
            contract.RUNTIME_PERMISSION_CONTRACT_VERSION,
            "opportunity_runtime_permissions:v1",
        )
        self.assertEqual(
            contract.REQUIRED_OWNER_PERMISSION_BITS,
            0o600,
        )
        self.assertEqual(
            contract.FORBIDDEN_GROUP_OTHER_PERMISSION_BITS,
            0o077,
        )
        self.assertEqual(
            contract.MAX_SUPPORTED_PERMISSION_MODE,
            0o7777,
        )

    def test_exact_0600_for_all_runtime_files_passes(self):
        observation = self.observation()
        self.assertIs(
            contract.assert_runtime_permissions_compatible(observation),
            observation,
        )

    def test_absent_sidecars_are_allowed_when_authoritatively_confirmed(self):
        observation = self.observation(
            wal_mode=None,
            shm_mode=None,
            wal_absence_confirmed=True,
            shm_absence_confirmed=True,
        )
        self.assertIs(
            contract.assert_runtime_permissions_compatible(observation),
            observation,
        )

    def test_unconfirmed_sidecar_absence_fails_closed(self):
        cases = (
            {
                "wal_mode": None,
                "wal_absence_confirmed": False,
            },
            {
                "shm_mode": None,
                "shm_absence_confirmed": False,
            },
        )
        for changes in cases:
            with self.subTest(changes=changes):
                self.assert_rejected(
                    self.observation(**changes)
                )

    def test_present_sidecar_cannot_be_confirmed_absent(self):
        for field in ("wal", "shm"):
            with self.subTest(field=field):
                with self.assertRaises(
                    contract.OpportunityDatabasePermissionContractError
                ):
                    self.observation(
                        **{
                            f"{field}_mode": 0o600,
                            f"{field}_absence_confirmed": True,
                        }
                    )

    def test_private_owner_execute_superset_is_allowed(self):
        for field in ("database_mode", "wal_mode", "shm_mode"):
            with self.subTest(field=field):
                observation = self.observation(**{field: 0o700})
                self.assertIs(
                    contract.assert_runtime_permissions_compatible(observation),
                    observation,
                )

    def test_database_must_exist_for_permission_admission(self):
        self.assert_rejected(
            self.observation(database_mode=None)
        )

    def test_existing_sidecars_fail_closed_when_not_private(self):
        invalid_modes = (
            0o000,
            0o200,
            0o400,
            0o640,
            0o604,
            0o660,
            0o666,
            0o777,
        )
        for field in ("wal_mode", "shm_mode"):
            for mode in invalid_modes:
                with self.subTest(field=field, mode=oct(mode)):
                    self.assert_rejected(
                        self.observation(**{field: mode})
                    )

    def test_database_permission_matrix_is_exact(self):
        accepted = []
        rejected = []

        for mode in range(0o1000):
            observation = self.observation(
                database_mode=mode,
                wal_mode=None,
                shm_mode=None,
                wal_absence_confirmed=True,
                shm_absence_confirmed=True,
            )
            try:
                contract.assert_runtime_permissions_compatible(observation)
            except contract.OpportunityDatabasePermissionContractError:
                rejected.append(mode)
            else:
                accepted.append(mode)

        self.assertEqual(accepted, [0o600, 0o700])
        self.assertEqual(len(rejected), 510)

    def test_special_permission_bits_are_not_invented_as_forbidden(self):
        accepted = []

        for mode in range(0o10000):
            observation = self.observation(
                database_mode=mode,
                wal_mode=None,
                shm_mode=None,
                wal_absence_confirmed=True,
                shm_absence_confirmed=True,
            )
            try:
                contract.assert_runtime_permissions_compatible(observation)
            except contract.OpportunityDatabasePermissionContractError:
                continue
            accepted.append(mode)

        expected = [
            special | owner
            for special in range(0, 0o10000, 0o1000)
            for owner in (0o600, 0o700)
        ]

        self.assertEqual(
            accepted,
            sorted(expected),
        )
        self.assertEqual(len(accepted), 16)

    def test_mode_metadata_types_fail_closed(self):
        invalid = (
            False,
            True,
            -1,
            0o10000,
            384.0,
            "0600",
            b"0600",
            object(),
        )
        for field in ("database_mode", "wal_mode", "shm_mode"):
            for value in invalid:
                with self.subTest(field=field, value=repr(value)):
                    with self.assertRaises(
                        contract.OpportunityDatabasePermissionContractError
                    ):
                        self.observation(**{field: value})

    def test_absence_confirmation_metadata_types_fail_closed(self):
        invalid = (
            None,
            0,
            1,
            "true",
            object(),
        )

        for field in (
            "wal_absence_confirmed",
            "shm_absence_confirmed",
        ):
            for value in invalid:
                with self.subTest(field=field, value=repr(value)):
                    with self.assertRaises(
                        contract.OpportunityDatabasePermissionContractError
                    ):
                        self.observation(**{field: value})

    def test_exact_contract_object_type_is_required(self):
        class SpoofedObservation(contract.RuntimePermissionObservation):
            def __getattribute__(self, name):
                if name == "database_mode":
                    return 0o600
                return super().__getattribute__(name)

        spoofed = SpoofedObservation(
            database_mode=0o644,
            wal_mode=None,
            shm_mode=None,
        )

        stored_mode = contract.RuntimePermissionObservation.__dict__[
            "database_mode"
        ].__get__(
            spoofed,
            contract.RuntimePermissionObservation,
        )
        self.assertEqual(stored_mode, 0o644)
        self.assert_rejected(spoofed)
        self.assert_rejected(object())

    def test_contract_record_is_immutable(self):
        observation = self.observation()
        with self.assertRaises(FrozenInstanceError):
            observation.database_mode = 0o644

    def test_same_input_is_deterministic_and_not_mutated(self):
        observation = self.observation(
            wal_mode=None,
            shm_mode=0o700,
            wal_absence_confirmed=True,
        )
        before = repr(observation)

        for _ in range(5):
            self.assertIs(
                contract.assert_runtime_permissions_compatible(observation),
                observation,
            )

        self.assertEqual(repr(observation), before)

    def test_public_gate_has_no_bypass_arguments(self):
        signature = inspect.signature(
            contract.assert_runtime_permissions_compatible
        )
        self.assertEqual(
            list(signature.parameters),
            ["observation"],
        )

        with self.assertRaises(TypeError):
            contract.assert_runtime_permissions_compatible(
                self.observation(),
                allow_insecure=True,
            )

    def test_source_is_pure_and_does_not_claim_extra_d006_rules(self):
        source = Path(contract.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)

        imports = set()
        attribute_calls = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.add(node.module)
            elif isinstance(node, ast.Call) and isinstance(
                node.func,
                ast.Attribute,
            ):
                attribute_calls.append(ast.unparse(node.func))

        self.assertEqual(imports, {"__future__", "dataclasses"})
        self.assertEqual(attribute_calls, [])

        for token in (
            "sqlite3",
            "Path(",
            "open(",
            "os.",
            "subprocess",
            "socket",
            "requests",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        normalized = " ".join(source.split())
        self.assertIn(
            "does not invent a UID/GID ownership requirement",
            normalized,
        )
        self.assertIn(
            "does not invent a symlink policy",
            normalized,
        )
        self.assertIn(
            "authoritatively confirmed absence",
            normalized,
        )
        self.assertIn(
            "unknown or unobservable state must remain unconfirmed",
            normalized,
        )
        self.assertIn(
            "NOT full V3 database admission",
            normalized,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
