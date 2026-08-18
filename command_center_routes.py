from flask import Blueprint, redirect, render_template, request

from dashboard_cache_service import load_dashboard_cache
from ai_portfolio_lab_context_service import build_portfolio_lab_context
from system_health_service import get_system_health
from market_score_service import get_market_score
from market_summary_service import get_market_summary
from top_picks_service import get_top_picks
from combined_score_service import combined_stock_score as service_combined_score
from openai_service import client
from ai_alerts_service import get_ai_alerts
from portfolio_summary_service import get_portfolio_summary
from portfolio_health_service import get_portfolio_health
from ai_analyst_service import get_ai_analyst
from morning_brief_service import get_morning_brief
from market_score_history_service import load_market_score_history
from ai_engine_status_service import get_ai_engine_status
from portfolio_rebalancing_simulator import generate_rebalancing_plan
from ai_portfolio_decision_service import load_portfolio_decisions
from ai_portfolio_change_service import get_portfolio_changes
from ai_portfolio_performance_service import get_portfolio_performance
from ai_portfolio_analytics_service import get_portfolio_analytics
from ai_learning_service import get_learning_report
from ai_learning_timeline_service import get_learning_timeline
from ai_confidence_calibration_service import get_confidence_calibration
from ai_learning_by_stock_service import get_learning_by_stock
from ai_signal_accuracy_service import get_signal_accuracy
from ai_improvement_advisor_service import get_improvement_advisor
from ai_learning_trends_service import get_learning_trends
from ai_insight_generator_service import get_ai_insight
from ai_pattern_detector_service import get_pattern_detection
from ai_prediction_engine_service import get_prediction_engine
from ai_decision_optimizer_service import get_decision_optimizer
from ai_learning_feedback_service import get_learning_feedback
from ai_context_engine_service import get_ai_context
from ai_strategy_engine_service import get_ai_strategy
from ai_copilot_engine_service import get_ai_copilot
from ai_copilot_decision_service import get_copilot_decision
from ai_decision_performance_service import get_decision_performance
from ai_portfolio_executive_service import get_ai_portfolio_executive
from ai_portfolio_overview_service import get_ai_portfolio_overview
from ai_portfolio_brain_service import get_ai_portfolio_brain
from ai_portfolio_brain_score_service import get_brain_score
from ai_portfolio_brain_score_explanation_service import get_brain_score_explanation
from ai_portfolio_confidence_calibration_service import get_confidence_calibration as get_portfolio_confidence_calibration
from ai_portfolio_decision_memory_service import get_decision_memory
from ai_portfolio_memory_trend_service import get_memory_trends
from ai_portfolio_memory_insight_service import get_memory_insights
from ai_portfolio_memory_advisor_service import get_memory_advisor
from ai_portfolio_memory_center_service import get_memory_center
from ai_portfolio_memory_intelligence_service import get_memory_intelligence
from ai_portfolio_memory_learning_service import get_memory_learning
from ai_portfolio_learning_evolution_service import get_learning_evolution
from ai_portfolio_learning_analytics_service import get_learning_analytics
from ai_confidence_intelligence_service import get_confidence_intelligence
from ai_stock_decision_intelligence_service import get_stock_decision_intelligence
from ai_data_quality_service import get_ai_data_quality
from market_dashboard_service import (
    get_market_dashboard_status,
    get_relevant_market_status,
    summarize_market_dashboard_status,
)
from market_intelligence_service import get_market_intelligence
from ai_decision_evolution_service import get_decision_evolution


command_center_bp = Blueprint("command_center", __name__)

@command_center_bp.route(
    "/command-center-v2",
    endpoint="command_center_v2",
)
def legacy_command_center_redirect():
    return redirect("/command-center")


