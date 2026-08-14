import json
import math
import os

from aureum_paths import cache_path
from market_data_provider import get_history
from currency_service import (
    get_fx_rates,
    get_currency,
    convert_to_dkk,
)
from stock_universe_service import get_active_stocks
from portfolio_stock_service import get_monitored_stock_map


CACHE_FILE = cache_path(
    "stock_screener_cache.json"
)

DEFAULT_BATCH_SIZE = 50


def _get_batch_size():
    """
    Returnerer antal ordinary universe-stocks pr. screener-kørsel.

    Standard 50 betyder, at et univers på 1.000 aktier bliver
    gennemgået over 20 planlagte kørsler i stedet for at sende
    1.000 eksterne market-data kald i samme job.
    """
    raw_value = os.getenv(
        "AUREUM_STOCK_SCREENER_BATCH_SIZE",
        str(DEFAULT_BATCH_SIZE),
    )

    try:
        value = int(raw_value)

    except (TypeError, ValueError):
        value = DEFAULT_BATCH_SIZE

    return max(
        1,
        value,
    )


def _load_existing_cache():
    if not CACHE_FILE.exists():
        return {
            "ranking": [],
            "scan_state": {},
        }

    try:
        with CACHE_FILE.open(
            "r",
            encoding="utf-8",
        ) as handle:
            data = json.load(handle)

    except (
        OSError,
        json.JSONDecodeError,
    ):
        return {
            "ranking": [],
            "scan_state": {},
        }

    if not isinstance(
        data,
        dict,
    ):
        return {
            "ranking": [],
            "scan_state": {},
        }

    ranking = data.get(
        "ranking",
        [],
    )

    if not isinstance(
        ranking,
        list,
    ):
        ranking = []

    scan_state = data.get(
        "scan_state",
        {},
    )

    if not isinstance(
        scan_state,
        dict,
    ):
        scan_state = {}

    return {
        "ranking": ranking,
        "scan_state": scan_state,
    }


def _scan_stock(
    name,
    ticker,
    fx_rates,
):
    try:
        data = get_history(
            ticker,
            period="10d",
        )

        data = data.dropna(
            subset=["Close"]
        )

        if (
            data.empty
            or len(data.index) < 6
        ):
            raise ValueError(
                "Ikke nok gyldige kursdata til beregning"
            )

        latest = float(
            data["Close"].iloc[-1]
        )

        week_ago = float(
            data["Close"].iloc[-6]
        )

        currency = get_currency(
            ticker
        )

        latest_dkk = convert_to_dkk(
            latest,
            currency,
            fx_rates,
        )

        weekly_change = (
            (
                latest
                - week_ago
            )
            / week_ago
        ) * 100

        if not all(
            math.isfinite(value)
            for value in (
                latest,
                week_ago,
                latest_dkk,
                weekly_change,
            )
        ):
            raise ValueError(
                "Ugyldige kurs- eller valutadata"
            )

        score = 50

        if weekly_change > 5:
            score += 20

        elif weekly_change > 2:
            score += 10

        if weekly_change < -5:
            score -= 20

        return {
            "stock": name,
            "ticker": ticker,
            "price": round(
                latest_dkk,
                2,
            ),
            "original_price": round(
                latest,
                2,
            ),
            "currency": currency,
            "weekly_change": round(
                weekly_change,
                2,
            ),
            "score": score,
        }

    except Exception as exc:
        return {
            "stock": name,
            "error": str(exc),
        }


def _select_regular_batch(
    items,
    cursor,
    batch_size,
):
    """
    Vælger næste sekventielle del af universet.

    Der wrap'es ikke midt i samme batch. Ved slutningen sættes
    cursor tilbage til 0, så næste cron-kørsel starter en ny
    komplet scanningcyklus.
    """
    total = len(items)

    if total == 0:
        return (
            [],
            0,
            0,
            True,
        )

    start = (
        cursor % total
    )

    end = min(
        start + batch_size,
        total,
    )

    batch = items[
        start:end
    ]

    cycle_completed = (
        end >= total
    )

    next_cursor = (
        0
        if cycle_completed
        else end
    )

    return (
        batch,
        start,
        next_cursor,
        cycle_completed,
    )


