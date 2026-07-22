from earnings_calendar_service import get_upcoming_earnings
from ai_decision_service import get_ai_decision


def calculate_earnings_risk(stock, score, days_left):
    """
    Beregner risiko omkring kommende regnskab.
    """

    decision = get_ai_decision(score)

    risk = "Low"
    message = "Ingen særlig opmærksomhed."

    if days_left <= 7:

        if decision["signal"] == "REDUCE":
            risk = "High"
            message = "Høj opmærksomhed før regnskab."

        elif decision["signal"] == "WATCH":
            risk = "Medium"
            message = "Overvåg position før regnskab."

        else:
            risk = "Low"
            message = "Regnskab nærmer sig."

    return {
        "stock": stock,
        "days_left": days_left,
        "signal": decision["signal"],
        "score": score,
        "risk": risk,
        "message": message,
    }


def get_earnings_risks():

    earnings = get_upcoming_earnings()

    results = []

    example_scores = {
        "DSV": 38,
        "NOVO": 50,
        "GENMAB": 50,
        "PANDORA": 50,
        "VESTAS": 50,
    }

    for item in earnings:

        score = example_scores.get(
            item["stock"],
            50
        )

        results.append(
            calculate_earnings_risk(
                item["stock"],
                score,
                item["days_left"]
            )
        )

    return results