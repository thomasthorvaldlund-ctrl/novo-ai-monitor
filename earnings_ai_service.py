import json

from openai_service import client


def analyze_earnings_article(article):
    """
    AI-analyserer én regnskabsnyhed.
    """

    if client is None:
        return {
            "company": article.get("title", "Ukendt"),
            "sentiment": "Unavailable",
            "impact": "Unknown",
            "summary": "OpenAI-klient ikke tilgængelig.",
        }

    prompt = f"""
Analyser denne regnskabsnyhed.

Titel:
{article.get("title", "")}

Resume:
{article.get("summary", "")}

Svar KUN som gyldig JSON i dette format:

{{
    "company": "",
    "sentiment": "Positive | Neutral | Negative",
    "impact": "High | Medium | Low",
    "summary": ""
}}

Summary må højst være to korte sætninger.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Du er professionel aktieanalytiker med speciale "
                    "i virksomheders kvartalsregnskaber."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return {
            "company": article.get("title", "Ukendt"),
            "sentiment": "Unavailable",
            "impact": "Unknown",
            "summary": "AI returnerede et ugyldigt JSON-svar.",
        }


def analyze_earnings_articles(articles):
    """
    AI-analyserer en liste af direkte regnskabsartikler.
    """

    results = []

    for article in articles:
        analysis = analyze_earnings_article(article)

        results.append({
            "title": article.get("title", ""),
            "link": article.get("link", ""),
            "published": article.get("published", ""),
            "analysis": analysis,
        })

    return results
