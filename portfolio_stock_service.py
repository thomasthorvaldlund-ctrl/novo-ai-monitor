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
