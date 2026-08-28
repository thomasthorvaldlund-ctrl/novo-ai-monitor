def explain_stock(stock_data):
    """
    Returnerer en forklaring baseret på eksisterende aktiedata.
    Første version bruger Combined Score, teknisk score,
    nyhedsscore og ugentlig kursændring.
    """

    stock = stock_data.get("stock", "Ukendt")
    score = stock_data.get("combined_score")
    technical_score = stock_data.get("technical_score", 0)
    news_score = stock_data.get("news_score", 0)
    weekly_change = stock_data.get("weekly_change")
    weekly_change_available = isinstance(
        weekly_change,
        (int, float),
    )
    rating = str(
        stock_data.get(
            "rating",
            "Ukendt",
        )
    ).strip() or "Ukendt"

    positives = []
    negatives = []

    if technical_score >= 65:
        positives.append("Stærk teknisk udvikling")
    elif technical_score < 50:
        negatives.append("Svag teknisk udvikling")

    if news_score >= 65:
        positives.append("Positivt nyhedsbillede")
    elif news_score < 50:
        negatives.append("Negativt nyhedsbillede")

    if weekly_change_available and weekly_change >= 5:
        positives.append(
            f"Stærkt momentum med {weekly_change:.1f}% stigning på en uge"
        )
    elif weekly_change_available and weekly_change <= -5:
        negatives.append(
            f"Svagt momentum med {weekly_change:.1f}% fald på en uge"
        )

    if score is None:
        headline = f"Ingen samlet score for {stock}"
        confidence = 30
    elif rating == "Stærk kandidat":
        headline = f"{stock} vurderes som en stærk kandidat"
        confidence = 85
    elif rating == "Kandidat":
        headline = f"{stock} vurderes som kandidat"
        confidence = 75
    elif rating == "Neutral":
        headline = (
            f"{stock} har blandede eller neutrale signaler"
        )
        confidence = 60
    else:
        headline = f"{stock} kræver ekstra forsigtighed"
        confidence = 60

    if negatives:
        primary_reason = negatives[0]
    elif news_score >= technical_score and news_score >= 65:
        primary_reason = "Positivt nyhedsbillede"
    elif technical_score >= 65:
        primary_reason = "Stærk teknisk udvikling"
    elif weekly_change_available and weekly_change >= 5:
        primary_reason = "Stærkt kortsigtet momentum"
    else:
        primary_reason = "Blandede eller neutrale signaler"

    positive_text = (
        ", ".join(positives)
        if positives
        else "ingen tydelige positive signaler"
    )

    negative_text = (
        ", ".join(negatives)
        if negatives
        else "ingen tydelige negative signaler"
    )

    summary = (
        f"{stock} har en Combined Score på "
        f"{score if score is not None else 'ukendt'} "
        f"og vurderingen '{rating}'. "
        f"Positive forhold: {positive_text}. "
        f"Negative forhold: {negative_text}."
    )

    if score is None:
        conclusion = (
            "Der er endnu ikke nok data til en sikker vurdering."
        )
    elif rating == "Stærk kandidat":
        conclusion = (
            "Den samlede vurdering understøttes af flere stærke "
            "signaler, og aktien fremstår attraktiv lige nu."
        )
    elif rating == "Kandidat":
        conclusion = (
            "Den samlede vurdering er positiv, men der er også "
            "forhold, som bør overvåges."
        )
    elif rating == "Neutral":
        conclusion = (
            "Den samlede vurdering er neutral, fordi signalerne "
            "er blandede eller uden tydelig retning."
        )
    else:
        conclusion = (
            "Den samlede vurdering er svag, og aktien kræver "
            "ekstra forsigtighed."
        )

    return {
        "stock": stock,
        "headline": headline,
        "summary": summary,
        "conclusion": conclusion,
        "score": score,
        "rating": rating,
        "confidence": confidence,
        "primary_reason": primary_reason,
        "technical": technical_score,
        "news": news_score,
        "macro": 0,
        "earnings": 0,
        "positives": positives,
        "negatives": negatives,
    }