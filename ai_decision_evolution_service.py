import json
from pathlib import Path
from collections import defaultdict


DECISION_FILE = Path(
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

    stocks = defaultdict(list)

    for snapshot in history:

        for decision in snapshot.get("decisions", []):

            stocks[decision["stock"]].append(
                {
                    "date": snapshot["date"],
                    "action": decision["action"],
                    "score": decision["score"],
                    "reason": decision["reason"],
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

                    "changed_at": new["date"],
                    "change_count": len(changes),

                    "stability": calculate_stability(
                        len(changes)
                    )
                }
                )

    for item in results:
        item["explanation"] = generate_evolution_explanation(item)

    return results

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


    return (
        f"AI ændrede vurderingen fra "
        f"{item['previous_action']} til "
        f"{item['current_action']}. "
        f"{score_text} "
        f"Tidligere vurdering: "
        f"{item['previous_reason']} "
        f"Ny vurdering: "
        f"{item['current_reason']} "
        f"Signalstabilitet: "
        f"{item['stability']}. "
        f"Historiske ændringer: "
        f"{item['change_count']}."
    )
