import time

from market_data_provider import get_history
from stock_universe_service import get_all_stocks


FX_CACHE_SECONDS = 1800

_FX_CACHE = {
    "timestamp": 0.0,
    "rates": None,
}


# Alle rater angiver:
#
#     1 enhed af valutaen = X DKK
#
# Fallbacks bruges kun, hvis market-data-provider
# midlertidigt ikke kan hente den aktuelle FX-rate.
_FX_RATE_SPECS = {
    "USD": (
        "FX:USD/DKK",
        6.95,
    ),
    "EUR": (
        "FX:EUR/DKK",
        7.46,
    ),
    "SEK": (
        "FX:SEK/DKK",
        0.66,
    ),
    "NOK": (
        "FX:NOK/DKK",
        0.64,
    ),
    "GBP": (
        "FX:GBP/DKK",
        8.65,
    ),
    "CHF": (
        "FX:CHF/DKK",
        7.95,
    ),
    "PLN": (
        "FX:PLN/DKK",
        1.73,
    ),
    "CZK": (
        "FX:CZK/DKK",
        0.30,
    ),
}


SUPPORTED_CURRENCIES = frozenset({
    "DKK",
    *tuple(_FX_RATE_SPECS),
    "GBp",
})


# Fallback bruges kun for tickers, som ikke findes
# i det canonical stock universe.
#
# London (.L) er bevidst ikke med, fordi Yahoo kan
# rapportere både GBP og GBp. London-valuta skal derfor
# komme fra canonical metadata.
_SUFFIX_CURRENCY_FALLBACK = {
    ".CO": "DKK",
    ".ST": "SEK",
    ".OL": "NOK",
    ".HE": "EUR",
    ".AS": "EUR",
    ".DE": "EUR",
    ".PA": "EUR",
    ".SW": "CHF",
    ".MI": "EUR",
    ".MC": "EUR",
    ".BR": "EUR",
    ".VI": "EUR",
    ".IR": "EUR",
    ".LS": "EUR",
    ".WA": "PLN",
    ".PR": "CZK",
}


def _normalize_currency(currency):
    value = str(
        currency or ""
    ).strip()

    if value == "GBp":
        return "GBp"

    return value.upper()


def _fetch_fx_rate(
    pair,
    fallback,
):
    try:
        data = get_history(
            pair,
            period="5d",
        )

        values = (
            data["Close"]
            .dropna()
        )

        if values.empty:
            raise ValueError(
                "FX-serien er tom."
            )

        rate = float(
            values.iloc[-1]
        )

        if rate <= 0:
            raise ValueError(
                "FX-rate skal være positiv."
            )

        return rate

    except Exception:
        return float(
            fallback
        )


def get_fx_rates(
    force_refresh=False,
):
    """
    Returnerer DKK-rate for alle understøttede valutaer.

    Resultatet caches i processen i 30 minutter, så flere
    services ikke gentager de samme FX-kald unødigt.
    """
    now = time.time()

    cached = _FX_CACHE.get(
        "rates"
    )

    timestamp = float(
        _FX_CACHE.get(
            "timestamp",
            0.0,
        )
        or 0.0
    )

    if (
        not force_refresh
        and isinstance(
            cached,
            dict,
        )
        and (
            now - timestamp
            < FX_CACHE_SECONDS
        )
    ):
        return cached.copy()

    rates = {
        "DKK": 1.0,
    }

    for (
        currency,
        (
            pair,
            fallback,
        ),
    ) in _FX_RATE_SPECS.items():

        rates[
            currency
        ] = _fetch_fx_rate(
            pair,
            fallback,
        )

    # Yahoo anvender GBp for britiske pence.
    #
    # 100 GBp = 1 GBP.
    rates["GBp"] = (
        rates["GBP"]
        / 100.0
    )

    _FX_CACHE[
        "timestamp"
    ] = now

    _FX_CACHE[
        "rates"
    ] = rates.copy()

    return rates.copy()


def _canonical_currency_map():
    """
    Bygger ticker -> currency fra det canonical stock universe.
    """
    result = {}

    for data in (
        get_all_stocks()
        .values()
    ):
        ticker = str(
            data.get(
                "ticker",
                "",
            )
        ).strip().upper()

        currency = (
            _normalize_currency(
                data.get(
                    "currency",
                    "",
                )
            )
        )

        if (
            ticker
            and currency
        ):
            result[
                ticker
            ] = currency

    return result


def get_currency(ticker):
    """
    Finder handelsvaluta for en ticker.

    Canonical stock metadata er source of truth.
    For ikke-canonical tickers bruges kun sikre,
    entydige suffix-fallbacks.
    """
    normalized_ticker = str(
        ticker or ""
    ).strip().upper()

    if not normalized_ticker:
        raise ValueError(
            "Ticker må ikke være tom."
        )

    canonical = (
        _canonical_currency_map()
    )

    currency = canonical.get(
        normalized_ticker
    )

    if currency:
        if (
            currency
            not in SUPPORTED_CURRENCIES
        ):
            raise ValueError(
                "Ikke-understøttet canonical valuta "
                f"for {normalized_ticker}: "
                f"{currency}"
            )

        return currency

    # Bare tickers uden exchange suffix behandles som
    # amerikanske tickers for bagudkompatibilitet.
    if "." not in normalized_ticker:
        return "USD"

    for (
        suffix,
        fallback_currency,
    ) in (
        _SUFFIX_CURRENCY_FALLBACK
        .items()
    ):
        if normalized_ticker.endswith(
            suffix
        ):
            return fallback_currency

    if normalized_ticker.endswith(
        ".L"
    ):
        raise ValueError(
            "London ticker findes ikke i canonical universe; "
            "GBP kontra GBp kan ikke afgøres sikkert: "
            f"{normalized_ticker}"
        )

    raise ValueError(
        "Kan ikke bestemme valuta sikkert for ticker: "
        f"{normalized_ticker}"
    )


def convert_to_dkk(
    price,
    currency,
    fx_rates=None,
):
    """
    Konverterer en pris til DKK.

    Ukendte valutaer giver fejl i stedet for stiltiende
    at blive behandlet som 1:1 DKK.
    """
    normalized_currency = (
        _normalize_currency(
            currency
        )
    )

    if fx_rates is None:
        fx_rates = get_fx_rates()

    if (
        normalized_currency
        not in fx_rates
    ):
        raise ValueError(
            "Mangler DKK FX-rate for valuta: "
            f"{normalized_currency}"
        )

    rate = float(
        fx_rates[
            normalized_currency
        ]
    )

    return (
        float(price)
        * rate
    )
