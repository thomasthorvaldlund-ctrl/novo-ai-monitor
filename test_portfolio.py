from pathlib import Path
from tempfile import TemporaryDirectory

from portfolio import (
    load_portfolio_rows,
    save_portfolio_rows,
    update_portfolio_position,
)


def run_test():
    with TemporaryDirectory(
        prefix="aureum-portfolio-test-"
    ) as temp_dir:
        test_file = (
            Path(temp_dir)
            / "portfolio.csv"
        )

        initial_positions = [
            {
                "id": 1,
                "stock": "NVIDIA",
                "ticker": "NVDA",
                "qty": 5,
                "buy_price": 193.1,
                "cost_dkk": 6432.0,
            }
        ]

        save_portfolio_rows(
            initial_positions,
            test_file,
        )

        before = load_portfolio_rows(
            test_file
        )

        assert len(before) == 1
        assert before[0]["id"] == 1
        assert before[0]["ticker"] == "NVDA"
        assert before[0]["qty"] == 5.0

        update_portfolio_position(
            position_id=1,
            stock="NVIDIA",
            ticker="NVDA",
            qty=6,
            buy_price=190,
            cost_dkk=6500,
            portfolio_file=test_file,
        )

        after = load_portfolio_rows(
            test_file
        )

        assert len(after) == 1

        position = after[0]

        assert position["id"] == 1
        assert position["stock"] == "NVIDIA"
        assert position["ticker"] == "NVDA"
        assert position["qty"] == 6.0
        assert position["buy_price"] == 190.0
        assert position["cost_dkk"] == 6500.0

        temp_file = test_file.with_suffix(
            test_file.suffix + ".tmp"
        )

        assert not temp_file.exists()

        print(
            "before_qty:",
            before[0]["qty"],
        )
        print(
            "after_qty:",
            position["qty"],
        )
        print(
            "after_buy_price:",
            position["buy_price"],
        )
        print(
            "after_cost_dkk:",
            position["cost_dkk"],
        )
        print(
            "atomic_temp_remaining:",
            temp_file.exists(),
        )

        temp_path = Path(temp_dir)

    assert not temp_path.exists()

    print(
        "temporary_directory_removed:",
        True,
    )
    print(
        "portfolio_update_test: OK"
    )


if __name__ == "__main__":
    run_test()
