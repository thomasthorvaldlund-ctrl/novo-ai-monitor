import json

from market_score_service import get_market_score
from market_summary_service import get_market_summary
from ai_alerts_service import get_ai_alerts
from portfolio_summary_service import get_portfolio_summary
from system_health_service import get_system_health

from dashboard_cache_service import save_dashboard_cache


def build_dashboard_cache():

    data = {
        "market": get_market_score(),
        "summary": get_market_summary(),
        "alerts": get_ai_alerts(),
        "portfolio": get_portfolio_summary(),
        "system_health": get_system_health(),
    }

    save_dashboard_cache(data)

    return data


if __name__ == "__main__":
    build_dashboard_cache()
    print("Dashboard cache updated.")