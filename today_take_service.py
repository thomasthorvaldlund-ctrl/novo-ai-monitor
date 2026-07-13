from ai_alerts_service import get_ai_alerts


def get_today_take(
    market,
    top_pick,
    performance,
    ai_news,
):
    """
    Returnerer dagens regelbaserede AI-opsummering.
    """

    market_score = market.get("score", 50)

    buy_count = performance.get("buy", 0)
    hold_count = performance.get("hold", 0)
    watch_count = performance.get("watch", 0)
    sell_count = performance.get("sell", 0)

    alerts = get_ai_alerts()
    critical_alerts = [
        alert
        for alert in alerts
        if alert.get("level") != "green"
    ]
    alert_count = len(critical_alerts)

    if market_score >= 70:
        market_text = "Markedet vurderes positivt."
        risk_level = "Lav"
    elif market_score >= 50:
        market_text = "Markedet vurderes neutralt."
        risk_level = "Moderat"
    else:
        market_text = "Markedet vurderes fortsat svagt."
        risk_level = "Forhøjet"

    alert_stocks = [
        alert.get("title", "Ukendt")
        for alert in critical_alerts
    ]

    if critical_alerts:
        alert_text = (
            f"{alert_count} kritiske AI-alerts."
        )
    else:
        alert_text = "Ingen kritiske AI-alerts."

    if top_pick:
        top_stock = top_pick.get("stock", "Ukendt")
        top_score = top_pick.get("score")
        top_signal = top_pick.get("signal", "Ukendt")
        top_stars = top_pick.get("stars", "")
        top_text = f"Dagens Top Pick er {top_stock}."
    else:
        top_stock = None
        top_score = None
        top_signal = None
        top_stars = ""
        top_text = "Ingen Top Pick tilgængelig."

    signal_text = (
        f"{buy_count} BUY, "
        f"{hold_count} HOLD, "
        f"{watch_count} WATCH og "
        f"{sell_count} SELL."
    )

    news_status = ai_news.get("status")

    if not news_status or news_status == "Unavailable":
        news_text = "Nyhedsanalysen er midlertidigt utilgængelig."
    else:
        news_text = (
            f"Nyhedsbilledet vurderes som "
            f"{news_status.lower()}."
        )

    summary = (
        f"Der er aktuelt {buy_count} BUY-signaler, "
        f"{hold_count} HOLD-signaler og "
        f"{watch_count} WATCH-signaler. "
        f"{alert_text}"
    )

    if market_score < 50:
        recommendation = (
            "Afvent nye køb, indtil Market Score og de tekniske "
            "signaler viser tydelig bedring. Behold fokus på "
            "kvalitetsaktier og overvåg WATCH-positionerne tæt."
        )
    elif buy_count > 0:
        recommendation = (
            "Markedet understøtter selektive køb. Prioritér aktier "
            "med stærk Combined Score og høj AI-confidence."
        )
    else:
        recommendation = (
            "Behold eksisterende kvalitetspositioner og afvent "
            "stærkere BUY-signaler, før nye positioner åbnes."
        )

    if top_stock:
        recommendation += (
            f" {top_stock} er aktuelt den stærkeste kandidat."
        )

    return {
        "headline": market_text,
        "summary": summary,
        "recommendation": recommendation,
        "risk_level": risk_level,
        "top_pick": top_text,
        "top_pick_stock": top_stock,
        "top_pick_score": top_score,
        "top_pick_signal": top_signal,
        "top_pick_stars": top_stars,
        "alerts": alert_text,
        "alert_stocks": alert_stocks,
        "signals": signal_text,
        "news": news_text,
    }
