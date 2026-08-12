"""
Aureum AI Portfolio Health Service

Omsætter eksisterende porteføljedata til et kort og forklarligt
helbredstjek. Servicen foretager ingen eksterne API-kald.
"""

from statistics import mean

from asset_registry import find_asset_by_ticker


RISK_LABELS = {
    "Low": "Lav",
    "Medium": "Moderat",
    "High": "Høj",
}


def _clamp(value, minimum=0.0, maximum=100.0):
    return max(minimum, min(maximum, float(value)))


def _status_from_score(score):
    if score >= 75:
        return "God"
    if score >= 55:
        return "Moderat"
    return "Kræver opmærksomhed"


def _level_from_score(score):
    if score >= 75:
        return "good"
    if score >= 55:
        return "medium"
    return "weak"


def get_portfolio_health(portfolio_summary):
    """
    Returnerer et forklarligt Portfolio Health-overblik.

    Forventede inputfelter:
    - portfolio_score
    - portfolio_risk
    - position_details
    - recommendations
    - best_position
    - weakest_position
    """

    summary = portfolio_summary or {}
    positions = summary.get("position_details", []) or []
    recommendations = summary.get("recommendations", {}) or {}

    portfolio_score = _clamp(summary.get("portfolio_score", 0))

    confidences = [
        float(position.get("confidence", 0))
        for position in positions
        if position.get("confidence") is not None
    ]
    confidence_score = mean(confidences) if confidences else 0.0

    weights = []
    countries = set()
    regions = set()
    sectors = set()

    for position in positions:
        raw_weight = position.get("weight_pct", 0)

        if isinstance(raw_weight, str):
            raw_weight = raw_weight.replace("%", "").strip()

        try:
            weights.append(float(raw_weight))
        except (TypeError, ValueError):
            continue

        asset = find_asset_by_ticker(position.get("ticker"))

        if asset:
            country = asset.get("country")
            region = asset.get("region")
            sector = asset.get("sector")

            if country:
                countries.add(country)

            if region:
                regions.add(region)

            if sector:
                sectors.add(sector)

    largest_weight = max(weights, default=0.0)
    position_count = len(positions)

    # 1. Koncentration
    if largest_weight <= 20:
        concentration_score = 100.0
    elif largest_weight <= 30:
        concentration_score = 80.0
    elif largest_weight <= 40:
        concentration_score = 60.0
    elif largest_weight <= 50:
        concentration_score = 40.0
    else:
        concentration_score = 20.0

    # 2. Sektorspredning
    sector_count = len(sectors)

    if sector_count >= 5:
        sector_score = 100.0
    elif sector_count >= 4:
        sector_score = 85.0
    elif sector_count >= 3:
        sector_score = 70.0
    elif sector_count >= 2:
        sector_score = 50.0
    else:
        sector_score = 20.0

    # 3. Regionspredning
    region_count = len(regions)

    if region_count >= 3:
        region_score = 100.0
    elif region_count == 2:
        region_score = 60.0
    else:
        region_score = 20.0

    # 4. Landespredning
    country_count = len(countries)

    if country_count >= 5:
        country_score = 100.0
    elif country_count >= 4:
        country_score = 85.0
    elif country_count >= 3:
        country_score = 70.0
    elif country_count >= 2:
        country_score = 50.0
    else:
        country_score = 20.0

    diversification_score = round(
        concentration_score * 0.40
        + sector_score * 0.30
        + region_score * 0.20
        + country_score * 0.10,
        1,
    )

    risk = summary.get("portfolio_risk", "Unknown")

    risk_scores = {
        "Low": 90.0,
        "Medium": 65.0,
        "High": 35.0,
    }
    risk_score = risk_scores.get(risk, 50.0)

    def _momentum_from_score(score):
        try:
            score = float(score)
        except (TypeError, ValueError):
            return 20.0

        if score >= 80:
            return 100.0
        elif score >= 70:
            return 80.0
        elif score >= 60:
            return 60.0
        elif score >= 50:
            return 40.0
        return 20.0

    momentum_values = [
        _momentum_from_score(position.get("score"))
        for position in positions
    ]

    momentum_score = (
        sum(momentum_values) / len(momentum_values)
        if momentum_values
        else 0.0
    )

    health_score = round(
        portfolio_score * 0.40
        + risk_score * 0.20
        + diversification_score * 0.20
        + confidence_score * 0.10
        + momentum_score * 0.10,
        1,
    )

    reduce = recommendations.get("reduce", []) or []
    increase = recommendations.get("increase", []) or []

    observations = []

    if diversification_score < 55:
        observations.append(
            "Porteføljen er koncentreret på få positioner."
        )

    if reduce:
        observations.append(
            "AI anbefaler særlig opmærksomhed på "
            + ", ".join(reduce)
            + "."
        )

    if increase:
        observations.append(
            "Stærkeste positive signal findes i "
            + ", ".join(increase)
            + "."
        )

    if not observations:
        observations.append(
            "Der er ingen væsentlige porteføljeproblemer identificeret."
        )

    if health_score >= 75:
        conclusion = (
            "Porteføljen vurderes som robust, men bør fortsat "
            "overvåges for ændringer i risiko og signaler."
        )
    elif health_score >= 55:
        conclusion = (
            "Porteføljen vurderes som moderat sund. "
            "Den største forbedringsmulighed er bedre spredning "
            "og opfølgning på svage positioner."
        )
    else:
        conclusion = (
            "Porteføljen kræver opmærksomhed. Risiko, koncentration "
            "og svage AI-signaler bør gennemgås før nye investeringer."
        )

    return {
        "score": health_score,
        "status": _status_from_score(health_score),
        "level": _level_from_score(health_score),
        "risk": {
            "label": RISK_LABELS.get(risk, risk),
            "score": risk_score,
            "level": _level_from_score(risk_score),
        },
        "diversification": {
            "label": _status_from_score(diversification_score),
            "score": diversification_score,
            "level": _level_from_score(diversification_score),
            "position_count": position_count,
            "largest_weight": round(largest_weight, 1),
        },
        "momentum": {
            "label": _status_from_score(momentum_score),
            "score": round(momentum_score, 1),
            "level": _level_from_score(momentum_score),
        },
        "confidence": {
            "label": _status_from_score(confidence_score),
            "score": round(confidence_score, 1),
            "level": _level_from_score(confidence_score),
        },
        "best_position": summary.get("best_position", "-"),
        "weakest_position": summary.get("weakest_position", "-"),
        "observations": observations,
        "conclusion": conclusion,
    }
