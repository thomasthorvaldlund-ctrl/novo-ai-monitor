from portfolio import (
    load_portfolio_rows,
    update_portfolio_position,
)

TEST_FILE = "portfolio_test.csv"

print("Før:", load_portfolio_rows(TEST_FILE))

update_portfolio_position(
    original_ticker="NVDA",
    stock="NVIDIA",
    ticker="NVDA",
    qty=6,
    buy_price=190,
    cost_dkk=6500,
    portfolio_file=TEST_FILE,
)

print("Efter redigering:", load_portfolio_rows(TEST_FILE))
