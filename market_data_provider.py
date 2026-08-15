"""
Aureum AI Market Data Provider

Denne fil er det centrale adgangslag til markedsdata.

I første version bruges Yahoo Finance som datakilde.
Senere kan Yahoo udskiftes med f.eks. EODHD eller Finnhub,
uden at resten af platformen skal ændres.
"""

from datetime import datetime
import os
import pandas as pd

from yahoo_provider import (
    get_history as yahoo_get_history,
    get_metadata as yahoo_get_metadata,
)
from eodhd_provider import (
    get_history as eodhd_get_history,
    get_metadata as eodhd_get_metadata,
)


# Aktiv datakilde.
# Skift senere til "eodhd", når EODHD-integrationen er implementeret.
DATA_PROVIDER = os.getenv(
    "MARKET_DATA_PROVIDER",
    "yahoo",
).strip().lower()

PROVIDER_NAMES = {
    "yahoo": "Yahoo Finance",
    "eodhd": "EODHD",
}


METADATA_FIELDS = (
    "sector",
    "industry",
    "country",
    "exchange",
    "full_exchange",
    "currency",
    "quote_type",
    "long_name",
)


def _metadata_contract(data):
    """
    Håndhæver Aureums provider-neutrale metadataformat.
    """
    if data is None:
        data = {}

    if not isinstance(
        data,
        dict,
    ):
        raise TypeError(
            "Market Data Provider metadata skal være et dict."
        )

    return {
        field:
            data.get(field)
        for field
        in METADATA_FIELDS
    }

HISTORY_REQUIRED_COLUMNS = (
    "Close",
)

HISTORY_OPTIONAL_COLUMNS = (
    "Open",
    "High",
    "Low",
    "Adj Close",
    "Volume",
)

HISTORY_COLUMNS = (
    "Open",
    "High",
    "Low",
    "Close",
    "Adj Close",
    "Volume",
)

HISTORY_COLUMN_ALIASES = {
    "open": "Open",
    "high": "High",
    "low": "Low",
    "close": "Close",
    "adjclose": "Adj Close",
    "adjustedclose": "Adj Close",
    "volume": "Volume",
}

HISTORY_TIME_COLUMNS = (
    "Datetime",
    "Date",
    "Timestamp",
    "datetime",
    "date",
    "timestamp",
)


def _history_column_key(value):
    return "".join(
        character
        for character
        in str(value).strip().casefold()
        if character.isalnum()
    )


