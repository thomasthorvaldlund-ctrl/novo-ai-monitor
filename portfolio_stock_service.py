from portfolio import load_portfolio_rows


def get_monitored_stocks():
    """
    Returnerer unikke tickers fra brugerens portefølje.
    """

    rows = load_portfolio_rows()

    tickers = []

    for row in rows:
        ticker = row.get("ticker")

        if ticker:
            ticker = ticker.strip().upper()

            if ticker not in tickers:
                tickers.append(ticker)

    return tickers


def get_monitored_stock_names():
    """
    Returnerer unikke aktienavne fra brugerens portefølje.
    """

    rows = load_portfolio_rows()

    stocks = []

    for row in rows:
        stock = row.get("stock")

        if stock:
            stock = stock.strip().upper()

            if stock not in stocks:
                stocks.append(stock)

    return stocks


def get_monitored_stock_map():
    """
    Returnerer mapping mellem aktienavn og ticker.
    """

    rows = load_portfolio_rows()

    stocks = {}

    for row in rows:
        stock = row.get("stock")
        ticker = row.get("ticker")

        if stock and ticker:
            stock = stock.strip().upper()
            ticker = ticker.strip().upper()

            stocks[stock] = ticker

    return stocks



def _normalise_identifier(value):
    return str(value or "").strip().upper()


def _identifier_variants(
    stock=None,
    ticker=None,
):
    """
    Returnerer sikre navne- og tickeraliasser.

    Eksempel:
    DSV A/S + DSV.CO giver også DSV.
    """
    stock_identifier = (
        _normalise_identifier(stock)
    )
    ticker_identifier = (
        _normalise_identifier(ticker)
    )

    variants = {
        value
        for value in (
            stock_identifier,
            ticker_identifier,
        )
        if value
    }

    if "." in ticker_identifier:
        symbol, exchange = (
            ticker_identifier.rsplit(
                ".",
                1,
            )
        )

        if symbol:
            variants.add(symbol)

        for separator in ("_", "."):
            suffix = (
                f"{separator}{exchange}"
            )

            if (
                stock_identifier.endswith(
                    suffix
                )
                and len(stock_identifier)
                > len(suffix)
            ):
                variants.add(
                    stock_identifier[
                        :-len(suffix)
                    ]
                )

    return variants


def get_monitored_identifiers():
    """
    Returnerer navne, tickers og kendte
    univers-aliasser for aktuelle positioner.
    """
    rows = load_portfolio_rows()

    names = {
        _normalise_identifier(
            row.get("stock")
        )
        for row in rows
        if _normalise_identifier(
            row.get("stock")
        )
    }

    tickers = {
        _normalise_identifier(
            row.get("ticker")
        )
        for row in rows
        if _normalise_identifier(
            row.get("ticker")
        )
    }

    aliases = set()

    for row in rows:
        aliases.update(
            _identifier_variants(
                stock=row.get("stock"),
                ticker=row.get("ticker"),
            )
        )

    try:
        from stock_universe_service import (
            get_active_stocks,
        )

        for name, ticker in (
            get_active_stocks().items()
        ):
            if (
                _normalise_identifier(
                    ticker
                )
                in tickers
            ):
                aliases.update(
                    _identifier_variants(
                        stock=name,
                        ticker=ticker,
                    )
                )
    except Exception:
        # Filtreringen fejler sikkert lukket:
        # eksakte navne/tickers virker fortsat.
        pass

    return {
        "names": names,
        "tickers": tickers,
        "aliases": aliases,
    }


def is_monitored_stock(
    stock=None,
    ticker=None,
):
    """
    True kun når aktien findes i den
    aktuelle portfolio.csv.
    """
    identifiers = (
        get_monitored_identifiers()
    )

    candidates = {
        _normalise_identifier(stock),
        _normalise_identifier(ticker),
    }
    candidates.discard("")

    allowed = (
        identifiers["names"]
        | identifiers["tickers"]
        | identifiers["aliases"]
    )

    return bool(candidates & allowed)
