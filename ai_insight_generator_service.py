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
            f"AI'ens historiske beslutningspræcision er steget med "
            f"{change:.1f} procentpoint siden de første sammenlignelige "
            "Decision Events v2-målinger."
        )
    elif trend == "Faldende":
        opening = (
            f"AI'ens historiske beslutningspræcision er faldet med "
            f"{abs(change):.1f} procentpoint og bør undersøges nærmere."
        )
    elif trend == "Stabil":
        opening = (
            "AI'ens historiske beslutningspræcision har været stabil "
            "gennem den målte periode."
        )
    elif trend == "For lidt historik":
        opening = (
            "Der er endnu for få sammenlignelige Decision Events v2-"
            "snapshots til at vurdere udviklingen i AI'ens historiske "
            "beslutningspræcision."
        )
    else:
        opening = (
            "Der er endnu ikke tilstrækkelig historik til at vurdere "
            "udviklingen i AI'ens beslutningspræcision."
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
