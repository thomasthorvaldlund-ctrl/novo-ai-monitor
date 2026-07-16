import csv
from stock_utils import get_history
from currency import get_fx_rates, get_currency, convert_to_dkk


PORTFOLIO_FILE = "/root/novo-ai-monitor/portfolio.csv"


def load_portfolio_rows(portfolio_file=PORTFOLIO_FILE):
    positions = []

    with open(portfolio_file, "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            positions.append({
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
        latest = float(data["Close"].iloc[-1])

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