def _history_contract(data):
    """
    Håndhæver Aureums provider-neutrale history-format.

    Minimum:
    - pandas DataFrame
    - numerisk Close-kolonne
    - kronologisk DatetimeIndex

    Open, High, Low, Adj Close og Volume er valgfrie.
    Provider-specifikke kolonner fjernes.
    """
    if data is None:
        data = pd.DataFrame()

    if not isinstance(
        data,
        pd.DataFrame,
    ):
        raise TypeError(
            "Market Data Provider history skal være en pandas DataFrame."
        )

    result = data.copy()

    existing_columns = set(
        result.columns
    )

    rename = {}

    for column in result.columns:

        target = HISTORY_COLUMN_ALIASES.get(
            _history_column_key(
                column
            )
        )

        if (
            target
            and column != target
            and target not in existing_columns
        ):
            rename[
                column
            ] = target

    if rename:
        result = result.rename(
            columns=rename
        )

    if not isinstance(
        result.index,
        pd.DatetimeIndex,
    ):
        time_column = next(
            (
                column
                for column
                in HISTORY_TIME_COLUMNS
                if column in result.columns
            ),
            None,
        )

        if time_column is not None:
            timestamps = pd.to_datetime(
                result[
                    time_column
                ],
                errors="coerce",
            )

            if (
                not result.empty
                and timestamps.isna().any()
            ):
                raise ValueError(
                    "History indeholder ugyldige timestamps."
                )

            result = result.drop(
                columns=[
                    time_column
                ]
            )

            result.index = pd.DatetimeIndex(
                timestamps,
                name=time_column,
            )

        elif result.empty:
            result.index = pd.DatetimeIndex(
                [],
                name=result.index.name,
            )

        else:
            index_dtype = result.index.dtype

            index_is_datetime_candidate = (
                pd.api.types.is_object_dtype(
                    index_dtype
                )
                or pd.api.types.is_string_dtype(
                    index_dtype
                )
            )

            if not index_is_datetime_candidate:
                raise ValueError(
                    "History mangler datetime-index "
                    "eller dato/timestamp-kolonne."
                )

            timestamps = pd.to_datetime(
                result.index,
                errors="coerce",
            )

            if pd.isna(
                timestamps
            ).any():
                raise ValueError(
                    "History index kan ikke konverteres til datetime."
                )

            result.index = pd.DatetimeIndex(
                timestamps,
                name=result.index.name,
            )

    if result.index.hasnans:
        raise ValueError(
            "History indeholder ugyldige datetime-værdier."
        )

    if (
        "Close"
        not in result.columns
    ):
        if result.empty:
            result[
                "Close"
            ] = pd.Series(
                index=result.index,
                dtype="float64",
            )

        else:
            raise ValueError(
                "History mangler obligatorisk Close-kolonne."
            )

    for column in HISTORY_COLUMNS:

        if column not in result.columns:
            continue

        original_values = result[
            column
        ]

        numeric_values = pd.to_numeric(
            original_values,
            errors="coerce",
        )

        invalid = (
            original_values.notna()
            & numeric_values.isna()
        )

        if invalid.any():
            raise ValueError(
                f"History-kolonnen {column} "
                "indeholder ikke-numeriske værdier."
            )

        result[
            column
        ] = numeric_values

    canonical_columns = [
        column
        for column
        in HISTORY_COLUMNS
        if column in result.columns
    ]

    result = result.loc[
        :,
        canonical_columns,
    ]

    result = result.sort_index()

    return result




def get_provider_name():
    return PROVIDER_NAMES.get(
        DATA_PROVIDER,
        DATA_PROVIDER,
    )


def get_ticker(symbol: str):
    """
    Oversætter interne symboler til markeds-tickers.
    """

    mapping = {
        "NOVO": "NOVO-B.CO",
        "DSV": "DSV.CO",
    }

    return mapping.get(symbol.upper(), symbol)


def get_history(symbol, period="1mo", interval=None):
    """
    Returnerer historiske kursdata fra den aktive datakilde
    i Aureums provider-neutrale history-format.
    """
    ticker = get_ticker(symbol)

    if DATA_PROVIDER == "yahoo":
        data = yahoo_get_history(
            ticker,
            period=period,
            interval=interval,
        )

    elif DATA_PROVIDER == "eodhd":
        data = eodhd_get_history(
            ticker,
            period=period,
            interval=interval,
        )

    else:
        raise RuntimeError(
            f"Ukendt Market Data Provider: {DATA_PROVIDER}"
        )

    return _history_contract(
        data
    )


def get_metadata(symbol):
    """
    Returnerer selskabsmetadata fra den aktive datakilde
    i Aureums provider-neutrale metadataformat.
    """
    ticker = get_ticker(symbol)

    if DATA_PROVIDER == "yahoo":
        data = yahoo_get_metadata(
            ticker
        )

    elif DATA_PROVIDER == "eodhd":
        data = eodhd_get_metadata(
            ticker
        )

    else:
        raise RuntimeError(
            f"Ukendt Market Data Provider: {DATA_PROVIDER}"
        )

    return _metadata_contract(
        data
    )


def get_latest_price(symbol):
    """
    Returnerer seneste lukkekurs.
    """

    history = get_history(symbol, period="5d")

    if history.empty:
        return None

    return float(history["Close"].iloc[-1])


def get_latest_timestamp(symbol):
    """
    Returnerer tidspunktet for seneste datapunkt.
    """

    history = get_history(
        symbol,
        period="1d",
        interval="1m",
    )

    if history.empty:
        return None

    return history.index[-1].to_pydatetime()


if __name__ == "__main__":

    print("Provider:", get_provider_name())
    print("NOVO:", get_latest_price("NOVO"))
    print("Tid :", get_latest_timestamp("NOVO"))
