from ai_portfolio_decision_memory_service import get_decision_memory
from ai_portfolio_memory_trend_service import get_memory_trends
from ai_portfolio_memory_insight_service import get_memory_insights
from ai_portfolio_memory_advisor_service import get_memory_advisor


def get_memory_center():

    decision_memory = get_decision_memory()
    memory_trends = get_memory_trends()
    memory_insights = get_memory_insights()
    memory_advisor = get_memory_advisor()


    return {

        "decision_memory": decision_memory,

        "trends": memory_trends,

        "insights": memory_insights,

        "advisor": memory_advisor,


        "summary":
            (
                "AI Portfolio Memory Center samler historiske "
                "beslutninger, mønstre, trends og anbefalinger."
            )
    }