@command_center_bp.route("/command-center")
def command_center():
    cache = load_dashboard_cache()
    updated_at = cache.get("updated_at", "Ukendt")

    system_health = cache.get("system_health", get_system_health())
    market = cache.get("market", get_market_score())
    market_data_status = cache.get("market_data_status", {})
    summary = cache.get("summary", get_market_summary())
    alerts = cache.get("alerts", get_ai_alerts())
    portfolio = cache.get("portfolio", get_portfolio_summary())
    portfolio_health = get_portfolio_health(portfolio)

    top_picks = cache.get("top_picks", [])
    analyst = cache.get("analyst", "AI Analyst er ikke tilgængelig endnu.")
    brief = cache.get("morning_brief", {})
    performance = cache.get("performance", {})
    ai_news = cache.get("ai_news", {})
    stock_explanations = cache.get("stock_explanations", [])
    portfolio_insights = cache.get("portfolio_insights", [])
    portfolio_recommendations = cache.get("portfolio_recommendations", [])
    rebalancing = cache.get("rebalancing", {})
    ai_rebalancing_plan = cache.get("ai_rebalancing_plan", {})
    rebalancing_amount = cache.get("rebalancing_amount", 5000)
    today_take = cache.get("today_take", {})
    earnings = cache.get("earnings", {})
    earnings_risks = cache.get("earnings_risks", [])
    executive_summary = cache.get("executive_summary", {})
    ai_copilot = cache.get("ai_copilot", {})
    decision_intelligence = cache.get("decision_intelligence", {})
    ai_copilot_timeline = cache.get("ai_copilot_timeline", [])
    ai_copilot_changes = cache.get("ai_copilot_changes", {})
    ai_risk_dashboard = cache.get("ai_risk_dashboard", {})
    decision_quality = cache.get("decision_quality", {})
    decision_learning = cache.get("decision_learning", {})
    decision_learning_trend = cache.get("decision_learning_trend", {})
    adaptive_behavior = cache.get("adaptive_behavior", {})
    adaptive_performance = cache.get("adaptive_performance", {})
    adaptive_explanation = cache.get("adaptive_explanation", {})
    ai_maturity = cache.get("ai_maturity", {})

    ai_maturity_trend = cache.get(
        "ai_maturity_trend",
        {}
    )

    ai_maturity_explanation = cache.get(
        "ai_maturity_explanation",
        {}
    )
    market_dashboard_status = get_relevant_market_status()
    market_overview_status = summarize_market_dashboard_status(
        market_dashboard_status
    )
    market_intelligence = get_market_intelligence()

    ai_engine_status = get_ai_engine_status()

    return render_template(
        "command_center.html",
        system_health=system_health,
        market=market,
        market_data_status=market_data_status,
        top_picks=top_picks,
        summary=summary,
        alerts=alerts,
        portfolio=portfolio,
        portfolio_health=portfolio_health,
        analyst=analyst,
        brief=brief,
        updated_at=updated_at,
        performance=performance,
        ai_news=ai_news,
        stock_explanations=stock_explanations,
        portfolio_insights=portfolio_insights,
        portfolio_recommendations=portfolio_recommendations,
        rebalancing=rebalancing,
        ai_rebalancing_plan=ai_rebalancing_plan,
        rebalancing_amount=rebalancing_amount,
        today_take=today_take,
        earnings=earnings,
        earnings_risks=earnings_risks,
        executive_summary=executive_summary,
        ai_copilot=ai_copilot,
        decision_intelligence=decision_intelligence,
        ai_copilot_timeline=ai_copilot_timeline,
        ai_copilot_changes=ai_copilot_changes,
        ai_risk_dashboard=ai_risk_dashboard,
        decision_quality=decision_quality,
        decision_learning=decision_learning,
        decision_learning_trend=decision_learning_trend,
          adaptive_behavior=adaptive_behavior,
          adaptive_performance=adaptive_performance,
          adaptive_explanation=adaptive_explanation,
          ai_maturity=ai_maturity,
        ai_maturity_trend=ai_maturity_trend,
        ai_maturity_explanation=ai_maturity_explanation,
        market_dashboard_status=market_dashboard_status,
        market_overview_status=market_overview_status,
        market_intelligence=market_intelligence,
        ai_engine_status=ai_engine_status,
        
    )

@command_center_bp.route("/market-score-history")
def market_score_history():
    return {
        "history": load_market_score_history()
    }    

