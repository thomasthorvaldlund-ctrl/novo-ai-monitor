from portfolio_summary_service import get_portfolio_summary
from portfolio_health_service import get_portfolio_health
from portfolio_health_history_service import save_portfolio_health_snapshot


if __name__ == "__main__":
    summary = get_portfolio_summary()
    health = get_portfolio_health(summary)
    result = save_portfolio_health_snapshot(health)
    print(result)
