from flask import Blueprint, render_template, request

from dashboard_cache_service import load_dashboard_cache
from system_health_service import get_system_health
from market_score_service import get_market_score
from market_summary_service import get_market_summary
from top_picks_service import get_top_picks
from combined_score_service import combined_stock_score as service_combined_score
from openai_service import client
from ai_alerts_service import get_ai_alerts
from portfolio_summary_service import get_portfolio_summary
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
from ai_decision_intelligence_service import get_decision_intelligence
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


command_center_bp = Blueprint("command_center", __name__)

@command_center_bp.route("/command-center")
def command_center():
    return command_center_v2()


# Stock AI Monitor v2.0 testside
@command_center_bp.route("/command-center-v2")
def command_center_v2():
    cache = load_dashboard_cache()
    updated_at = cache.get("updated_at", "Ukendt")

    system_health = cache.get("system_health", get_system_health())
    market = cache.get("market", get_market_score())
    summary = cache.get("summary", get_market_summary())
    alerts = cache.get("alerts", get_ai_alerts())
    portfolio = cache.get("portfolio", get_portfolio_summary())

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
    earnings_ai = cache.get("earnings_ai", [])
    earnings_risks = cache.get("earnings_risks", [])
    executive_summary = cache.get("executive_summary", {})
    ai_copilot = cache.get("ai_copilot", {})
    ai_copilot_timeline = cache.get("ai_copilot_timeline", [])
    ai_copilot_changes = cache.get("ai_copilot_changes", {})
    ai_risk_dashboard = cache.get("ai_risk_dashboard", {})
    decision_quality = cache.get("decision_quality", {})
    decision_learning = cache.get("decision_learning", {})
    decision_learning_trend = cache.get("decision_learning_trend", {})

    ai_engine_status = get_ai_engine_status()

    return render_template(
        "command_center_v2.html",
        system_health=system_health,
        market=market,
        top_picks=top_picks,
        summary=summary,
        alerts=alerts,
        portfolio=portfolio,
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
        earnings_ai=earnings_ai,
        earnings_risks=earnings_risks,
        executive_summary=executive_summary,
        ai_copilot=ai_copilot,
        ai_copilot_timeline=ai_copilot_timeline,
        ai_copilot_changes=ai_copilot_changes,
        ai_risk_dashboard=ai_risk_dashboard,
        decision_quality=decision_quality,
        decision_learning=decision_learning,
        decision_learning_trend=decision_learning_trend,
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

    stock_explanations = cache.get(
        "stock_explanations",
        []
    )

    selected_stock = request.args.get("stock", "").strip().upper()
    selected_signal = request.args.get("signal", "").strip().upper()

    performance = cache.get("performance", {})

    signal_stocks = {
        "BUY": performance.get("buy_stocks", []),
        "HOLD": performance.get("hold_stocks", []),
        "WATCH": performance.get("watch_stocks", []),
        "SELL": performance.get("sell_stocks", []),
    }

    if selected_signal in signal_stocks:
        allowed_stocks = {
            stock.strip().upper()
            for stock in signal_stocks[selected_signal]
        }

        stock_explanations = [
            item
            for item in stock_explanations
            if item.get("stock", "").strip().upper() in allowed_stocks
        ]
    else:
        selected_signal = ""

    return render_template(
        "ai_stock_library.html",
        stock_explanations=stock_explanations,
        selected_stock=selected_stock,
        selected_signal=selected_signal,
        performance=performance,
    )


@command_center_bp.route("/ai-portfolio-lab")
def ai_portfolio_lab():

    cache = load_dashboard_cache()

    return render_template(
        "ai_portfolio_lab.html",
        portfolio_insights=cache.get("portfolio_insights", []),
        portfolio_recommendations=cache.get("portfolio_recommendations", []),
        rebalancing=cache.get("rebalancing", {}),
        portfolio_decision_history=load_portfolio_decisions(),
        portfolio_changes=get_portfolio_changes(),
        portfolio_performance=get_portfolio_performance(),
        portfolio_analytics=get_portfolio_analytics(),
        learning_report=get_learning_report(),
        learning_timeline=get_learning_timeline(),
        confidence_calibration=get_confidence_calibration(),
        portfolio_confidence_calibration=get_portfolio_confidence_calibration(),
        learning_by_stock=get_learning_by_stock(),
        signal_accuracy=get_signal_accuracy(),
        improvement_advisor=get_improvement_advisor(),
        learning_trends=get_learning_trends(),
        ai_insight=get_ai_insight(),
        pattern_detection=get_pattern_detection(),
        prediction_engine=get_prediction_engine(),
        decision_optimizer=get_decision_optimizer(),
        learning_feedback=get_learning_feedback(),
        ai_context=get_ai_context(),
        ai_strategy=get_ai_strategy(),
        ai_copilot=get_ai_copilot(),
        copilot_decision=get_copilot_decision(),
        decision_intelligence=get_decision_intelligence(),
        decision_performance=get_decision_performance(),
        ai_portfolio_executive=get_ai_portfolio_executive(),
        ai_portfolio_brain=get_ai_portfolio_brain(),
        brain_score=get_brain_score(),
        brain_score_explanation=get_brain_score_explanation(),
        decision_memory=get_decision_memory(),
        memory_trends=get_memory_trends(),
        memory_insights=get_memory_insights(),
        memory_advisor=get_memory_advisor(),
        memory_center=get_memory_center(),
        memory_intelligence=get_memory_intelligence(),
        memory_learning=get_memory_learning(),
          learning_evolution=get_learning_evolution(),
          learning_analytics=get_learning_analytics(),
        ai_portfolio_overview=get_ai_portfolio_overview(),
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
        earnings_ai=cache.get("earnings_ai", []),
        earnings_risks=cache.get("earnings_risks", []),
        executive_summary=cache.get("executive_summary", {}),
        ai_copilot=cache.get("ai_copilot", {}),
        ai_copilot_timeline=cache.get("ai_copilot_timeline", []),
        ai_copilot_changes=cache.get("ai_copilot_changes", {}),
        ai_risk_dashboard=cache.get("ai_risk_dashboard", {}),
        ai_engine_status=get_ai_engine_status(),
    )
