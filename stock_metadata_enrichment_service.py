"""
Aureum AI Stock Metadata Enrichment Service

Checkpointet indsamling af rå metadata for canonical stocks,
som stadig har sector=Unknown.

Servicen ændrer aldrig stock_universe.csv.
"""

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from aureum_paths import cache_path
from market_data_provider import (
    get_metadata as provider_get_metadata,
    get_provider_name,
)
from stock_universe_service import get_all_stocks


CACHE_FILE = cache_path(
    "stock_metadata_enrichment_cache.json"
)

DEFAULT_BATCH_SIZE = 25
DEFAULT_REQUEST_PAUSE_SECONDS = 0.4


def _usable(value):
    if value is None:
        return False

    value = str(value).strip()

    return (
        bool(value)
        and value.casefold()
        not in {
            "unknown",
            "none",
            "n/a",
            "null",
        }
    )


def _clean(value):
    if not _usable(value):
        return None

    return str(value).strip()


def _get_batch_size():
    try:
        value = int(
            os.getenv(
                "AUREUM_METADATA_BATCH_SIZE",
                str(DEFAULT_BATCH_SIZE),
            )
        )
    except (TypeError, ValueError):
        value = DEFAULT_BATCH_SIZE

    return max(1, value)


def _get_pause_seconds():
    try:
        value = float(
            os.getenv(
                "AUREUM_METADATA_REQUEST_PAUSE_SECONDS",
                str(DEFAULT_REQUEST_PAUSE_SECONDS),
            )
        )
    except (TypeError, ValueError):
        value = DEFAULT_REQUEST_PAUSE_SECONDS

    return max(0.0, value)


def _load_cache(cache_file=None):
    path = Path(
        cache_file or CACHE_FILE
    )

    if not path.exists():
        return {
            "results": {},
            "scan_state": {},
        }

    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as handle:
            data = json.load(handle)
    except (
        OSError,
        json.JSONDecodeError,
    ):
        return {
            "results": {},
            "scan_state": {},
        }

    if not isinstance(data, dict):
        return {
            "results": {},
            "scan_state": {},
        }

    results = data.get(
        "results",
        {},
    )

    state = data.get(
        "scan_state",
        {},
    )

    return {
        "results":
            results
            if isinstance(results, dict)
            else {},
        "scan_state":
            state
            if isinstance(state, dict)
            else {},
    }


