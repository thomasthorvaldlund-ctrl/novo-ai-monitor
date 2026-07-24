RISK_LEVELS = {
    "Lav": 1,
    "Moderat": 2,
    "Høj": 3,
    "Kritisk": 4,
}


def _to_number(value, default=0):
    """
    Konverterer værdier sikkert til float.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _risk_rank(value):
    """
    Returnerer numerisk rangering af risikoniveau.
    """
    if value is None:
        return 0

    normalized = str(value).strip().capitalize()
    return RISK_LEVELS.get(normalized, 0)


def _format_number(value):
    """
    Formaterer tal uden unødvendige decimaler.
    """
    number = _to_number(value)

    if number.is_integer():
        return str(int(number))

    return f"{number:.1f}"


def compare_copilot_snapshots(previous, current):
    """
    Sammenligner to AI Copilot snapshots.

    Returnerer:
        changed: om der er registreret ændringer
        status: positive, negative eller neutral
        changes: beskrivelser af de registrerede ændringer
    """

    if not previous or not current:
        return {
            "changed": False,
            "status": "neutral",
            "changes": [
                "Ingen tidligere AI Copilot analyse til sammenligning."
            ],
        }

    changes = []
    positive_weight = 0
    negative_weight = 0

    previous_headline = previous.get("headline")
    current_headline = current.get("headline")

    if previous_headline != current_headline:
        changes.append(
            f"AI-vurdering ændret: "
            f"{previous_headline or 'Ukendt'} → "
            f"{current_headline or 'Ukendt'}"
        )

    previous_opportunity = previous.get("best_opportunity")
    current_opportunity = current.get("best_opportunity")

    if previous_opportunity != current_opportunity:
        changes.append(
            f"Topkandidat ændret: "
            f"{previous_opportunity or 'Ingen'} → "
            f"{current_opportunity or 'Ingen'}"
        )

    previous_confidence = _to_number(
        previous.get("confidence")
    )
    current_confidence = _to_number(
        current.get("confidence")
    )

    confidence_change = current_confidence - previous_confidence

    if confidence_change != 0:
        direction = "+" if confidence_change > 0 else ""

        changes.append(
            f"AI confidence ændret: "
            f"{_format_number(previous_confidence)} → "
            f"{_format_number(current_confidence)} "
            f"({direction}{_format_number(confidence_change)})"
        )

        if confidence_change > 0:
            positive_weight += 1
        else:
            negative_weight += 1

    previous_risk_level = previous.get("risk_level")
    current_risk_level = current.get("risk_level")

    if previous_risk_level != current_risk_level:
        changes.append(
            f"Copilot-risiko ændret: "
            f"{previous_risk_level or 'Ukendt'} → "
            f"{current_risk_level or 'Ukendt'}"
        )

        old_rank = _risk_rank(previous_risk_level)
        new_rank = _risk_rank(current_risk_level)

        if old_rank and new_rank:
            if new_rank < old_rank:
                positive_weight += 3
            elif new_rank > old_rank:
                negative_weight += 3

    previous_overall_risk = previous.get("overall_risk")
    current_overall_risk = current.get("overall_risk")

    if previous_overall_risk != current_overall_risk:
        changes.append(
            f"Samlet AI Risk ændret: "
            f"{previous_overall_risk or 'Ukendt'} → "
            f"{current_overall_risk or 'Ukendt'}"
        )

        old_rank = _risk_rank(previous_overall_risk)
        new_rank = _risk_rank(current_overall_risk)

        if old_rank and new_rank:
            if new_rank < old_rank:
                positive_weight += 3
            elif new_rank > old_rank:
                negative_weight += 3

    previous_risk_score = _to_number(
        previous.get("risk_score")
    )
    current_risk_score = _to_number(
        current.get("risk_score")
    )

    risk_score_change = current_risk_score - previous_risk_score

    if risk_score_change != 0:
        direction = "+" if risk_score_change > 0 else ""

        changes.append(
            f"AI Risk Score ændret: "
            f"{_format_number(previous_risk_score)} → "
            f"{_format_number(current_risk_score)} "
            f"({direction}{_format_number(risk_score_change)})"
        )

        if risk_score_change < 0:
            positive_weight += 2
        else:
            negative_weight += 2

    previous_reasons = previous.get("risk_reasons") or []
    current_reasons = current.get("risk_reasons") or []

    previous_reasons_set = {
        str(reason).strip()
        for reason in previous_reasons
        if reason
    }
    current_reasons_set = {
        str(reason).strip()
        for reason in current_reasons
        if reason
    }

    added_reasons = sorted(
        current_reasons_set - previous_reasons_set
    )
    removed_reasons = sorted(
        previous_reasons_set - current_reasons_set
    )

    if added_reasons:
        changes.append(
            "Nye risikofaktorer: "
            + ", ".join(added_reasons)
        )
        negative_weight += len(added_reasons)

    if removed_reasons:
        changes.append(
            "Risikofaktorer fjernet: "
            + ", ".join(removed_reasons)
        )
        positive_weight += len(removed_reasons)

    status = "neutral"

    if positive_weight > negative_weight:
        status = "positive"
    elif negative_weight > positive_weight:
        status = "negative"

    return {
        "changed": bool(changes),
        "status": status,
        "changes": changes if changes else [
            "Ingen væsentlige ændringer siden sidste analyse."
        ],
    }
