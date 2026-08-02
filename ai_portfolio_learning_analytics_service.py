from ai_portfolio_memory_feedback_service import get_memory_feedback


def get_learning_analytics():

    feedback = get_memory_feedback()

    action_stats = feedback.get("action_stats", {})

    signal_performance = {}


    for action, stats in action_stats.items():

        total = stats.get("total", 0)
        correct = stats.get("correct", 0)

        accuracy = 0

        if total:
            accuracy = round(
                correct / total * 100,
                1
            )

        signal_performance[action] = {
            "cases": total,
            "accuracy": accuracy,
            "correct": correct,
            "neutral": stats.get("neutral", 0),
            "incorrect": stats.get("incorrect", 0)
        }


    best_signal = None
    best_score = -1


    for signal, data in signal_performance.items():

        if data["cases"] >= 10 and data["accuracy"] > best_score:
            best_score = data["accuracy"]
            best_signal = signal


    confidence = "Lav"

    if best_score >= 80:
        confidence = "Høj"

    elif best_score >= 50:
        confidence = "Middel"


    return {

        "total_cases":
            feedback.get("evaluated_cases", 0),

        "signal_performance":
            signal_performance,

        "best_signal":
            best_signal,

        "best_signal_score":
            best_score,

        "confidence":
            confidence
    }
