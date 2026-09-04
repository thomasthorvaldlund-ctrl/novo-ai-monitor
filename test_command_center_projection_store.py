from copy import deepcopy
import json
import os
from pathlib import Path
import stat
from tempfile import TemporaryDirectory

import command_center_projection_store as store

from command_center_projection_builder import (
    build_command_center_projection,
)
from command_center_projection_contract import (
    ProjectionValidationError,
)


GLOBAL_SCOPE = {
    "kind": "GLOBAL",
}


def projection(
    projection_id,
    *,
    materialized_at,
    as_of,
    source_cutoff,
):
    return build_command_center_projection(
        command_center_projection_id=projection_id,
        presentation_policy_version=(
            "command_center_presentation:v1"
        ),
        materialized_at=materialized_at,
        as_of=as_of,
        source_cutoff=source_cutoff,
        source_references=[
            f"source:{projection_id}",
        ],
        scope=GLOBAL_SCOPE,
        build_status="COMPLETE",
        sections={
            "attention": {
                "availability": "AVAILABLE",
                "freshness": "CURRENT",
                "source_as_of": source_cutoff,
                "source_references": [
                    f"source:attention:{projection_id}",
                ],
            },
            "portfolio_relevance": {
                "availability": "UNAVAILABLE",
                "freshness": "UNKNOWN",
                "source_as_of": None,
                "source_references": [],
            },
        },
    )


def load(path, scope=GLOBAL_SCOPE):
    return store.load_command_center_projection(
        path,
        expected_scope=scope,
    )


