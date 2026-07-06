from combined_score_service import combined_stock_score
from openai_service import client


def get_market_summary():
    data = combined_stock_score(client)
    ranking = data.get("combined_ranking", [])

    top_items = ranking[:5]
    weak_items = [item for item in ranking if item.get("combined_score", 0) < 50]

    top_text = ", ".join(
        f"{item.get('stock')} ({item.get('combined_score')})"
        for item in top_items
    )

    weak_text = ", ".join(
        f"{item.get('stock')} ({item.get('combined_score')})"
        for item in weak_items[:3]
    ) or "ingen tydelige svage aktier"

    return (
        f"De stærkeste aktier lige nu er {top_text}. "
        f"De svageste signaler ses ved {weak_text}. "
        "Markedet vurderes samlet ud fra teknisk score og AI-nyhedsscore."
    )