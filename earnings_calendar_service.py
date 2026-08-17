import fcntl
import json
import os
import tempfile
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo

import yfinance as yf


BASE_DIR = Path(__file__).resolve().parent

CACHE_FILE = BASE_DIR / "earnings_calendar_cache.json"
LOCK_FILE = BASE_DIR / "earnings_calendar_cache.lock"

CACHE_VERSION = 2
CACHE_TTL = timedelta(hours=12)
MARKET_TIMEZONE = ZoneInfo("Europe/Copenhagen")

DEEP_AI_CANDIDATE_LIMIT = 30
DEEP_AI_DISPLAY_LIMIT = 20


OFFICIAL_OVERRIDES = {
    "VWS.CO": {
        "company": "Vestas",
        "fallback_date": "2026-11-11",
        "calendar_url": (
            "https://www.vestas.com/"
            "en/investor/Calendar-Events"
        ),
    },
    "MAERSK-B.CO": {
        "company": "A.P. Møller - Mærsk",
        "fallback_date": "2026-11-05",
        "calendar_url": (
            "https://investor.maersk.com/"
            "events-and-presentations/events"
        ),
    },
    "ASML.AS": {
        "company": "ASML",
        "fallback_date": "2026-10-14",
        "calendar_url": (
            "https://www.asml.com/"
            "investors/financial-calendar"
        ),
    },
    "DSV.CO": {
        "company": "DSV",
        "fallback_date": "2026-10-21",
        "calendar_url": (
            "https://investor.dsv.com/calendar"
        ),
    },
    "NVDA": {
        "company": "NVIDIA",
        "fallback_date": "2026-08-26",
        "calendar_url": (
            "https://investor.nvidia.com/"
            "home/default.aspx"
        ),
    },
    "NOVO-B.CO": {
        "company": "Novo Nordisk",
        "fallback_date": "2026-11-04",
        "calendar_url": (
            "https://www.novonordisk.com/"
            "investors/financial-calendar.html"
        ),
    },
    "GMAB.CO": {
        "company": "Genmab",
        "fallback_date": "2026-11-05",
        "calendar_url": (
            "https://ir.genmab.com/"
            "financial-calendar/"
        ),
    },
    "PNDORA.CO": {
        "company": "Pandora",
        "fallback_date": "2026-11-04",
        "calendar_url": (
            "https://pandoragroup.com/"
            "investor/financial-calendar"
        ),
    },
}


def _utc_now():
    return datetime.now(timezone.utc)


def _market_today():
    return datetime.now(
        MARKET_TIMEZONE
    ).date()


def _parse_date(value):
    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    try:
        return date.fromisoformat(
            text[:10]
        )
    except ValueError:
        return None


def _parse_datetime(value):
    if not isinstance(value, str):
        return None

    try:
        parsed = datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00",
            )
        )
    except ValueError:
        return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(
            tzinfo=timezone.utc
        )

    return parsed.astimezone(
        timezone.utc
    )


def _format_checked_at(value):
    parsed = _parse_datetime(
        value
    )

    if parsed is None:
        return None

    return parsed.astimezone(
        MARKET_TIMEZONE
    ).strftime(
        "%d.%m.%Y kl. %H:%M"
    )


def _normalise_values(values):
    if not values:
        return set()

    return {
        str(value).strip().upper()
        for value in values
        if str(value).strip()
    }


def _build_company_config(
    item,
    position,
    in_portfolio,
):
    stock = str(
        item.get(
            "stock",
            "",
        )
    ).strip()

    ticker = str(
        item.get(
            "ticker",
            "",
        )
    ).strip()

    ticker_key = ticker.upper()

    override = OFFICIAL_OVERRIDES.get(
        ticker_key,
        {},
    )

    official_url = override.get(
        "calendar_url"
    )

    if official_url:
        calendar_url = official_url
        is_official_link = True
        link_label = (
            "Åbn officiel finanskalender"
        )
    else:
        calendar_url = (
            "https://finance.yahoo.com/"
            f"quote/{quote(ticker, safe='')}/"
        )
        is_official_link = False
        link_label = (
            "Åbn regnskabsoversigt"
        )

    return {
        "stock": stock,
        "company": override.get(
            "company",
            stock,
        ),
        "ticker": ticker,
        "ticker_key": ticker_key,
        "deep_ai_rank": position,
        "is_deep_ai_candidate": (
            position
            <= DEEP_AI_CANDIDATE_LIMIT
        ),
        "in_portfolio": in_portfolio,
        "fallback_date": override.get(
            "fallback_date"
        ),
        "calendar_url": calendar_url,
        "is_official_link": (
            is_official_link
        ),
        "link_label": link_label,
    }


