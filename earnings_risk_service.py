import math

from ai_decision_service import get_ai_decision
from earnings_calendar_service import get_upcoming_earnings
from portfolio_stock_service import (
    get_monitored_stock_names,
    get_monitored_stocks,
)


DEFAULT_SCORE = 50.0


def _normalise_score(value):
    if isinstance(value, bool):
        return None

    try:
        score = float(value)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(score):
        return None

    return round(
        min(
            100.0,
            max(
                0.0,
                score,
            ),
        ),
        1,
    )


def _build_score_map(ranking):
    if not isinstance(ranking, list):
        return {}

    score_map = {}

    for item in ranking:
        if not isinstance(item, dict):
            continue

        stock = str(
            item.get(
                "stock",
                "",
            )
        ).strip().upper()

        score = _normalise_score(
            item.get(
                "combined_score"
            )
        )

        if stock and score is not None:
            score_map[stock] = score

    return score_map


def _get_date_message(days_left):
    if days_left < -1:
        return (
            "Regnskab var for "
            f"{abs(days_left)} dage siden"
        )

    if days_left == -1:
        return "Regnskab var i går"

    if days_left == 0:
        return "Regnskab er i dag"

    if days_left == 1:
        return "Regnskab er i morgen"

    return (
        f"Regnskab om {days_left} dage"
    )


def calculate_earnings_risk(
    stock,
    score,
    days_left,
):
    """
    Beregner risiko omkring et regnskab.

    Fortidige datoer markeres som udløbet
    og kan derfor aldrig udløse en aktiv
    regnskabsalarm.
    """

    normalised_score = _normalise_score(
        score
    )

    if normalised_score is None:
        normalised_score = DEFAULT_SCORE

    decision = get_ai_decision(
        normalised_score
    )

    signal = decision["signal"]

    if days_left < 0:
        alert_level = "EXPIRED"
        risk = "Low"
        message = "Regnskabet er afholdt."

    elif days_left <= 2:
        alert_level = "HIGH"

        if signal == "REDUCE":
            risk = "High"
            message = (
                "Høj opmærksomhed før "
                "regnskab."
            )
        elif signal == "WATCH":
            risk = "Medium"
            message = (
                "Overvåg position før "
                "regnskab."
            )
        else:
            risk = "Low"
            message = (
                "Regnskab er nært "
                "forestående."
            )

    elif days_left <= 7:
        alert_level = "ALERT"

        if signal == "REDUCE":
            risk = "High"
            message = (
                "Høj opmærksomhed før "
                "regnskab."
            )
        elif signal == "WATCH":
            risk = "Medium"
            message = (
                "Overvåg position før "
                "regnskab."
            )
        else:
            risk = "Low"
            message = (
                "Regnskab nærmer sig."
            )

    elif days_left <= 14:
        alert_level = "WATCH"

        if signal == "REDUCE":
            risk = "Medium"
            message = (
                "Svagt signal før kommende "
                "regnskab."
            )
        else:
            risk = "Low"
            message = (
                "Følg udviklingen frem mod "
                "regnskabet."
            )

    else:
        alert_level = "NORMAL"
        risk = "Low"
        message = (
            "Ingen særlig opmærksomhed."
        )

    return {
        "stock": stock,
        "days_left": days_left,
        "date_message": (
            _get_date_message(
                days_left
            )
        ),
        "alert_level": alert_level,
        "signal": signal,
        "score": normalised_score,
        "risk": risk,
        "message": message,
    }


def get_earnings_risks(
    ranking=None,
):
    """
    Kombinerer kommende regnskabsdatoer
    med aktuelle Combined Scores.

    Hvis ranking ikke leveres, anvendes
    en tydeligt markeret neutral fallback.
    """

    if not isinstance(
        ranking,
        list,
    ) or not ranking:
        from dashboard_cache_service import (
            load_dashboard_cache,
        )

        cache = load_dashboard_cache()

        ranking = cache.get(
            "combined_ranking",
            [],
        )

    portfolio_names = (
        get_monitored_stock_names()
    )

    portfolio_tickers = (
        get_monitored_stocks()
    )

    earnings = get_upcoming_earnings(
        ranking,
        portfolio_names=portfolio_names,
        portfolio_tickers=portfolio_tickers,
    )

    score_map = _build_score_map(
        ranking
    )

    results = []

    for item in earnings:
        stock = item["stock"]

        score = score_map.get(
            stock
        )

        if score is None:
            score = DEFAULT_SCORE
            score_source = "fallback"
        else:
            score_source = (
                "combined_ranking"
            )

        assessment = (
            calculate_earnings_risk(
                stock,
                score,
                item["days_left"],
            )
        )

        results.append({
            **item,
            **assessment,
            "score_source": score_source,
        })

    return results
