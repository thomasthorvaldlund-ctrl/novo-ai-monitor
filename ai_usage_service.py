import fcntl
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from aureum_paths import log_path


AI_USAGE_FILE = Path(
    log_path(
        "ai_usage_history.jsonl"
    )
)


def _value(
    obj,
    key,
    default=None,
):
    if obj is None:
        return default

    if isinstance(
        obj,
        dict,
    ):
        return obj.get(
            key,
            default,
        )

    return getattr(
        obj,
        key,
        default,
    )


def _integer(
    value,
):
    try:
        return int(
            value
            or 0
        )
    except (
        TypeError,
        ValueError,
    ):
        return 0


def extract_ai_usage(
    response,
):
    """
    Normaliserer OpenAI usage-data.

    Chat Completions:
    prompt_tokens -> input_tokens
    completion_tokens -> output_tokens

    Responses API understøttes også via
    input_tokens/output_tokens fallback.
    """
    usage = _value(
        response,
        "usage",
    )

    if usage is None:
        return {
            "usage_available":
                False,

            "input_tokens":
                0,

            "cached_input_tokens":
                0,

            "output_tokens":
                0,

            "reasoning_tokens":
                0,

            "total_tokens":
                0,
        }

    input_tokens = _integer(
        _value(
            usage,
            "prompt_tokens",
            _value(
                usage,
                "input_tokens",
                0,
            ),
        )
    )

    output_tokens = _integer(
        _value(
            usage,
            "completion_tokens",
            _value(
                usage,
                "output_tokens",
                0,
            ),
        )
    )

    total_tokens = _integer(
        _value(
            usage,
            "total_tokens",
            (
                input_tokens
                + output_tokens
            ),
        )
    )

    input_details = _value(
        usage,
        "prompt_tokens_details",
        _value(
            usage,
            "input_tokens_details",
        ),
    )

    output_details = _value(
        usage,
        "completion_tokens_details",
        _value(
            usage,
            "output_tokens_details",
        ),
    )

    cached_input_tokens = _integer(
        _value(
            input_details,
            "cached_tokens",
            0,
        )
    )

    reasoning_tokens = _integer(
        _value(
            output_details,
            "reasoning_tokens",
            0,
        )
    )

    return {
        "usage_available":
            True,

        "input_tokens":
            input_tokens,

        "cached_input_tokens":
            cached_input_tokens,

        "output_tokens":
            output_tokens,

        "reasoning_tokens":
            reasoning_tokens,

        "total_tokens":
            total_tokens,
    }


def record_ai_usage(
    response,
    *,
    service,
    requested_model,
    operation=None,
    instrument=None,
    route=None,
    usage_file=None,
):
    """
    Gemmer én AI-usage event som JSONL.

    Prompts, messages og API credentials gemmes aldrig.
    """
    if not service:
        raise ValueError(
            "service er obligatorisk."
        )

    path = (
        Path(
            usage_file
        )
        if usage_file is not None
        else AI_USAGE_FILE
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    usage = extract_ai_usage(
        response
    )

    record = {
        "recorded_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "service":
            str(
                service
            ),

        "operation":
            (
                str(
                    operation
                )
                if operation
                else None
            ),

        "instrument":
            (
                str(
                    instrument
                )
                if instrument
                else None
            ),

        "route":
            (
                str(
                    route
                )
                if route
                else None
            ),

        "requested_model":
            (
                str(
                    requested_model
                )
                if requested_model
                else None
            ),

        "response_model":
            (
                str(
                    _value(
                        response,
                        "model",
                    )
                )
                if _value(
                    response,
                    "model",
                )
                else None
            ),

        **usage,
    }

    line = json.dumps(
        record,
        ensure_ascii=False,
        separators=(
            ",",
            ":",
        ),
    )

    with path.open(
        "a",
        encoding="utf-8",
    ) as handle:

        fcntl.flock(
            handle.fileno(),
            fcntl.LOCK_EX,
        )

        try:
            handle.write(
                line
                + "\n"
            )

            handle.flush()

            os.fsync(
                handle.fileno()
            )

        finally:
            fcntl.flock(
                handle.fileno(),
                fcntl.LOCK_UN,
            )

    return record
