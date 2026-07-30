from ai_learning_trends_service import get_learning_trends
from ai_improvement_advisor_service import get_improvement_advisor


def get_ai_insight():
    """
    Genererer en samlet AI Learning-indsigt.
    """

    trends = get_learning_trends()
    advisor = get_improvement_advisor()

    trend = trends["trend"]
    change = trends["change"]

    if trend == "Forbedres":
        opening = (
            f"AI'ens confidence er steget med {change:.1f} procentpoint "
            "siden de første historiske målinger."
        )
    elif trend == "Faldende":
        opening = (
            f"AI'ens confidence er faldet med {abs(change):.1f} procentpoint "
            "og bør undersøges nærmere."
        )
    else:
        opening = (
            "AI'ens confidence har været stabil gennem den målte periode."
        )

    strengths = [
        item.rstrip(".")
        for item in advisor["strengths"][:2]
    ]

    summary = opening

    if strengths:
        summary += " De stærkeste observationer er: " + "; ".join(strengths) + "."

    return {
        "headline": "AI Learning Insight",
        "summary": summary,
    }
