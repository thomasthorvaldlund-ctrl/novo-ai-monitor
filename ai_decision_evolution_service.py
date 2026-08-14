import json
from pathlib import Path

from aureum_paths import data_path
from collections import defaultdict
from portfolio import load_portfolio_rows


DECISION_FILE = data_path(
    "ai_portfolio_decisions.json"
)


def load_history():

    if not DECISION_FILE.exists():
        return []

    with open(
        DECISION_FILE,
        encoding="utf-8"
    ) as f:
        return json.load(f)



def calculate_stability(change_count):

    if change_count >= 15:
        return "Lav"

    if change_count >= 8:
        return "Middel"

    return "Høj"



def get_decision_evolution():

    history = load_history()

    current_stocks = {
        row.get("stock")
        for row in load_portfolio_rows()
        if row.get("stock")
    }

    stocks = defaultdict(list)

    for snapshot in history:

        for decision in snapshot.get("decisions", []):

            stock = decision.get("stock")

            if stock not in current_stocks:
                continue

            stocks[stock].append(
                {
                    "date": snapshot["date"],
                    "action": decision["action"],
                    "score": decision["score"],
                    "reason": decision["reason"],
                    "weight_pct": decision.get(
                        "weight_pct"
                    ),
                    "portfolio_action": (
                        decision.get(
                            "portfolio_action"
                        )
                        or "NONE"
                    ),
                    "portfolio_reason": (
                        decision.get(
                            "portfolio_reason"
                        )
                        or ""
                    ),
                }
            )


    results = []


    for stock, items in stocks.items():

        changes = []


        previous = items[0]

        for current in items[1:]:

            if current["action"] != previous["action"]:

                changes.append(
                    {
                        "from": previous,
                        "to": current
                    }
                )

            previous = current


        if changes:

            latest_change = changes[-1]

            old = latest_change["from"]
            new = latest_change["to"]
            current_state = items[-1]

            results.append(
                {
                    "stock": stock,
                    "changed": True,

                    "previous_action": old["action"],
                    "current_action": new["action"],

                    "previous_score": old["score"],
                    "current_score": new["score"],
                    "score_change": new["score"] - old["score"],

                    "previous_reason": old["reason"],
                    "current_reason": new["reason"],

                    "previous_weight_pct": old.get(
                        "weight_pct"
                    ),
                    "current_weight_pct": current_state.get(
                        "weight_pct"
                    ),

                    "previous_portfolio_action": old.get(
                        "portfolio_action",
                        "NONE",
                    ),
                    "current_portfolio_action": current_state.get(
                        "portfolio_action",
                        "NONE",
                    ),

                    "previous_portfolio_reason": old.get(
                        "portfolio_reason",
                        "",
                    ),
                    "current_portfolio_reason": current_state.get(
                        "portfolio_reason",
                        "",
                    ),

                    "changed_at": new["date"],
                    "change_count": len(changes),

                    "stability": calculate_stability(
                        len(changes)
                    )
                }
                )

    for item in results:
        item[
            "legacy_concentration_transition"
        ] = _is_legacy_concentration_transition(
            item
        )

        item["explanation"] = (
            generate_evolution_explanation(
                item
            )
        )

    return results

def _is_legacy_concentration_transition(item):
    previous_reason = str(
        item.get(
            "previous_reason",
            ""
        )
        or ""
    ).lower()

    concentration_reason = (
        "fylder for meget i porteføljen"
        in previous_reason
        or "koncentr"
        in previous_reason
    )

    return (
        item.get("previous_action") == "REDUCE"
        and item.get("current_action") != "REDUCE"
        and item.get("score_change", 0) == 0
        and concentration_reason
    )


def generate_evolution_explanation(item):
    """
    Genererer en menneskelig forklaring
    på hvorfor AI ændrede beslutning.
    """

    if not item.get("changed"):
        return (
            "AI har ikke ændret vurdering "
            "for denne aktie."
        )

    score_change = item.get(
        "score_change",
        0
    )

    if item.get(
        "legacy_concentration_transition"
    ):
        current_portfolio_action = (
            item.get(
                "current_portfolio_action"
            )
            or "NONE"
        )

        current_portfolio_reason = str(
            item.get(
                "current_portfolio_reason"
            )
            or ""
        ).strip()

        parts = [
            (
                f"AI ændrede aktievurderingen fra "
                f"{item['previous_action']} til "
                f"{item['current_action']}, mens "
                f"AI-score var uændret."
            ),
            (
                "Det tidligere REDUCE var drevet af "
                "porteføljekoncentration og ikke af "
                "en svagere aktievurdering."
            ),
        ]

        if (
            current_portfolio_action
            == "DIVERSIFY"
        ):
            parts.append(
                "Koncentrationsrisikoen håndteres "
                "nu separat som DIVERSIFY."
            )

            if current_portfolio_reason:
                parts.append(
                    current_portfolio_reason
                )

        else:
            parts.append(
                "Koncentrationsrisiko og "
                "aktiesignal vurderes nu separat."
            )

        parts.extend([
            (
                "Ny aktievurdering: "
                f"{item['current_reason']}"
            ),
            (
                "Signalstabilitet: "
                f"{item['stability']}."
            ),
            (
                "Historiske ændringer: "
                f"{item['change_count']}."
            ),
        ])

        return " ".join(
            str(part).strip()
            for part in parts
            if str(part).strip()
        )

    if score_change > 0:
        score_text = (
            f"AI-score steg med "
            f"{score_change:.1f} point."
        )

    elif score_change < 0:
        score_text = (
            f"AI-score faldt med "
            f"{abs(score_change):.1f} point."
        )

    else:
        score_text = (
            "AI-score var uændret."
        )

    parts = [
        (
            f"AI ændrede vurderingen fra "
            f"{item['previous_action']} til "
            f"{item['current_action']}."
        ),
        score_text,
        (
            "Tidligere vurdering: "
            f"{item['previous_reason']}"
        ),
        (
            "Ny vurdering: "
            f"{item['current_reason']}"
        ),
        (
            "Signalstabilitet: "
            f"{item['stability']}."
        ),
        (
            "Historiske ændringer: "
            f"{item['change_count']}."
        ),
    ]

    return " ".join(
        str(part).strip()
        for part in parts
        if str(part).strip()
    )
