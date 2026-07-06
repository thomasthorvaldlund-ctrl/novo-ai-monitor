from combined_score_service import combined_stock_score
from openai_service import client


def get_ai_analyst():
    data = combined_stock_score(client)
    ranking = data.get("combined_ranking", [])

    if not ranking:
        return "Ingen markedsdata er tilgængelige."

    best = ranking[0]

    return (
        f"AI vurderer markedet som overvejende positivt. "
        f"Den stærkeste aktie lige nu er {best['stock']} "
        f"med en Combined Score på {best['combined_score']}."
    )