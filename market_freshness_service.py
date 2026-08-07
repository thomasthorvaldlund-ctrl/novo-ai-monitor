"""
Aureum AI Market Freshness Service

Vurderer hvor frisk markedsdata er
baseret på markedets status.
"""


from datetime import datetime


def get_market_data_freshness(market_status):
    """
    Returnerer datakvalitet for et marked.
    """

    if not market_status:
        return {
            "freshness": "UNKNOWN",
            "label": "Ingen data",
        }


    status = market_status.get(
        "status"
    )


    if status == "OPEN":
        return {
            "freshness": "LIVE",
            "label": "Live markedsdata",
            "checked_at": datetime.now().isoformat(),
        }


    if status in [
        "CLOSED",
        "HOLIDAY",
        "WEEKEND",
    ]:

        if status == "HOLIDAY":
            reason = "Helligdag"

        elif status == "WEEKEND":
            reason = "Weekend"

        else:
            reason = "Uden for åbningstid"


        return {
            "freshness": "LAST_CLOSE",
            "label": "Seneste officielle lukkekurs anvendes",
            "reason": reason,
            "checked_at": datetime.now().isoformat(),
        }


    return {
        "freshness": "UNKNOWN",
        "label": "Ukendt datastatus",
        "checked_at": datetime.now().isoformat(),
    }
