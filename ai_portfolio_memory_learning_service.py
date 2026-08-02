from ai_portfolio_memory_feedback_service import get_memory_feedback


def get_memory_learning():

    feedback = get_memory_feedback()

    action_stats = feedback.get("action_stats", {})


    strongest_signal = None
    strongest_score = -1


    for action, stats in action_stats.items():

        total = stats.get("total", 0)

        if total == 0:
            continue

        score = (
            stats.get("correct", 0)
            /
            total
            *
            100
        )


        if score > strongest_score:
            strongest_score = score
            strongest_signal = action



    learning_points = []

    recommendations = []


    if "REDUCE" in action_stats:

        reduce_stats = action_stats["REDUCE"]

        learning_points.append(
            "REDUCE-signaler har historisk haft høj præcision "
            "og identificerer effektivt risikoperioder."
        )

        recommendations.append(
            "AI bør have høj tillid til REDUCE-signaler."
        )


    if "WATCH" in action_stats:

        watch_stats = action_stats["WATCH"]

        learning_points.append(
            "WATCH bruges primært som overvågning og giver "
            "sjældent et klart resultat."
        )

        recommendations.append(
            "WATCH bør behandles som et usikkerhedssignal "
            "og ikke som en aktiv handelsbeslutning."
        )


    if "HOLD" in action_stats:

        learning_points.append(
            "HOLD fungerer stabilt, men mange historiske tilfælde "
            "forbliver neutrale."
        )


    confidence = 0

    if strongest_score >= 80:
        confidence = "Høj"

    elif strongest_score >= 60:
        confidence = "Moderat"

    else:
        confidence = "Lav"



    return {

        "cases_analyzed":
            feedback.get("evaluated_cases", 0),


        "strongest_signal":
            strongest_signal,


        "strongest_signal_score":
            round(strongest_score, 1),


        "confidence":
            confidence,


        "learning_points":
            learning_points,


        "recommendations":
            recommendations,


        "action_stats":
            action_stats,


        "summary":
            (
                "AI Learning Summary analyserer historiske "
                "beslutninger og identificerer mønstre, "
                "styrker og forbedringsområder."
            )
    }