def build_stock_screener_cache():
    """
    Opdaterer screener-cachen inkrementelt.

    Aktive stocks scannes i batches. Portfolio-stocks prioriteres
    på hver kørsel, så en stor global universe-scan ikke gør
    portfolio-data langsommere at opdatere.

    Cache-readers ser fortsat én samlet "ranking"-liste.
    """
    watchlist = (
        get_active_stocks()
    )

    portfolio_map = (
        get_monitored_stock_map()
    )

    for stock_name, ticker in (
        portfolio_map.items()
    ):
        if ticker not in watchlist.values():
            watchlist[
                stock_name
            ] = ticker

    items = list(
        watchlist.items()
    )

    total_watchlist = len(
        items
    )

    existing = (
        _load_existing_cache()
    )

    existing_ranking = (
        existing.get(
            "ranking",
            [],
        )
    )

    current_names = set(
        watchlist
    )

    ranking_map = {
        item.get("stock"): item
        for item in existing_ranking
        if (
            isinstance(
                item,
                dict,
            )
            and item.get("stock")
            in current_names
        )
    }

    previous_state = (
        existing.get(
            "scan_state",
            {},
        )
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

    batch_size = (
        _get_batch_size()
    )

    (
        regular_batch,
        cursor_start,
        next_cursor,
        cycle_completed,
    ) = _select_regular_batch(
        items,
        cursor,
        batch_size,
    )

    selected = []
    selected_names = set()

    # Portfolio-stocks får altid høj prioritet.
    for stock_name, ticker in (
        portfolio_map.items()
    ):
        if (
            stock_name in watchlist
            and stock_name
            not in selected_names
        ):
            selected.append(
                (
                    stock_name,
                    watchlist[
                        stock_name
                    ],
                )
            )

            selected_names.add(
                stock_name
            )

    # Derefter den ordinære universe-batch.
    for stock_name, ticker in (
        regular_batch
    ):
        if (
            stock_name
            in selected_names
        ):
            continue

        selected.append(
            (
                stock_name,
                ticker,
            )
        )

        selected_names.add(
            stock_name
        )

    fx_rates = get_fx_rates()

    updated_results = []

    for name, ticker in selected:
        item = _scan_stock(
            name,
            ticker,
            fx_rates,
        )

        ranking_map[
            name
        ] = item

        updated_results.append(
            item
        )

    results = list(
        ranking_map.values()
    )

    results.sort(
        key=lambda item: item.get(
            "score",
            0,
        ),
        reverse=True,
    )

    regular_batch_names = [
        name
        for name, _ in regular_batch
    ]

    cache_data = {
        "ranking": results,
        "scan_state": {
            "total_watchlist":
                total_watchlist,
            "batch_size":
                batch_size,
            "cursor_start":
                cursor_start,
            "next_cursor":
                next_cursor,
            "regular_scanned":
                len(
                    regular_batch
                ),
            "total_scanned":
                len(
                    selected
                ),
            "cycle_completed":
                cycle_completed,
            "regular_batch_stocks":
                regular_batch_names,
        },
    }

    temp_file = (
        CACHE_FILE.with_suffix(
            CACHE_FILE.suffix
            + ".tmp"
        )
    )

    with temp_file.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            cache_data,
            handle,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )

        handle.flush()
        os.fsync(
            handle.fileno()
        )

    temp_file.replace(
        CACHE_FILE
    )

    return {
        "status": "ok",
        "stocks": len(
            results
        ),
        "scanned": len(
            selected
        ),
        "regular_scanned": len(
            regular_batch
        ),
        "errors": sum(
            1
            for item in results
            if "error" in item
        ),
        "next_cursor":
            next_cursor,
        "cycle_completed":
            cycle_completed,
    }
