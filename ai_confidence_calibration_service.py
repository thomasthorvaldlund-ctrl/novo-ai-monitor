from ai_portfolio_performance_service import get_portfolio_performance


LEVELS = (
    ("Very High", 80),
    ("High", 60),
    ("Medium", 40),
    ("Low", 0),
)


SUCCESS = {
    "God beslutning",
    "God risikostyring",
    "Stabil vurdering",
    "Positiv udvikling",
}


def confidence_level(score):
    """
    Returnerer confidence-niveau ud fra AI-score.
    """
    score = score or 0

    for level, minimum in LEVELS:
        if score >= minimum:
            return level

    return "Low"


def get_confidence_calibration():
    """
    Beregner AI-accuracy opdelt på confidence-niveau.
    """
    performance = get_portfolio_performance()

    calibration = {
        level: {
            "total": 0,
            "correct": 0,
            "accuracy_pct": 0.0,
        }
        for level, _ in LEVELS
    }

    for row in performance:
        level = confidence_level(row.get("score"))

        calibration[level]["total"] += 1

        if row.get("ai_result") in SUCCESS:
            calibration[level]["correct"] += 1

    for stats in calibration.values():
        if stats["total"] > 0:
            stats["accuracy_pct"] = round(
                stats["correct"] / stats["total"] * 100,
                1,
            )

    return calibration
