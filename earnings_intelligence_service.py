import re


EARNINGS_PATTERNS = [
    r"\bearnings\b",
    r"\bquarterly results?\b",
    r"\bfinancial results?\b",
    r"\bresults for (the )?(first|second|third|fourth) quarter\b",
    r"\bq[1-4]\s+(earnings|results|report)\b",
    r"\b(first|second|third|fourth)[- ]quarter earnings\b",
    r"\b(first|second|third|fourth)[- ]quarter results\b",
    r"\brevenue (beat|miss|growth|falls?|rises?)\b",
    r"\beps (beat|miss|growth|falls?|rises?)\b",
    r"\b(raises?|cuts?|reaffirms?) guidance\b",
    r"\bguidance (raised|cut|lowered|reaffirmed)\b",
    r"\bprofit (beat|miss|growth|falls?|rises?)\b",
]


def detect_earnings_news(news_items):
    """
    Finder sandsynlige regnskabsnyheder.

    Titlen vægtes højest for at undgå falske matches fra
    HTML, tracking-links og metadata i artikel-summary.
    """

    earnings = []

    for item in news_items:
        title = item.get("title", "").strip()
        title_lower = title.lower()

        matched_patterns = [
            pattern
            for pattern in EARNINGS_PATTERNS
            if re.search(pattern, title_lower)
        ]

        if matched_patterns:
            direct_company_report = any(
                re.search(pattern, title_lower)
                for pattern in [
                    r"\bearnings beat\b",
                    r"\bearnings miss\b",
                    r"\bquarterly results?\b",
                    r"\bfinancial results?\b",
                    r"\bq[1-4]\s+(earnings|results|report)\b",
                    r"\b(raises?|cuts?|reaffirms?) guidance\b",
                    r"\bguidance (raised|cut|lowered|reaffirmed)\b",
                    r"\beps (beat|miss)\b",
                    r"\brevenue (beat|miss)\b",
                ]
            )

            earnings.append({
                **item,
                "earnings_matches": matched_patterns,
                "earnings_type": (
                    "company_report"
                    if direct_company_report
                    else "market_coverage"
                ),
            })

    return earnings


def get_earnings_summary(news_items):
    """
    Returnerer en kort opsummering af fundne regnskabsnyheder.
    """

    earnings = detect_earnings_news(news_items)

    company_reports = [
        item
        for item in earnings
        if item.get("earnings_type") == "company_report"
    ]

    market_coverage = [
        item
        for item in earnings
        if item.get("earnings_type") == "market_coverage"
    ]

    return {
        "total": len(earnings),
        "company_reports": len(company_reports),
        "market_coverage": len(market_coverage),
        "all_articles": earnings,
        "company_report_articles": company_reports,
        "market_coverage_articles": market_coverage,
        "latest_company_reports": company_reports[:5],
    }
