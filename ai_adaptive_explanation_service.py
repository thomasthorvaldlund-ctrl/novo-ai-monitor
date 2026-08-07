from ai_adaptive_behavior_service import get_adaptive_behavior
from ai_adaptive_performance_service import get_adaptive_performance


def get_adaptive_explanation():
    """
    Genererer en forklaring af AI's adaptive læringsadfærd.
    """

    behavior = get_adaptive_behavior()
    performance = get_adaptive_performance()

    change = behavior.get(
        "change_behavior",
        {}
    )

    most_common_change = change.get(
        "most_common_change",
        "Ukendt"
    )

    change_rate = change.get(
        "change_rate",
        0
    )

    ai_style = behavior.get(
        "decision_style",
        {}
    ).get(
        "style",
        "Ukendt"
    )

    total_simulations = performance.get(
        "total_simulations",
        0
    )

    if change_rate >= 80:
        learning_signal = "Høj tilpasningsaktivitet"
    elif change_rate >= 40:
        learning_signal = "Moderat tilpasning"
    else:
        learning_signal = "Stabil beslutningsadfærd"


    headline = (
        f"AI viser {ai_style.lower()} læringsadfærd"
    )


    summary = (
        f"AI har analyseret {total_simulations} adaptive simulationer "
        f"og ændrer primært beslutninger via {most_common_change}. "
        f"Ændringsraten er {change_rate}%, hvilket indikerer "
        f"{learning_signal.lower()}."
    )


    if most_common_change == "BUY_to_HOLD":
        risk_interpretation = (
            "AI prioriterer risikostyring og reducerer aggressiv eksponering."
        )
    else:
        risk_interpretation = (
            "AI justerer løbende signaler baseret på ny information."
        )


    return {
        "headline": headline,
        "summary": summary,
        "risk_interpretation": risk_interpretation,
        "learning_signal": learning_signal,
        "confidence": 80
    }