def _select_companies(
    ranking,
    portfolio_names=None,
    portfolio_tickers=None,
):
    if not isinstance(ranking, list):
        return []

    portfolio_names = _normalise_values(
        portfolio_names
    )

    portfolio_tickers = _normalise_values(
        portfolio_tickers
    )

    selected = {}

    for position, item in enumerate(
        ranking,
        start=1,
    ):
        if not isinstance(item, dict):
            continue

        stock = str(
            item.get(
                "stock",
                "",
            )
        ).strip()

        ticker = str(
            item.get(
                "ticker",
                "",
            )
        ).strip()

        if not stock or not ticker:
            continue

        ticker_key = ticker.upper()

        in_portfolio = (
            stock.upper()
            in portfolio_names
            or ticker_key
            in portfolio_tickers
        )

        is_candidate = (
            position
            <= DEEP_AI_CANDIDATE_LIMIT
        )

        if (
            not is_candidate
            and not in_portfolio
        ):
            continue

        existing = selected.get(
            ticker_key
        )

        if existing is not None:
            existing["in_portfolio"] = (
                existing["in_portfolio"]
                or in_portfolio
            )
            continue

        selected[ticker_key] = (
            _build_company_config(
                item,
                position,
                in_portfolio,
            )
        )

    return list(
        selected.values()
    )


def _load_cache():
    if not CACHE_FILE.exists():
        return {}

    try:
        with CACHE_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)
    except (
        OSError,
        json.JSONDecodeError,
    ):
        return {}

    if not isinstance(data, dict):
        return {}

    if data.get("version") != CACHE_VERSION:
        return {}

    if not isinstance(
        data.get("events"),
        dict,
    ):
        return {}

    return data


def _cache_is_fresh(
    cache,
    now,
):
    checked_at = _parse_datetime(
        cache.get("checked_at")
    )

    if checked_at is None:
        return False

    age = now - checked_at

    return (
        timedelta(0)
        <= age
        < CACHE_TTL
    )


def _cache_covers(
    cache,
    companies,
):
    events = cache.get(
        "events",
        {},
    )

    if not isinstance(events, dict):
        return False

    requested = {
        item["ticker_key"]
        for item in companies
    }

    return requested.issubset(
        events
    )


def _extract_next_date(
    calendar,
    today,
):
    if not isinstance(calendar, dict):
        return None

    raw_dates = calendar.get(
        "Earnings Date"
    )

    if raw_dates is None:
        return None

    if not isinstance(
        raw_dates,
        (list, tuple, set),
    ):
        raw_dates = [raw_dates]

    dates = sorted(
        parsed
        for parsed in (
            _parse_date(value)
            for value in raw_dates
        )
        if parsed is not None
        and parsed >= today
    )

    return dates[0] if dates else None


def _fallback_event(
    config,
    previous_events,
    today,
):
    previous = previous_events.get(
        config["ticker_key"],
        {},
    )

    if isinstance(previous, dict):
        previous_date = _parse_date(
            previous.get("date")
        )

        if (
            previous_date is not None
            and previous_date >= today
        ):
            return {
                "date": previous_date.isoformat(),
                "source": previous.get(
                    "source",
                    "cache",
                ),
                "status": "cached",
            }

    fallback_date = _parse_date(
        config.get("fallback_date")
    )

    if (
        fallback_date is not None
        and fallback_date >= today
    ):
        return {
            "date": fallback_date.isoformat(),
            "source": "official_fallback",
            "status": "fallback",
        }

    return {
        "date": None,
        "source": "unavailable",
        "status": "unavailable",
    }


def _refresh_cache(
    previous_cache,
    now,
    today,
    companies,
):
    previous_events = (
        previous_cache.get(
            "events",
            {},
        )
        if isinstance(
            previous_cache,
            dict,
        )
        else {}
    )

    events = {}
    errors = {}

    for config in companies:
        ticker_key = config["ticker_key"]

        try:
            calendar = yf.Ticker(
                config["ticker"]
            ).calendar

            next_date = _extract_next_date(
                calendar,
                today,
            )
        except Exception as error:
            next_date = None
            errors[ticker_key] = (
                f"{type(error).__name__}: "
                f"{str(error)[:200]}"
            )

        if next_date is not None:
            events[ticker_key] = {
                "date": next_date.isoformat(),
                "source": "yfinance",
                "status": "live",
            }
            continue

        events[ticker_key] = (
            _fallback_event(
                config,
                previous_events,
                today,
            )
        )

        if ticker_key not in errors:
            errors[ticker_key] = (
                "Ingen fremtidig dato "
                "returneret."
            )

    return {
        "version": CACHE_VERSION,
        "checked_at": now.isoformat(
            timespec="seconds"
        ),
        "events": events,
        "errors": errors,
    }