def _save_cache(data, cache_file=None):
    path = Path(
        cache_file or CACHE_FILE
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp = path.with_suffix(
        path.suffix + ".tmp"
    )

    with temp.open(
        "w",
        encoding="utf-8",
    ) as handle:

        json.dump(
            data,
            handle,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )

        handle.flush()
        os.fsync(handle.fileno())

    temp.replace(path)


def _get_unknown_sector_items(stocks=None):
    universe = (
        stocks
        if stocks is not None
        else get_all_stocks()
    )

    items = []

    for symbol, stock in universe.items():

        sector = str(
            stock.get(
                "sector",
                "",
            )
            or ""
        ).strip()

        if sector.casefold() != "unknown":
            continue

        ticker = str(
            stock.get(
                "ticker",
                "",
            )
            or ""
        ).strip().upper()

        if not ticker:
            continue

        items.append(
            (
                symbol,
                stock,
            )
        )

    return items


def _select_batch(
    items,
    cursor,
    batch_size,
):
    total = len(items)

    if total == 0:
        return (
            [],
            0,
            0,
            True,
        )

    start = cursor % total

    end = min(
        start + batch_size,
        total,
    )

    batch = items[
        start:end
    ]

    completed = (
        end >= total
    )

    next_cursor = (
        0
        if completed
        else end
    )

    return (
        batch,
        start,
        next_cursor,
        completed,
    )


def _success_result(
    symbol,
    stock,
    info,
):
    sector = _clean(
        info.get("sector")
    )

    industry = _clean(
        info.get("industry")
    )

    provider_country = _clean(
        info.get("country")
    )

    return {
        "symbol":
            symbol,
        "ticker":
            stock.get("ticker"),
        "name":
            stock.get("name"),

        "canonical_sector":
            stock.get("sector"),
        "canonical_country":
            stock.get("country"),
        "canonical_market":
            stock.get("market"),

        "provider_sector":
            sector,
        "provider_industry":
            industry,
        "provider_country":
            provider_country,

        "provider_exchange":
            _clean(
                info.get("exchange")
            ),

        "provider_full_exchange":
            _clean(
                info.get(
                    "fullExchangeName"
                )
            ),

        "provider_currency":
            _clean(
                info.get("currency")
            ),

        "quote_type":
            _clean(
                info.get("quoteType")
            ),

        "provider_long_name":
            _clean(
                info.get("longName")
                or info.get("shortName")
            ),

        "sector_usable":
            bool(sector),

        "industry_usable":
            bool(industry),

        "provider_country_usable":
            bool(provider_country),

        "status":
            (
                "OK"
                if sector
                else "PARTIAL"
            ),

        "error":
            None,

        "observed_at":
            datetime.now(
                timezone.utc
            ).isoformat(),
    }


def _error_result(
    symbol,
    stock,
    ticker,
    exc,
):
    return {
        "symbol":
            symbol,
        "ticker":
            ticker,
        "name":
            stock.get("name"),

        "canonical_sector":
            stock.get("sector"),
        "canonical_country":
            stock.get("country"),
        "canonical_market":
            stock.get("market"),

        "provider_sector":
            None,
        "provider_industry":
            None,
        "provider_country":
            None,
        "provider_exchange":
            None,
        "provider_full_exchange":
            None,
        "provider_currency":
            None,
        "quote_type":
            None,
        "provider_long_name":
            None,

        "sector_usable":
            False,
        "industry_usable":
            False,
        "provider_country_usable":
            False,

        "status":
            "ERROR",

        "error":
            (
                f"{type(exc).__name__}: "
                f"{exc}"
            ),

        "observed_at":
            datetime.now(
                timezone.utc
            ).isoformat(),
    }


def build_stock_metadata_enrichment_cache(
    *,
    fetcher=None,
    stocks=None,
    cache_file=None,
    batch_size=None,
    pause_seconds=None,
):
    """
    Scanner næste metadata-batch.

    Kun cachefilen skrives.
    Canonical stock_universe.csv ændres aldrig.
    """

    provider = (
        fetcher
        or provider_get_metadata
    )

    items = _get_unknown_sector_items(
        stocks=stocks
    )

    existing = _load_cache(
        cache_file=cache_file
    )

    results = dict(
        existing.get(
            "results",
            {},
        )
    )

    previous_state = existing.get(
        "scan_state",
        {},
    )

    try:
        cursor = int(
            previous_state.get(
                "next_cursor",
                0,
            )
        )
    except (
        TypeError,
        ValueError,
    ):
        cursor = 0

    actual_batch_size = (
        int(batch_size)
        if batch_size is not None
        else _get_batch_size()
    )

    actual_batch_size = max(
        1,
        actual_batch_size,
    )

    actual_pause = (
        float(pause_seconds)
        if pause_seconds is not None
        else _get_pause_seconds()
    )

    actual_pause = max(
        0.0,
        actual_pause,
    )

    (
        batch,
        cursor_start,
        next_cursor,
        cycle_completed,
    ) = _select_batch(
        items,
        cursor,
        actual_batch_size,
    )

    batch_tickers = []

    for index, (
        symbol,
        stock,
    ) in enumerate(batch):

        ticker = str(
            stock.get(
                "ticker",
                "",
            )
            or ""
        ).strip().upper()

        batch_tickers.append(
            ticker
        )

        try:
            info = provider(
                ticker
            )

            if not isinstance(
                info,
                dict,
            ):
                raise TypeError(
                    "Provider returnerede ikke dict"
                )

            result = _success_result(
                symbol,
                stock,
                info,
            )

        except Exception as exc:
            result = _error_result(
                symbol,
                stock,
                ticker,
                exc,
            )

        results[ticker] = result

        if (
            actual_pause > 0
            and index
            < len(batch) - 1
        ):
            time.sleep(
                actual_pause
            )

    unknown_tickers = {
        str(
            stock.get(
                "ticker",
                "",
            )
            or ""
        ).strip().upper()
        for _, stock in items
    }

    current_results = [
        result
        for ticker, result
        in results.items()
        if ticker in unknown_tickers
    ]

    observed = len(
        current_results
    )

    usable_sector = sum(
        bool(
            result.get(
                "sector_usable"
            )
        )
        for result in current_results
    )

    usable_industry = sum(
        bool(
            result.get(
                "industry_usable"
            )
        )
        for result in current_results
    )

    errors = sum(
        result.get(
            "status"
        )
        == "ERROR"
        for result in current_results
    )

    unseen = sum(
        ticker not in results
        for ticker in unknown_tickers
    )

    data = {
        "metadata_source":
            get_provider_name(),

        "canonical_country_semantics":
            "listing_country_preserved",

        "canonical_file_modified":
            False,

        "results":
            results,

        "scan_state": {
            "total_unknown":
                len(items),

            "batch_size":
                actual_batch_size,

            "cursor_start":
                cursor_start,

            "next_cursor":
                next_cursor,

            "batch_scanned":
                len(batch),

            "batch_tickers":
                batch_tickers,

            "cycle_completed":
                cycle_completed,

            "observed_results":
                observed,

            "unseen_tickers":
                unseen,

            "usable_sector":
                usable_sector,

            "usable_industry":
                usable_industry,

            "errors":
                errors,
        },

        "updated_at":
            datetime.now(
                timezone.utc
            ).isoformat(),
    }

    _save_cache(
        data,
        cache_file=cache_file,
    )

    return data
