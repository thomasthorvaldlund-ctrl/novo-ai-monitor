import json

from analysis_data_service import build_analysis_data
from openai_service import client
from openai_service import create_chat_completion
from ai_result_cache_service import get_cached_ai_result
from ai_result_cache_service import get_latest_cached_ai_result
from ai_result_cache_service import save_cached_ai_result

AI_ANALYST_CACHE_CONTRACT_VERSION = "ai_analyst:v1"

AI_ANALYST_EXACT_CACHE_MAX_AGE_SECONDS = 21600

AI_ANALYST_NARRATIVE_REFRESH_SECONDS = 3600


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

        cache_input = {
            "market": {
                "score": market.get("score"),
                "status": market.get("status"),
            },
            "top_picks": [
                {
                    "stock": item.get("stock"),
                    "score": item.get("score"),
                }
                for item in top_picks[:5]
            ],
            "portfolio": {
                "value": portfolio.get("value"),
                "total_return": portfolio.get("total_return"),
            },
            "alerts": [
                {
                    "title": item.get("title"),
                    "message": item.get("message"),
                }
                for item in alerts
            ],
            "summary": summary,
        }

        try:
            cached_result = get_cached_ai_result(
                service="ai_analyst",
                operation="market_briefing",
                model="gpt-4o-mini",
                prompt_contract_version=AI_ANALYST_CACHE_CONTRACT_VERSION,
                input_payload=cache_input,
                max_age_seconds=AI_ANALYST_EXACT_CACHE_MAX_AGE_SECONDS,
            )
        except Exception as e:
            print(
                "AI Analyst exact cache read error:",
                e,
            )
            cached_result = None

        if isinstance(
            cached_result,
            str,
        ):
            return cached_result

        try:
            latest_result = get_latest_cached_ai_result(
                service="ai_analyst",
                operation="market_briefing",
                model="gpt-4o-mini",
                prompt_contract_version=AI_ANALYST_CACHE_CONTRACT_VERSION,
                max_age_seconds=AI_ANALYST_NARRATIVE_REFRESH_SECONDS,
            )
        except Exception as e:
            print(
                "AI Analyst latest cache read error:",
                e,
            )
            latest_result = None

        if isinstance(
            latest_result,
            str,
        ):
            return latest_result

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

        response = create_chat_completion(
            service="ai_analyst",
            operation="market_briefing",
            instrument=None,
            route="/update-dashboard-cache",
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Du er en forsigtig og konkret aktieanalytiker."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=220,
        )

        result = response.choices[0].message.content.strip()

        if result:
            try:
                save_cached_ai_result(
                    service="ai_analyst",
                    operation="market_briefing",
                    model="gpt-4o-mini",
                    prompt_contract_version=AI_ANALYST_CACHE_CONTRACT_VERSION,
                    input_payload=cache_input,
                    result=result,
                )
            except Exception as e:
                print(
                    "AI Analyst result cache write error:",
                    e,
                )

        return result

    except Exception as e:
        print("AI Analyst error:", e)
        return fallback
