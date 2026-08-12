"""
Aureum AI Portfolio Evolution Service

Sammenligner to Portfolio Health snapshots og returnerer
ændringer i Health Score, komponenter og porteføljesammensætning.
"""


def _to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _split_portfolio(snapshot):
    if not snapshot or snapshot == "-":
        return set()

    return {
        item.strip()
        for item in str(snapshot).split(",")
        if item.strip()
    }


def compare_portfolio_health(previous, current):
    """
    Sammenligner to Portfolio Health snapshots.
    """

    previous = previous or {}
    current = current or {}

    previous_portfolio = _split_portfolio(
        previous.get("portfolio_snapshot")
    )
    current_portfolio = _split_portfolio(
        current.get("portfolio_snapshot")
    )

    return {
        "date_from": previous.get("date"),
        "date_to": current.get("date"),

        "health": {
            "from": _to_float(previous.get("score")),
            "to": _to_float(current.get("score")),
            "change": round(
                _to_float(current.get("score"))
                - _to_float(previous.get("score")),
                1,
            ),
        },

        "risk": {
            "from": _to_float(previous.get("risk_score")),
            "to": _to_float(current.get("risk_score")),
            "change": round(
                _to_float(current.get("risk_score"))
                - _to_float(previous.get("risk_score")),
                1,
            ),
        },

        "diversification": {
            "from": _to_float(previous.get("diversification_score")),
            "to": _to_float(current.get("diversification_score")),
            "change": round(
                _to_float(current.get("diversification_score"))
                - _to_float(previous.get("diversification_score")),
                1,
            ),
        },

        "momentum": {
            "from": _to_float(previous.get("momentum_score")),
            "to": _to_float(current.get("momentum_score")),
            "change": round(
                _to_float(current.get("momentum_score"))
                - _to_float(previous.get("momentum_score")),
                1,
            ),
        },

        "confidence": {
            "from": _to_float(previous.get("confidence_score")),
            "to": _to_float(current.get("confidence_score")),
            "change": round(
                _to_float(current.get("confidence_score"))
                - _to_float(previous.get("confidence_score")),
                1,
            ),
        },

        "positions": {
            "from": int(previous.get("position_count", 0)),
            "to": int(current.get("position_count", 0)),
            "change": (
                int(current.get("position_count", 0))
                - int(previous.get("position_count", 0))
            ),
        },

        "portfolio": {
            "added": sorted(current_portfolio - previous_portfolio),
            "removed": sorted(previous_portfolio - current_portfolio),
            "unchanged": sorted(
                previous_portfolio & current_portfolio
            ),
        },
    }
