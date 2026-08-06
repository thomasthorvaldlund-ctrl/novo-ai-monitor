import csv
from stock_utils import get_history
from currency import get_fx_rates, get_currency, convert_to_dkk


PORTFOLIO_FILE = "/root/aureum-ai-platform/portfolio.csv"


def load_portfolio_rows(portfolio_file=PORTFOLIO_FILE):
    positions = []

    with open(portfolio_file, "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            positions.append({
                "id": int(row["id"]) if row.get("id") else None,
                "stock": row["stock"],
                "ticker": row["ticker"],
                "qty": float(row["qty"]),
                "buy_price": float(row["buy_price"]),
                "cost_dkk": (
                    float(row["cost_dkk"])
                    if row.get("cost_dkk")
                    else None
                ),
            })

    return positions


def get_portfolio_positions(portfolio_file=PORTFOLIO_FILE):
    fx_rates = get_fx_rates()
    positions = []

    for row in load_portfolio_rows(portfolio_file):
        ticker = row["ticker"]
        currency = get_currency(ticker)

        data = get_history(ticker, period="10d")

        valid_prices = data["Close"].dropna()

        if valid_prices.empty:
            continue

        latest = float(valid_prices.iloc[-1])

        latest_dkk = convert_to_dkk(latest, currency, fx_rates)
        buy_price_dkk = convert_to_dkk(row["buy_price"], currency, fx_rates)

        value_dkk = latest_dkk * row["qty"]

        if row.get("cost_dkk") is not None:
            cost_dkk = row["cost_dkk"]
        else:
            cost_dkk = buy_price_dkk * row["qty"]
        profit_dkk = value_dkk - cost_dkk
        profit_pct = (profit_dkk / cost_dkk) * 100 if cost_dkk else 0

        positions.append({
            **row,
            "currency": currency,
            "latest": latest,
            "latest_dkk": latest_dkk,
            "buy_price_dkk": buy_price_dkk,
            "value_dkk": value_dkk,
            "cost_dkk": cost_dkk,
            "profit_dkk": profit_dkk,
            "profit_pct": profit_pct,
        })

    total_value = sum(p["value_dkk"] for p in positions)

    for p in positions:
        p["weight_pct"] = (p["value_dkk"] / total_value) * 100 if total_value else 0

    return positions


def get_portfolio_summary(portfolio_file=PORTFOLIO_FILE):
    positions = get_portfolio_positions(portfolio_file)

    total_value = sum(p["value_dkk"] for p in positions)
    total_cost = sum(p["cost_dkk"] for p in positions)
    total_profit = total_value - total_cost
    total_profit_pct = (total_profit / total_cost) * 100 if total_cost else 0

    return {
        "positions": positions,
        "total_value": total_value,
        "total_cost": total_cost,
        "total_profit": total_profit,
        "total_profit_pct": total_profit_pct,
    }


def save_portfolio_rows(positions, portfolio_file=PORTFOLIO_FILE):
    fieldnames = ["id", "stock", "ticker", "qty", "buy_price", "cost_dkk"]

    with open(portfolio_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for position in positions:
            writer.writerow({
                "id": position.get("id"),
                "stock": position["stock"],
                "ticker": position["ticker"],
                "qty": position["qty"],
                "buy_price": position["buy_price"],
                "cost_dkk": (
                    position.get("cost_dkk")
                    if position.get("cost_dkk") is not None
                    else ""
                ),
            })


def add_portfolio_position(
    stock,
    ticker,
    qty,
    buy_price,
    cost_dkk=None,
    portfolio_file=PORTFOLIO_FILE,
):
    positions = load_portfolio_rows(portfolio_file)

    stock = stock.strip().upper()
    ticker = ticker.strip().upper()

    if not stock or not ticker:
        raise ValueError("Aktie og ticker skal udfyldes")

    next_id = max(
        [p.get("id", 0) or 0 for p in positions],
        default=0
    ) + 1

    positions.append({
        "id": next_id,
        "stock": stock,
        "ticker": ticker,
        "qty": float(qty),
        "buy_price": float(buy_price),
        "cost_dkk": float(cost_dkk) if cost_dkk not in (None, "") else None,
    })

    save_portfolio_rows(positions, portfolio_file)


def update_portfolio_position(
    position_id,
    stock,
    ticker,
    qty,
    buy_price,
    cost_dkk=None,
    portfolio_file=PORTFOLIO_FILE,
):
    positions = load_portfolio_rows(portfolio_file)

    ticker = ticker.strip().upper()
    updated = False

    for position in positions:
        if str(position.get("id")) == str(position_id):
            position.update({
                "stock": stock.strip().upper(),
                "ticker": ticker,
                "qty": float(qty),
                "buy_price": float(buy_price),
                "cost_dkk": (
                    float(cost_dkk)
                    if cost_dkk not in (None, "")
                    else None
                ),
            })
            updated = True
            break

    if not updated:
        raise ValueError(f"Position {position_id} blev ikke fundet")

    save_portfolio_rows(positions, portfolio_file)


def delete_portfolio_position(position_id, portfolio_file=PORTFOLIO_FILE):
    positions = load_portfolio_rows(portfolio_file)

    filtered = [
        position
        for position in positions
        if str(position.get("id")) != str(position_id)
    ]

    if len(filtered) == len(positions):
        raise ValueError(f"Position {position_id} blev ikke fundet")

    save_portfolio_rows(filtered, portfolio_file)