def run_test():
    with TemporaryDirectory(
        prefix="aureum-v3-projection-store-"
    ) as temp_dir:
        root = Path(temp_dir)
        path = root / "projection.json"
        lock_path = root / "projection.json.lock"

        # Pure read on a missing projection must not create a lock/file.
        assert load(path) is None
        assert not path.exists()
        assert not lock_path.exists()

        first = projection(
            "projection-1",
            materialized_at=(
                "2026-09-04T18:00:00+00:00"
            ),
            as_of=(
                "2026-09-04T18:00:00+00:00"
            ),
            source_cutoff=(
                "2026-09-04T17:59:00+00:00"
            ),
        )

        first_before = deepcopy(first)

        published_1 = (
            store.publish_command_center_projection(
                first,
                path,
                expected_scope=GLOBAL_SCOPE,
                expected_current_projection_id=None,
                required_sections={
                    "attention",
                },
                required_source_sections={
                    "attention",
                },
            )
        )

        assert first == first_before
        assert published_1 == first
        assert path.exists()
        assert lock_path.exists()

        assert stat.S_IMODE(
            path.stat().st_mode
        ) == 0o600

        assert stat.S_IMODE(
            lock_path.stat().st_mode
        ) == 0o600

        on_disk_1 = load(path)
        assert on_disk_1 == published_1

        # One-shot policy iterables must be preserved across both
        # candidate validations performed before publication.
        policy_path = root / "policy.json"

        policy_candidate = projection(
            "projection-policy",
            materialized_at=(
                "2026-09-04T17:50:00+00:00"
            ),
            as_of=(
                "2026-09-04T17:50:00+00:00"
            ),
            source_cutoff=(
                "2026-09-04T17:49:00+00:00"
            ),
        )

        original_validator = (
            store.assert_valid_command_center_projection
        )
        validation_calls = []

        def validator_spy(
            value,
            *,
            required_sections=(),
            required_source_sections=(),
        ):
            sections = tuple(
                required_sections
            )
            source_sections = tuple(
                required_source_sections
            )

            validation_calls.append(
                (
                    sections,
                    source_sections,
                )
            )

            return original_validator(
                value,
                required_sections=sections,
                required_source_sections=(
                    source_sections
                ),
            )

        store.assert_valid_command_center_projection = (
            validator_spy
        )

        try:
            store.publish_command_center_projection(
                policy_candidate,
                policy_path,
                expected_scope=GLOBAL_SCOPE,
                expected_current_projection_id=None,
                required_sections=(
                    item
                    for item in ["attention"]
                ),
                required_source_sections=(
                    item
                    for item in ["attention"]
                ),
            )
        finally:
            store.assert_valid_command_center_projection = (
                original_validator
            )

        assert validation_calls == [
            (
                ("attention",),
                ("attention",),
            ),
            (
                ("attention",),
                ("attention",),
            ),
        ]

        # Exact same identity/content is idempotent and does not rewrite.
        before_bytes = path.read_bytes()
        before_mtime = path.stat().st_mtime_ns

        idempotent = (
            store.publish_command_center_projection(
                first,
                path,
                expected_scope=GLOBAL_SCOPE,
                expected_current_projection_id=(
                    "projection-1"
                ),
            )
        )

        assert idempotent == first
        assert path.read_bytes() == before_bytes
        assert (
            path.stat().st_mtime_ns
            == before_mtime
        )

        second = projection(
            "projection-2",
            materialized_at=(
                "2026-09-04T18:05:00+00:00"
            ),
            as_of=(
                "2026-09-04T18:05:00+00:00"
            ),
            source_cutoff=(
                "2026-09-04T18:04:00+00:00"
            ),
        )

        # Even if an existing publication was accidentally broadened,
        # the next atomic publication must create a private 0600 inode.
        os.chmod(
            path,
            0o644,
        )

        assert stat.S_IMODE(
            path.stat().st_mode
        ) == 0o644

        published_2 = (
            store.publish_command_center_projection(
                second,
                path,
                expected_scope=GLOBAL_SCOPE,
                expected_current_projection_id=(
                    "projection-1"
                ),
            )
        )

        assert published_2 == second
        assert load(path) == second

        assert stat.S_IMODE(
            path.stat().st_mode
        ) == 0o600

        stable_bytes = path.read_bytes()

        # A stale writer using the old CAS id must not overwrite v2.
        third = projection(
            "projection-3",
            materialized_at=(
                "2026-09-04T18:06:00+00:00"
            ),
            as_of=(
                "2026-09-04T18:06:00+00:00"
            ),
            source_cutoff=(
                "2026-09-04T18:05:00+00:00"
            ),
        )

        try:
            store.publish_command_center_projection(
                third,
                path,
                expected_scope=GLOBAL_SCOPE,
                expected_current_projection_id=(
                    "projection-1"
                ),
            )
        except store.ProjectionStoreConflictError:
            pass
        else:
            raise AssertionError(
                "Stale CAS writer must fail"
            )

        assert path.read_bytes() == stable_bytes
        assert load(path) == second

        # A new id may not regress publication timestamps.
        regressed = projection(
            "projection-regressed",
            materialized_at=(
                "2026-09-04T18:04:00+00:00"
            ),
            as_of=(
                "2026-09-04T18:04:00+00:00"
            ),
            source_cutoff=(
                "2026-09-04T18:03:00+00:00"
            ),
        )

        try:
            store.publish_command_center_projection(
                regressed,
                path,
                expected_scope=GLOBAL_SCOPE,
                expected_current_projection_id=(
                    "projection-2"
                ),
            )
        except store.ProjectionStoreRegressionError:
            pass
        else:
            raise AssertionError(
                "Regressed publication must fail"
            )

        assert path.read_bytes() == stable_bytes

        # Same projection id with different content is forbidden.
        identity_conflict = deepcopy(second)
        identity_conflict[
            "build_status"
        ] = "DIFFERENT"

        try:
            store.publish_command_center_projection(
                identity_conflict,
                path,
                expected_scope=GLOBAL_SCOPE,
                expected_current_projection_id=(
                    "projection-2"
                ),
            )
        except (
            store.ProjectionStoreIdentityConflictError
        ):
            pass
        else:
            raise AssertionError(
                "Projection identity must be immutable"
            )

        assert path.read_bytes() == stable_bytes

        # Invalid candidate must fail before publication.
        invalid = deepcopy(third)
        invalid[
            "sections"
        ][
            "attention"
        ][
            "freshness"
        ] = "LIVE"

        try:
            store.publish_command_center_projection(
                invalid,
                path,
                expected_scope=GLOBAL_SCOPE,
                expected_current_projection_id=(
                    "projection-2"
                ),
            )
        except ProjectionValidationError:
            pass
        else:
            raise AssertionError(
                "Invalid candidate must fail validation"
            )

        assert path.read_bytes() == stable_bytes

        # Scope mismatch must fail on publish and load.
        wrong_scope = {
            "kind": "PERSONAL",
            "scope_id": "principal-other",
        }

        try:
            store.publish_command_center_projection(
                third,
                path,
                expected_scope=wrong_scope,
                expected_current_projection_id=(
                    "projection-2"
                ),
            )
        except (
            store.ProjectionStoreScopeMismatchError
        ):
            pass
        else:
            raise AssertionError(
                "Publish scope mismatch must fail"
            )

        try:
            load(path, wrong_scope)
        except (
            store.ProjectionStoreScopeMismatchError
        ):
            pass
        else:
            raise AssertionError(
                "Read scope mismatch must fail"
            )

        assert path.read_bytes() == stable_bytes

        # JSON serialization must not silently change reader-visible
        # business payload shapes, such as integer mapping keys becoming
        # strings. Lossy candidates must be rejected before publication.
        lossy_new_path = (
            root / "lossy-new.json"
        )

        lossy_new = projection(
            "projection-lossy-new",
            materialized_at=(
                "2026-09-04T18:06:30+00:00"
            ),
            as_of=(
                "2026-09-04T18:06:30+00:00"
            ),
            source_cutoff=(
                "2026-09-04T18:05:30+00:00"
            ),
        )

        lossy_new[
            "sections"
        ][
            "attention"
        ][
            "payload"
        ] = {
            "numeric_keyed_map": {
                1: "one",
            },
        }

        lossy_new_before = deepcopy(
            lossy_new
        )

        try:
            store.publish_command_center_projection(
                lossy_new,
                lossy_new_path,
                expected_scope=GLOBAL_SCOPE,
                expected_current_projection_id=None,
            )
        except (
            store.ProjectionStoreSerializationError
        ):
            pass
        else:
            raise AssertionError(
                "Lossy JSON candidate must be rejected"
            )

        assert lossy_new == lossy_new_before
        assert not lossy_new_path.exists()

        lossy_existing = projection(
            "projection-lossy-existing",
            materialized_at=(
                "2026-09-04T18:06:45+00:00"
            ),
            as_of=(
                "2026-09-04T18:06:45+00:00"
            ),
            source_cutoff=(
                "2026-09-04T18:05:45+00:00"
            ),
        )

        lossy_existing[
            "sections"
        ][
            "attention"
        ][
            "payload"
        ] = {
            "numeric_keyed_map": {
                1: "one",
            },
        }

        try:
            store.publish_command_center_projection(
                lossy_existing,
                path,
                expected_scope=GLOBAL_SCOPE,
                expected_current_projection_id=(
                    "projection-2"
                ),
            )
        except (
            store.ProjectionStoreSerializationError
        ):
            pass
        else:
            raise AssertionError(
                "Lossy JSON update must be rejected"
            )

        assert path.read_bytes() == stable_bytes
        assert load(path) == second

        # Simulated replace failure must preserve the old publication.
        fourth = projection(
            "projection-4",
            materialized_at=(
                "2026-09-04T18:07:00+00:00"
            ),
            as_of=(
                "2026-09-04T18:07:00+00:00"
            ),
            source_cutoff=(
                "2026-09-04T18:06:00+00:00"
            ),
        )

        original_replace = store.os.replace

        def failing_replace(*args, **kwargs):
            raise OSError(
                "simulated replace failure"
            )

        store.os.replace = failing_replace

        try:
            try:
                store.publish_command_center_projection(
                    fourth,
                    path,
                    expected_scope=GLOBAL_SCOPE,
                    expected_current_projection_id=(
                        "projection-2"
                    ),
                )
            except OSError:
                pass
            else:
                raise AssertionError(
                    "Simulated replace failure expected"
                )
        finally:
            store.os.replace = original_replace

        assert path.read_bytes() == stable_bytes
        assert load(path) == second

        # If replacement succeeds but directory durability sync fails,
        # publication status is ambiguous: the new coherent projection
        # may already be reader-visible. The caller must re-read current.
        ambiguous_path = (
            root / "ambiguous.json"
        )

        ambiguous_current = projection(
            "projection-ambiguous-current",
            materialized_at=(
                "2026-09-04T18:10:00+00:00"
            ),
            as_of=(
                "2026-09-04T18:10:00+00:00"
            ),
            source_cutoff=(
                "2026-09-04T18:09:00+00:00"
            ),
        )

        ambiguous_next = projection(
            "projection-ambiguous-next",
            materialized_at=(
                "2026-09-04T18:11:00+00:00"
            ),
            as_of=(
                "2026-09-04T18:11:00+00:00"
            ),
            source_cutoff=(
                "2026-09-04T18:10:00+00:00"
            ),
        )

        store.publish_command_center_projection(
            ambiguous_current,
            ambiguous_path,
            expected_scope=GLOBAL_SCOPE,
            expected_current_projection_id=None,
        )

        ambiguous_before = (
            ambiguous_path.read_bytes()
        )

        original_fsync = store.os.fsync
        fsync_calls = {
            "count": 0,
        }

        def failing_directory_fsync(
            descriptor,
        ):
            fsync_calls["count"] += 1

            # First call syncs the completed temporary file.
            # Second call syncs the parent directory after os.replace.
            if fsync_calls["count"] == 2:
                raise OSError(
                    "simulated directory fsync failure"
                )

            return original_fsync(
                descriptor
            )

        store.os.fsync = (
            failing_directory_fsync
        )

        try:
            try:
                store.publish_command_center_projection(
                    ambiguous_next,
                    ambiguous_path,
                    expected_scope=GLOBAL_SCOPE,
                    expected_current_projection_id=(
                        "projection-ambiguous-current"
                    ),
                )
            except (
                store.ProjectionStorePublicationAmbiguousError
            ):
                pass
            else:
                raise AssertionError(
                    "Post-replace durability failure "
                    "must be marked ambiguous"
                )
        finally:
            store.os.fsync = original_fsync

        assert fsync_calls["count"] == 2

        ambiguous_after = (
            ambiguous_path.read_bytes()
        )

        assert (
            ambiguous_after
            != ambiguous_before
        )

        recovered = load(
            ambiguous_path
        )

        assert recovered == ambiguous_next

        temporary_files = list(
            root.glob(
                ".projection.json.*.tmp"
            )
        )

        assert temporary_files == []

        # Reader-visible JSON is a complete valid projection.
        raw = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        assert raw[
            "command_center_projection_id"
        ] == "projection-2"

        # Invalid current publication must fail honestly.
        corrupt_path = (
            root / "corrupt.json"
        )

        corrupt_path.write_text(
            "{not-json",
            encoding="utf-8",
        )

        corrupt_lock = (
            root / "corrupt.json.lock"
        )

        try:
            store.load_command_center_projection(
                corrupt_path,
                expected_scope=GLOBAL_SCOPE,
            )
        except store.ProjectionStoreCorruptError:
            pass
        else:
            raise AssertionError(
                "Corrupt publication must fail"
            )

        # Read path must not create a lock even for corrupt content.
        assert not corrupt_lock.exists()

        print("missing_read_side_effect_free: PASS")
        print("first_atomic_publication: PASS")
        print("published_file_mode_private: PASS")
        print("publication_lock_mode_private: PASS")
        print("read_back_valid: PASS")
        print("one_shot_policy_iterables_preserved: PASS")
        print("idempotent_republish_no_rewrite: PASS")
        print("publication_rehardens_private_mode: PASS")
        print("cas_update: PASS")
        print("stale_writer_rejected: PASS")
        print("timestamp_regression_rejected: PASS")
        print("projection_identity_immutable: PASS")
        print("invalid_candidate_not_published: PASS")
        print("scope_mismatch_rejected: PASS")
        print("lossy_json_new_publication_rejected: PASS")
        print("lossy_json_update_rejected: PASS")
        print("lossy_json_preserves_current: PASS")
        print("replace_failure_preserves_previous: PASS")
        print("post_replace_failure_marked_ambiguous: PASS")
        print("ambiguous_publication_recoverable_by_reread: PASS")
        print("temporary_file_cleanup: PASS")
        print("corrupt_current_fails_honestly: PASS")
        print("read_path_creates_no_lock: PASS")
        print(
            "command_center_projection_store_test: OK"
        )


if __name__ == "__main__":
    run_test()
