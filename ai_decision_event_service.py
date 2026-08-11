from collections import defaultdict
from datetime import datetime

from ai_portfolio_decision_service import load_portfolio_decisions


DATE_FORMAT = "%d-%m-%Y %H:%M"


def get_decision_events():
    """
    Omdanner gentagne portfolio snapshots til reelle
    beslutningsevents.

    Et nyt event opstår kun, når action ændres for en aktie.
    """

    history = load_portfolio_decisions()

    last_action = {}
    events_by_stock = defaultdict(list)

    for snapshot in history:
        date = snapshot.get("date")

        for decision in snapshot.get("decisions", []):
            stock = decision.get("stock")
            action = decision.get("action")

            if not stock or not action:
                continue

            previous_action = last_action.get(stock)

            if previous_action != action:
                events_by_stock[stock].append({
                    "date": date,
                    "stock": stock,
                    "from_action": previous_action,
                    "action": action,
                    "score": decision.get("score"),
                    "decision_price": decision.get(
                        "decision_price"
                    ),
                    "weight_pct": decision.get(
                        "weight_pct"
                    ),
                    "reason": decision.get("reason"),
                })

            last_action[stock] = action

    events = []

    for stock_events in events_by_stock.values():
        events.extend(stock_events)

    return sorted(
        events,
        key=lambda item: datetime.strptime(
            item["date"],
            DATE_FORMAT,
        ),
    )


def get_closed_decision_events():
    """
    Returnerer afsluttede beslutningsevents.

    Et event lukkes, når samme aktie skifter til en ny action.
    Performance måles mellem eventets startpris og prisen
    ved næste action-skift.
    """

    events = get_decision_events()

    events_by_stock = defaultdict(list)

    for event in events:
        events_by_stock[event["stock"]].append(event)

    closed_events = []

    for stock, stock_events in events_by_stock.items():

        for index, event in enumerate(stock_events[:-1]):
            next_event = stock_events[index + 1]

            start_price = event.get("decision_price")
            end_price = next_event.get("decision_price")

            if not isinstance(start_price, (int, float)):
                continue

            if not isinstance(end_price, (int, float)):
                continue

            try:
                start_time = datetime.strptime(
                    event["date"],
                    DATE_FORMAT,
                )

                end_time = datetime.strptime(
                    next_event["date"],
                    DATE_FORMAT,
                )

            except (TypeError, ValueError):
                continue

            duration_minutes = int(
                (
                    end_time - start_time
                ).total_seconds() / 60
            )

            performance_pct = (
                (end_price - start_price)
                / start_price
            ) * 100

            closed_events.append({
                **event,
                "end_date": next_event["date"],
                "end_price": end_price,
                "next_action": next_event["action"],
                "duration_minutes": duration_minutes,
                "performance_pct": round(
                    performance_pct,
                    2,
                ),
            })

    return sorted(
        closed_events,
        key=lambda item: datetime.strptime(
            item["date"],
            DATE_FORMAT,
        ),
    )
