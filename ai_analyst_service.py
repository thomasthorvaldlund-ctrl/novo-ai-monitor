import json

from analysis_data_service import build_analysis_data
from openai_service import client

def build_fallback_analysis(ranking):
    top_3 = ranking[:3]
    weak = [item for item in ranking if item.get("combined_score", 0) < 50]

    top_text = ", ".join(
        f"{item.get('stock')} ({item.get('combined_score')})"
        for item in top_3
    )

    risk_text = ", ".join(
        f"{item.get('stock')} ({item.get('combined_score')})"
        for item in weak[:3]
    ) or "ingen tydelige svage kandidater"

    return (
        f"AI Analyst vurderer markedet som moderat positivt. "
        f"De stærkeste kandidater er {top_text}. "
        f"De største svaghedstegn ses ved {risk_text}. "
        f"Fokus bør være på aktier med høj Combined Score og lav nyhedsrisiko."
    )


def get_ai_analyst():
    analysis = build_analysis_data()
    ranking = analysis["ranking"]

    if not ranking:
        return "Ingen markedsdata er tilgængelige."

    fallback = build_fallback_analysis(ranking)

    if client is None:
        return fallback
    
    try:
        market = analysis.get("market", {})
        portfolio = analysis.get("portfolio", {})
        alerts = analysis.get("alerts", [])
        top_picks = analysis.get("top_picks", [])
        summary = analysis.get("summary", "")

        top_picks_text = "\n".join(
            f"- {item.get('stock')} ({item.get('score')})"
            for item in top_picks[:5]
        )

        alerts_text = "\n".join(
            f"- {item.get('title')}: {item.get('message')}"
            for item in alerts
        )

        prompt = f"""
Du er en kortfattet dansk AI-aktieanalytiker.

Market Score:
{market.get("score")}/100 ({market.get("status")})

Top Picks:
{top_picks_text}

Portfolio:
Værdi: {portfolio.get("value")}
Afkast: {portfolio.get("total_return")}

AI Alerts:
{alerts_text}

Market Summary:
{summary}

Opgave:
Skriv en professionel markedsbriefing på dansk.
Maks 5 sætninger.
Ingen investeringsgaranti. Ingen lange forbehold.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Du er en forsigtig og konkret aktieanalytiker."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=220,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("AI Analyst error:", e)
        return fallback
