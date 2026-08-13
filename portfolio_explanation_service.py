def generate_portfolio_explanation(item):
    """
    Genererer en menneskelig forklaring
    af en AI porteføljeanbefaling.
    """

    stock = item.get("stock")
    recommendation = item.get("recommendation")
    score = item.get("score", 0)
    technical = item.get("technical_score", 0)
    news = item.get("news_score", 0)
    profit = item.get("profit_pct", 0)
    risk = item.get("concentration_risk", "Ukendt")
    portfolio_action = item.get(
        "portfolio_action",
        "NONE"
    )
    portfolio_reason = item.get(
        "portfolio_reason",
        ""
    )


    if recommendation == "REDUCE":
        headline = f"{stock} vurderes som svagere på nuværende tidspunkt."
        action = "Overvej reduktion eller tæt overvågning."

    elif recommendation == "HOLD":
        headline = f"{stock} vurderes stabil af AI."
        action = "Behold position og følg udviklingen."

    elif recommendation == "BUY":
        headline = f"{stock} har positive AI signaler."
        action = "Overvej øget eksponering."

    else:
        headline = f"{stock} bør overvåges."
        action = "Afvent yderligere signaler."


    factors = []

    if portfolio_action == "DIVERSIFY":
        if portfolio_reason:
            factors.append(
                portfolio_reason
            )
        else:
            factors.append(
                "Porteføljen har høj koncentrationsrisiko."
            )

        if recommendation == "HOLD":
            headline = (
                f"{stock} vurderes stabil af AI, "
                "men porteføljen er koncentreret."
            )
            action = (
                "Behold positionen, men prioriter nye investeringer "
                "i andre kvalitetsaktier for at reducere "
                "koncentrationsrisikoen."
            )

        elif recommendation == "WATCH":
            action = (
                "Overvåg positionen og prioriter samtidig "
                "diversificering af porteføljen."
            )

        elif recommendation == "REDUCE":
            action = (
                "Overvej reduktion af positionen og prioriter "
                "samtidig diversificering af porteføljen."
            )

    if score < 50:
        factors.append(
            f"Samlet AI score er lav ({score}/100)."
        )

    elif score >= 60:
        factors.append(
            f"Stabil AI score ({score}/100)."
        )


    if technical < 50:
        factors.append(
            f"Teknisk score er svag ({technical}/100)."
        )

    elif technical >= 70:
        factors.append(
            f"Teknisk styrke ({technical}/100)."
        )


    if news >= 70:
        factors.append(
            f"Nyhedsbilledet er positivt ({news}/100)."
        )


    if profit < 0:
        factors.append(
            f"Aktien har negativt afkast ({profit:.1f}%)."
        )

    elif profit > 5:
        factors.append(
            f"Positivt afkast ({profit:.1f}%)."
        )


    return {
        "stock": stock,
        "headline": headline,
        "summary": " ".join(factors),
        "action": action,
        "risk": risk,
        "portfolio_action": portfolio_action,
        "portfolio_reason": portfolio_reason,
    }
