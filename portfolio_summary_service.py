from portfolio import get_portfolio_summary as get_real_portfolio_summary


def get_portfolio_summary():
    data = get_real_portfolio_summary()

    total_value = data.get("total_value", 0)
    total_profit = data.get("total_profit", 0)
    total_profit_pct = data.get("total_profit_pct", 0)
    positions = data.get("positions", [])

    return {
        "value": f"{total_value:,.2f} DKK",
        "daily_change": f"{total_profit:,.2f} DKK",
        "total_return": f"{total_profit_pct:.2f}%",
        "positions": len(positions)
    }