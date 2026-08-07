"""
Aureum AI Global Market Score Service

Beregner en samlet global markedstilstand
baseret på Market Intelligence data.
"""


def get_global_market_score(market_intelligence):
    """
    Returnerer global market score.
    """

    if not market_intelligence:
        return {
            "score": 0,
            "status": "Ukendt",
            "confidence": 0,
            "explanation": "Ingen markedsdata tilgængelig.",
        }


    markets = market_intelligence.get(
        "markets",
        []
    )

    open_markets = market_intelligence.get(
        "open_markets",
        []
    )

    closed_markets = market_intelligence.get(
        "closed_markets",
        []
    )

    data_quality = market_intelligence.get(
        "data_quality",
        {}
    )


    total = len(markets)

    if total == 0:
        return {
            "score": 0,
            "status": "Ukendt",
            "confidence": 0,
            "explanation": "Ingen markeder fundet.",
        }


    open_ratio = len(open_markets) / total


    score = 50

    # Åbne markeder
    score += int(
        open_ratio * 30
    )


    # Data kvalitet
    live_count = 0

    for quality in data_quality.values():
        if quality.get("freshness") == "LIVE":
            live_count += 1


    if total:
        live_ratio = live_count / total
        score += int(
            live_ratio * 20
        )


    score = min(
        max(score, 0),
        100
    )


    if score >= 75:
        status = "Positiv global markedstilstand"

    elif score >= 50:
        status = "Blandet global markedstilstand"

    else:
        status = "Forsigtig global markedstilstand"


    confidence = int(
        50 + (live_count / total) * 50
    )


    explanation = (
        f"{len(open_markets)} af {total} markeder er åbne. "
        f"{live_count} markeder leverer live data."
    )


    return {
        "score": score,
        "status": status,
        "confidence": confidence,
        "open_markets": open_markets,
        "closed_markets": closed_markets,
        "explanation": explanation,
    }
