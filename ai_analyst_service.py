from combined_score_service import combined_stock_score
from openai_service import client

def build_analysis_data():
    data = combined_stock_score(client)
    ranking = data.get("combined_ranking", [])

    return {
        "ranking": ranking,
        "count": len(ranking),
    }
    
def get_ai_analyst():
    analysis = build_analysis_data()

    ranking = analysis["ranking"]

    if not ranking:
        return "Ingen markedsdata er tilgængelige."

    top_3 = ranking[:3]
    weak = [item for item in ranking if item.get("combined_score", 0) < 50]

    top_text = ", ".join(
        f"{item.get('stock')} ({item.get('combined_score')})"
        for item in top_3
    )

    if weak:
        risk_text = ", ".join(
            f"{item.get('stock')} ({item.get('combined_score')})"
            for item in weak[:3]
        )
    else:
        risk_text = "ingen tydelige svage kandidater"

    return (
        f"AI Analyst vurderer markedet som moderat positivt. "
        f"De stærkeste kandidater er {top_text}. "
        f"De største svaghedstegn ses ved {risk_text}. "
        f"Fokus bør være på aktier med høj Combined Score og lav nyhedsrisiko."
    )