def _write_cache(cache):
    file_descriptor, temporary_name = (
        tempfile.mkstemp(
            prefix=(
                f".{CACHE_FILE.name}."
            ),
            suffix=".tmp",
            dir=str(
                CACHE_FILE.parent
            ),
        )
    )

    temporary_path = Path(
        temporary_name
    )

    try:
        os.fchmod(
            file_descriptor,
            0o600,
        )

        with os.fdopen(
            file_descriptor,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                cache,
                file,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            file.write("\n")
            file.flush()
            os.fsync(
                file.fileno()
            )

        os.replace(
            temporary_path,
            CACHE_FILE,
        )

        os.chmod(
            CACHE_FILE,
            0o600,
        )
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


@contextmanager
def _calendar_lock():
    file_descriptor = os.open(
        LOCK_FILE,
        os.O_CREAT | os.O_RDWR,
        0o600,
    )

    try:
        os.fchmod(
            file_descriptor,
            0o600,
        )

        with os.fdopen(
            file_descriptor,
            "r+",
            encoding="utf-8",
        ) as lock_file:
            fcntl.flock(
                lock_file.fileno(),
                fcntl.LOCK_EX,
            )

            try:
                yield
            finally:
                fcntl.flock(
                    lock_file.fileno(),
                    fcntl.LOCK_UN,
                )
    except Exception:
        try:
            os.close(
                file_descriptor
            )
        except OSError:
            pass

        raise


def get_upcoming_earnings(
    ranking,
    portfolio_names=None,
    portfolio_tickers=None,
    force_refresh=False,
):
    """
    Returnerer Top 20 Deep AI-regnskaber
    med gyldig dato samt alle gyldige
    regnskaber for porteføljeaktier.

    Højst Top 30 plus porteføljeaktier
    kontrolleres via Yahoo Finance.
    """

    companies = _select_companies(
        ranking,
        portfolio_names,
        portfolio_tickers,
    )

    if not companies:
        return []

    now = _utc_now()
    today = _market_today()

    with _calendar_lock():
        cache = _load_cache()

        if (
            force_refresh
            or not _cache_is_fresh(
                cache,
                now,
            )
            or not _cache_covers(
                cache,
                companies,
            )
        ):
            cache = _refresh_cache(
                cache,
                now,
                today,
                companies,
            )

            _write_cache(
                cache
            )

    checked_at = cache.get(
        "checked_at"
    )

    checked_at_display = (
        _format_checked_at(
            checked_at
        )
    )

    events = cache.get(
        "events",
        {},
    )

    valid = []

    for config in companies:
        event = events.get(
            config["ticker_key"],
            {},
        )

        if not isinstance(event, dict):
            continue

        report_date = _parse_date(
            event.get("date")
        )

        if (
            report_date is None
            or report_date < today
        ):
            continue

        source = event.get(
            "source"
        )

        if source == "yfinance":
            date_source = "Yahoo Finance"
        elif source == "official_fallback":
            date_source = (
                "Officiel fallback"
            )
        else:
            date_source = "Cache"

        valid.append({
            "stock": config["stock"],
            "company": config["company"],
            "ticker": config["ticker"],
            "ticker_key": (
                config["ticker_key"]
            ),
            "date": report_date.isoformat(),
            "date_display": (
                report_date.strftime(
                    "%d.%m.%Y"
                )
            ),
            "days_left": (
                report_date - today
            ).days,
            "calendar_url": (
                config["calendar_url"]
            ),
            "is_official_link": (
                config["is_official_link"]
            ),
            "link_label": (
                config["link_label"]
            ),
            "calendar_checked_at": (
                checked_at
            ),
            "calendar_checked_at_display": (
                checked_at_display
            ),
            "date_source": date_source,
            "data_status": event.get(
                "status",
                "unknown",
            ),
            "deep_ai_rank": (
                config["deep_ai_rank"]
            ),
            "is_deep_ai_candidate": (
                config[
                    "is_deep_ai_candidate"
                ]
            ),
            "in_portfolio": (
                config["in_portfolio"]
            ),
        })

    deep_ai_results = sorted(
        (
            item
            for item in valid
            if item[
                "is_deep_ai_candidate"
            ]
        ),
        key=lambda item: (
            item["deep_ai_rank"],
            item["stock"],
        ),
    )[:DEEP_AI_DISPLAY_LIMIT]

    portfolio_results = [
        item
        for item in valid
        if item["in_portfolio"]
    ]

    deep_ai_tickers = {
        item["ticker_key"]
        for item in deep_ai_results
    }

    displayed = {}

    for item in (
        deep_ai_results
        + portfolio_results
    ):
        displayed[
            item["ticker_key"]
        ] = item

    results = list(
        displayed.values()
    )

    for item in results:
        item["is_deep_ai_top_20"] = (
            item["ticker_key"]
            in deep_ai_tickers
        )

    return sorted(
        results,
        key=lambda item: (
            item["days_left"],
            not item["in_portfolio"],
            item["stock"],
        ),
    )