@command_center_bp.route("/ai-stock-library")
def ai_stock_library():

    cache = load_dashboard_cache()

    cached_explanations = cache.get(
        "stock_explanations",
        [],
    )

    if not isinstance(
        cached_explanations,
        list,
    ):
        cached_explanations = []

    performance = cache.get(
        "performance",
        {},
    )

    if not isinstance(
        performance,
        dict,
    ):
        performance = {}

    selected_stock = request.args.get(
        "stock",
        "",
    ).strip().upper()

    selected_signal = request.args.get(
        "signal",
        "",
    ).strip().upper()

    selected_query = request.args.get(
        "q",
        "",
    ).strip()[:80]

    signal_names = (
        "BUY",
        "HOLD",
        "WATCH",
        "SELL",
    )

    signal_stocks = {}

    for signal in signal_names:
        values = performance.get(
            f"{signal.lower()}_stocks",
            [],
        )

        if not isinstance(values, list):
            values = []

        signal_stocks[signal] = {
            str(stock).strip().upper()
            for stock in values
            if str(stock).strip()
        }

    ranking = cache.get(
        "combined_ranking",
        [],
    )

    if not isinstance(ranking, list):
        ranking = []

    ticker_by_stock = {}

    for row in ranking:
        if not isinstance(row, dict):
            continue

        stock = str(
            row.get("stock", "")
        ).strip().upper()

        ticker = str(
            row.get("ticker", "")
        ).strip()

        if stock and ticker:
            ticker_by_stock[stock] = ticker

    all_explanations = []

    for cached_item in cached_explanations:
        if not isinstance(
            cached_item,
            dict,
        ):
            continue

        item = cached_item.copy()

        stock = str(
            item.get("stock", "")
        ).strip().upper()

        item["ticker"] = (
            ticker_by_stock.get(
                stock,
                "",
            )
        )

        item["signal"] = "UNKNOWN"

        for signal in signal_names:
            if stock in signal_stocks[signal]:
                item["signal"] = signal
                break

        all_explanations.append(item)

    actionable_explanations = [
        item
        for item in all_explanations
        if item.get("signal") in signal_names
    ]

    total_stock_count = len(
        all_explanations
    )

    signal_stock_count = len(
        actionable_explanations
    )

    signal_counts = {
        signal: len(signal_stocks[signal])
        for signal in signal_names
    }

    query_too_short = bool(
        selected_query
        and len(selected_query) < 2
    )

    search_total_count = 0
    results_truncated = False
    search_result_limit = 40

    if selected_stock:
        display_mode = "stock"

        stock_explanations = [
            item
            for item in all_explanations
            if str(
                item.get("stock", "")
            ).strip().upper()
            == selected_stock
        ]

        search_total_count = len(
            stock_explanations
        )

    elif selected_query:
        display_mode = "search"
        selected_signal = ""

        if query_too_short:
            stock_explanations = []
        else:
            normalized_query = (
                selected_query.casefold()
            )

            search_matches = []

            for item in all_explanations:
                searchable_text = " ".join(
                    str(
                        item.get(field, "")
                    )
                    for field in (
                        "stock",
                        "ticker",
                        "headline",
                        "summary",
                    )
                ).casefold()

                if (
                    normalized_query
                    in searchable_text
                ):
                    search_matches.append(
                        item
                    )

            search_total_count = len(
                search_matches
            )

            results_truncated = (
                search_total_count
                > search_result_limit
            )

            stock_explanations = (
                search_matches[
                    :search_result_limit
                ]
            )

    elif selected_signal in signal_stocks:
        display_mode = "signal"

        allowed_stocks = (
            signal_stocks[
                selected_signal
            ]
        )

        stock_explanations = [
            item
            for item in all_explanations
            if str(
                item.get("stock", "")
            ).strip().upper()
            in allowed_stocks
        ]

        search_total_count = len(
            stock_explanations
        )

    else:
        display_mode = "signals"
        selected_signal = ""

        stock_explanations = (
            actionable_explanations
        )

        search_total_count = len(
            stock_explanations
        )

    return render_template(
        "ai_stock_library.html",
        stock_explanations=(
            stock_explanations
        ),
        selected_stock=selected_stock,
        selected_signal=selected_signal,
        selected_query=selected_query,
        display_mode=display_mode,
        performance=performance,
        signal_counts=signal_counts,
        total_stock_count=(
            total_stock_count
        ),
        signal_stock_count=(
            signal_stock_count
        ),
        displayed_count=len(
            stock_explanations
        ),
        search_total_count=(
            search_total_count
        ),
        results_truncated=(
            results_truncated
        ),
        query_too_short=query_too_short,
    )


@command_center_bp.route("/ai-portfolio-lab")
def ai_portfolio_lab():
    cache = load_dashboard_cache()

    context = cache.get(
        "portfolio_lab_context"
    )

    if not isinstance(
        context,
        dict,
    ):
        context = (
            build_portfolio_lab_context(
                cache
            )
        )

    return render_template(
        "ai_portfolio_lab.html",
        **context,
    )


@command_center_bp.route("/simulate-rebalancing")
def simulate_rebalancing():

    amount = request.args.get(
        "amount",
        5000
    )

    try:
        amount = int(amount)
    except ValueError:
        amount = 5000

    plan = generate_rebalancing_plan(amount)

    cache = load_dashboard_cache()

    return render_template(
        "ai_rebalancing_simulator.html",
        system_health=cache.get("system_health", {}),
        market=cache.get("market", {}),
        top_picks=cache.get("top_picks", []),
        summary=cache.get("summary", {}),
        alerts=cache.get("alerts", []),
        portfolio=cache.get("portfolio", {}),
        analyst=cache.get("analyst", ""),
        brief=cache.get("morning_brief", {}),
        updated_at=cache.get("updated_at", ""),
        performance=cache.get("performance", {}),
        ai_news=cache.get("ai_news", {}),
        stock_explanations=cache.get("stock_explanations", []),
        portfolio_insights=cache.get("portfolio_insights", []),
        portfolio_recommendations=cache.get("portfolio_recommendations", []),
        rebalancing=cache.get("rebalancing", {}),
        ai_rebalancing_plan=plan,
        rebalancing_amount=amount,
        today_take=cache.get("today_take", {}),
        earnings=cache.get("earnings", {}),
        earnings_risks=cache.get("earnings_risks", []),
        executive_summary=cache.get("executive_summary", {}),
        ai_copilot=cache.get("ai_copilot", {}),
        ai_copilot_timeline=cache.get("ai_copilot_timeline", []),
        ai_copilot_changes=cache.get("ai_copilot_changes", {}),
        ai_risk_dashboard=cache.get("ai_risk_dashboard", {}),
        ai_engine_status=get_ai_engine_status(),
    )
