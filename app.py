import json
import hmac
from pathlib import Path
from aureum_paths import data_path, log_path, state_path
from urllib.parse import quote_plus
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt
import csv
import matplotlib

from flask import (
    Flask,
    send_file,
    render_template,
    jsonify,
    request,
    Response,
    redirect,
)

from combined_score_service import (
    combined_stock_score as service_combined_score
)
from ai_decision_service import get_ai_decision
from dashboard_cache_service import load_dashboard_cache
matplotlib.use("Agg")

import os
from werkzeug.security import check_password_hash
from openai_service import client
from openai_service import create_chat_completion
from ai_result_cache_service import get_cached_ai_result
from ai_result_cache_service import save_cached_ai_result

import feedparser

from market_data_provider import get_history as provider_get_history
from currency_service import (
    get_fx_rates,
    get_currency,
    convert_to_dkk,
)
from stock_utils import get_history
from portfolio import get_portfolio_summary
from admin_account_routes import admin_accounts_bp
from deep_ai_settings_routes import deep_ai_settings_bp
from portfolio_manager_routes import portfolio_manager_bp
from portfolio_settings_routes import portfolio_settings_bp
from market_dashboard_routes import market_dashboard_bp
from watchlist_routes import watchlist_bp
from combined_score_routes import combined_score_bp
from command_center_routes import command_center_bp
from backup_routes import backup_bp
from stock_screener_service import (
    stock_screener as service_stock_screener,
)
from stock_news_service import stock_news_ai_score as service_stock_news_ai_score
from job_status_routes import job_status_bp
from job_status_routes import job_status_bp
from signal_history_routes import signal_history_bp
from ai_performance_routes import ai_performance_bp
from stock_universe_routes import stock_universe_bp
from stock_universe_service import (
    get_active_stocks,
    get_news_query,
    get_stock_metadata,
)
from stock_news_cache_builder import build_stock_news_ai_cache
from user_identity_service import (
    get_optional_current_user_id,
)
import requests


import time

app = Flask(__name__)
from routes.system_status import system_status_bp

from private_login_service import (
    configure_private_login,
    get_authenticated_session_user_id,
    is_private_login_path,
    private_login_required,
)
app.register_blueprint(system_status_bp)
app.register_blueprint(admin_accounts_bp)
app.register_blueprint(deep_ai_settings_bp)
app.register_blueprint(portfolio_manager_bp)
app.register_blueprint(portfolio_settings_bp)
app.register_blueprint(market_dashboard_bp)
app.register_blueprint(watchlist_bp)
app.register_blueprint(combined_score_bp)
app.register_blueprint(command_center_bp)
app.register_blueprint(job_status_bp)
app.register_blueprint(signal_history_bp)
app.register_blueprint(ai_performance_bp)
app.register_blueprint(stock_universe_bp)
app.register_blueprint(backup_bp)

AUTH_HASH_ENV_VARS = {
    "thomas": "AUREUM_AUTH_THOMAS_HASH",
    "admin": "AUREUM_AUTH_ADMIN_HASH",
    "guest": "AUREUM_AUTH_GUEST_HASH",
}

USERS = {
    username: os.getenv(env_name, "").strip()
    for username, env_name in AUTH_HASH_ENV_VARS.items()
}

missing_auth_users = [
    username
    for username, password_hash in USERS.items()
    if not password_hash
]

if missing_auth_users:
    raise RuntimeError(
        "Missing Aureum AI authentication hashes for: "
        + ", ".join(missing_auth_users)
    )


def check_auth(username, password):
    password_hash = USERS.get(username)

    if not password_hash or not password:
        return False

    return check_password_hash(
        password_hash,
        password,
    )


configure_private_login(
    app,
    credential_checker=check_auth,
)


def require_auth():
    return private_login_required()


INTERNAL_JOB_PATHS = frozenset({
    "/risk-check",
    "/news-check",
    "/ai-news-check",
    "/status-report",
    "/daily-report",
    "/smart-alerts",
    "/save-history",
    "/combined-stock-score",
    "/combined-stock-score-report",
    "/update-dashboard-cache",
    "/update-stock-news-ai-cache",
    "/update-stock-screener-cache",
})

INTERNAL_JOB_TOKEN_HEADER = "X-Aureum-Job-Token"

INTERNAL_JOB_TOKEN = os.getenv(
    "AUREUM_INTERNAL_JOB_TOKEN",
    "",
).strip()

if not INTERNAL_JOB_TOKEN:
    raise RuntimeError(
        "Missing AUREUM_INTERNAL_JOB_TOKEN."
    )


def _has_valid_internal_job_token():
    supplied_token = request.headers.get(
        INTERNAL_JOB_TOKEN_HEADER,
        "",
    )

    if not supplied_token:
        return False

    return hmac.compare_digest(
        supplied_token,
        INTERNAL_JOB_TOKEN,
    )


@app.before_request
def before_request():
    if request.path.startswith("/static/"):
        return

    if is_private_login_path():
        return

    if (
        request.path in INTERNAL_JOB_PATHS
        and _has_valid_internal_job_token()
    ):
        return

    if (
        get_authenticated_session_user_id()
        is not None
    ):
        return

    auth = request.authorization

    if auth and check_auth(
        auth.username,
        auth.password,
    ):
        if (
            get_optional_current_user_id()
            is not None
        ):
            return

    return require_auth()


BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = "8532274659"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })

def get_stock_data(ticker):
    data = provider_get_history(
        ticker,
        period="10d",
    )

    if data.empty or "Close" not in data.columns:
        raise ValueError(f"Ingen kursdata fundet for {ticker}")

    close_prices = data["Close"].dropna()

    if len(close_prices) < 6:
        raise ValueError(
            f"For få gyldige kurspunkter for {ticker}: {len(close_prices)}"
        )

    latest = float(close_prices.iloc[-1])
    yesterday = float(close_prices.iloc[-2])
    week_ago = float(close_prices.iloc[-6])

    daily_change = ((latest - yesterday) / yesterday) * 100
    weekly_change = ((latest - week_ago) / week_ago) * 100

    score = 0

    if daily_change <= -2:
        score += 15
    if daily_change <= -4:
        score += 25
    if weekly_change <= -5:
        score += 20
    if weekly_change <= -8:
        score += 30

    if score < 30:
        risk_level = "Lav"
        color = "green"
    elif score < 60:
        risk_level = "Moderat"
        color = "orange"
    elif score < 80:
        risk_level = "Høj"
        color = "red"
    else:
        risk_level = "Kritisk"
        color = "darkred"

    return {
        "price": latest,
        "daily_change": daily_change,
        "weekly_change": weekly_change,
        "score": score,
        "risk_level": risk_level,
        "color": color
    }


# =========================
# V3.6.1 Currency Engine
# =========================







def format_dkk(amount):
    """
    Formaterer beløb pænt som DKK.
    """
    return f"{amount:,.2f} DKK".replace(",", "X").replace(".", ",").replace("X", ".")


@app.route("/")
def home():
    return redirect("/command-center")

@app.route("/test-alert")
def test_alert():
    send_telegram("✅ Aureum AI test-alarm virker!")
    return {"status": "Telegram test sent"}

@app.route("/risk-check")
def risk_check():
    selected_stock = request.args.get("stock", "NOVO").upper()

    stock_metadata = get_stock_metadata(selected_stock)

    if stock_metadata is None:
        selected_stock = "NOVO"
        stock_metadata = get_stock_metadata(selected_stock)

    ticker = stock_metadata["ticker"]
    currency = get_currency(ticker)
    data = provider_get_history(
        ticker,
        period="10d",
    )

    latest = data["Close"].iloc[-1]
    yesterday = data["Close"].iloc[-2]
    week_ago = data["Close"].iloc[-6]
    daily_change = ((latest - yesterday) / yesterday) * 100
    weekly_change = ((latest - week_ago) / week_ago) * 100

    alarm_sent = False
    reasons = []

    if daily_change <= -4:
        alarm_sent = True
        reasons.append(f"Dagsfald: {daily_change:.2f}%")

    if weekly_change <= -8:
        alarm_sent = True
        reasons.append(f"Ugefald: {weekly_change:.2f}%")

    if alarm_sent:
        message = (
            f"🚨 {selected_stock} RISIKOALARM 🚨\n"
            "Risiko: HØJ\n\n"
            + "\n".join(reasons)
        )
        send_telegram(message)

    dashboard_cache = load_dashboard_cache()
    combined_item = next(
        (
            item
            for item in dashboard_cache.get("combined_ranking", [])
            if item.get("stock") == selected_stock
        ),
        None,
    )

    combined_score = combined_item.get("combined_score", 0) if combined_item else 0
    ai_decision = get_ai_decision(combined_score)

    return render_template(
        "risk_check.html",
        stock=selected_stock,
        ticker=ticker,
        watchlist=get_active_stocks(),
        selected_stock=selected_stock,
        price=round(float(latest), 2),
        currency=currency,
        daily_change=round(float(daily_change), 2),
        weekly_change=round(float(weekly_change), 2),
        alarm_sent=alarm_sent,
        reasons=reasons,
        combined_score=combined_score,
        ai_signal=ai_decision.get("signal"),
        technical_score=combined_item.get("technical_score", 0) if combined_item else 0,
        news_score=combined_item.get("news_score", 0) if combined_item else 0,
        ai_rating=combined_item.get("rating", "Ingen vurdering") if combined_item else "Ingen vurdering",
        ai_analysis=combined_item.get("ai_analysis", "Ingen AI-analyse tilgængelig.") if combined_item else "Ingen AI-analyse tilgængelig.",

        ai_confidence=ai_decision.get("confidence"),
        ai_risk=ai_decision.get("risk"),
        ai_comment=ai_decision.get("comment"),

        updated_at=datetime.now().strftime("%d-%m-%Y %H:%M"),
    )

@app.route("/news-check")
def news_check():

    selected_stock = request.args.get("stock", "NOVO").upper()

    stock_metadata = get_stock_metadata(selected_stock)

    if stock_metadata is None:
        selected_stock = "NOVO"
        stock_metadata = get_stock_metadata(selected_stock)

    # News Check finder artikler for alle aktive aktier,
    # mens den fulde AI-sentimentanalyse kun findes for
    # det aktuelle Deep AI-nyhedsudvalg.
    from stock_news_service import stock_news_ai_score
    from deep_ai_selection_service import (
        get_effective_deep_ai_stocks,
    )

    deep_ai_user_id = (
        get_optional_current_user_id()
    )

    deep_ai_user_ids = (
        [deep_ai_user_id]
        if deep_ai_user_id
        else []
    )

    deep_ai_news_stocks = {
        str(stock).strip().upper()
        for stock in get_effective_deep_ai_stocks(
            user_ids=deep_ai_user_ids,
        )
    }

    is_deep_ai_news_stock = (
        selected_stock
        in deep_ai_news_stocks
    )

    news_ai_cache = stock_news_ai_score(
        None
    )

    news_ai_rows = news_ai_cache.get(
        "news_ai_scores",
        [],
    )

    news_ai_item = next(
        (
            item
            for item in news_ai_rows
            if isinstance(item, dict)
            and str(
                item.get("stock", "")
            ).strip().upper()
            == selected_stock
        ),
        None,
    )

    valid_news_ai_item = (
        isinstance(news_ai_item, dict)
        and isinstance(
            news_ai_item.get("news_score"),
            int,
        )
        and not isinstance(
            news_ai_item.get("news_score"),
            bool,
        )
        and 0
        <= news_ai_item.get("news_score")
        <= 100
        and isinstance(
            news_ai_item.get("ai_analysis"),
            str,
        )
        and bool(
            news_ai_item.get(
                "ai_analysis",
                "",
            ).strip()
        )
        and not news_ai_item.get("error")
    )

    if (
        is_deep_ai_news_stock
        and valid_news_ai_item
    ):
        news_analysis_status = "full"
    elif is_deep_ai_news_stock:
        news_analysis_status = "unavailable"
    else:
        news_analysis_status = "limited"

    seen_file = state_path("seen_news.txt")

    try:
        with open(seen_file, "r") as f:
            seen = set(line.strip() for line in f.readlines())
    except:
        seen = set()

    query = get_news_query(selected_stock)

    feed_url = (
        "https://news.google.com/rss/search?"
        f"q={quote_plus(query)}"
        "&hl=en-US&gl=US&ceid=US:en"
    )

    feed = feedparser.parse(feed_url)

    negative_words = [
        "falls", "drops", "lawsuit", "warning", "cuts",
        "misses", "pressure", "competition", "decline",
        "risk", "probe", "investigation", "side effects",
        "Eli Lilly", "price war"
    ]

    negative_articles = []
    new_negative_articles = []
    articles = []

    for entry in feed.entries[:10]:
        title = entry.get("title", "")
        title_lower = title.lower()

        article = {
            "title": title,
            "link": entry.get("link", ""),
            "published": entry.get("published", ""),
        }
        articles.append(article)

        is_negative = any(
            word.lower() in title_lower
            for word in negative_words
        )

        if is_negative:
            negative_articles.append(article)

            if title not in seen:
                new_negative_articles.append(article)
                seen.add(title)

    if new_negative_articles:
        message = (
            f"📰 {selected_stock} NYHEDSALARM\n"
            "Nyt muligt negativt nyhedssignal:\n\n"
            + "\n\n".join(
                item.get("title", "")
                for item in new_negative_articles[:5]
            )
        )
        send_telegram(message)

    seen_temp_file = Path(seen_file).with_suffix(
        Path(seen_file).suffix + ".tmp"
    )

    with open(
        seen_temp_file,
        "w",
        encoding="utf-8"
    ) as f:
        for title in seen:
            f.write(title + "\n")

        f.flush()
        os.fsync(f.fileno())

    seen_temp_file.replace(
        seen_file
    )

    return render_template(
        "news_check.html",
        checked_articles=len(articles),
        articles=articles,
        negative_matches=negative_articles[:5],
        new_negative_matches=new_negative_articles[:5],
        alarm_sent=bool(new_negative_articles),
        updated_at=datetime.now().strftime("%d-%m-%Y %H:%M"),
        watchlist=get_active_stocks(),
        selected_stock=selected_stock,
        query=query,
        news_analysis_status=news_analysis_status,
        news_ai_score=(
            news_ai_item.get("news_score")
            if valid_news_ai_item
            else None
        ),
        news_ai_analysis=(
            news_ai_item.get("ai_analysis")
            if valid_news_ai_item
            else ""
        ),
        deep_ai_news_count=len(
            deep_ai_news_stocks
        ),
    )

AI_NEWS_CHECK_CACHE_CONTRACT_VERSION = "ai_news_check:v1"


@app.route("/ai-news-check")
def ai_news_check():
    feed = feedparser.parse(
        "https://news.google.com/rss/search?q=Novo+Nordisk+stock+OR+Wegovy+OR+Ozempic&hl=en-US&gl=US&ceid=US:en"
    )

    titles = [entry.title for entry in feed.entries[:8]]

    text = "\n".join(titles)

    cache_input = {
        "instrument": "NOVO",
        "headlines": sorted(titles),
    }

    try:
        cached_ai_text = get_cached_ai_result(
            service="ai_news_check",
            operation="novo_news_risk",
            model="gpt-4.1-mini",
            prompt_contract_version=AI_NEWS_CHECK_CACHE_CONTRACT_VERSION,
            input_payload=cache_input,
        )
    except Exception as exc:
        print(
            "AI News Check exact cache read error:",
            exc,
        )
        cached_ai_text = None

    valid_cached_ai_text = (
        isinstance(
            cached_ai_text,
            str,
        )
        and bool(
            cached_ai_text.strip()
        )
    )

    if valid_cached_ai_text:
        ai_text = cached_ai_text

    else:
        response = create_chat_completion(
            service="ai_news_check",
            operation="novo_news_risk",
            instrument="NOVO",
            route="/ai-news-check",
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Du er en forsigtig aktie- og nyhedsanalytiker. Du vurderer risiko for større fald i Novo Nordisk aktien."
                },
                {
                    "role": "user",
                    "content": f"""
Analyser disse nyhedsoverskrifter om Novo Nordisk, Wegovy, Ozempic og konkurrenter.

Giv svar på dansk i dette format:

Risiko: Lav / Moderat / Høj / Kritisk
Kort forklaring:
Vigtigste negative signaler:
Vigtigste positive signaler:

Overskrifter:
{text}
"""
                }
            ]
        )

        ai_text = response.choices[0].message.content

        if ai_text.strip():
            try:
                save_cached_ai_result(
                    service="ai_news_check",
                    operation="novo_news_risk",
                    model="gpt-4.1-mini",
                    prompt_contract_version=AI_NEWS_CHECK_CACHE_CONTRACT_VERSION,
                    input_payload=cache_input,
                    result=ai_text,
                )
            except Exception as exc:
                print(
                    "AI News Check result cache write error:",
                    exc,
                )

    novo_ai_news_file = log_path(
        "last_ai_news_check.log"
    )

    temp_novo_ai_news_file = novo_ai_news_file.with_suffix(
        novo_ai_news_file.suffix + ".tmp"
    )

    with open(
        temp_novo_ai_news_file,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            {
                "ai_analysis": ai_text,
                "checked_articles": len(titles)
            },
            f,
            ensure_ascii=False,
        )

        f.flush()
        os.fsync(f.fileno())

    temp_novo_ai_news_file.replace(
        novo_ai_news_file
    )

    if "Høj" in ai_text or "Kritisk" in ai_text:
        send_telegram("🧠 NOVO AI NYHEDSALARM\n\n" + ai_text)

    return {
        "checked_articles": len(titles),
        "ai_analysis": ai_text
    }

@app.route("/status-report")
def status_report():
    ticker = get_stock_metadata("NOVO")["ticker"]
    data = provider_get_history(
        ticker,
        period="10d",
    )

    latest = data["Close"].iloc[-1]
    yesterday = data["Close"].iloc[-2]
    week_ago = data["Close"].iloc[-6]

    daily_change = ((latest - yesterday) / yesterday) * 100
    weekly_change = ((latest - week_ago) / week_ago) * 100

    score = 0
    reasons = []

    if daily_change <= -2:
        score += 15
        reasons.append(f"Dagsfald: {daily_change:.2f}%")

    if daily_change <= -4:
        score += 25
        reasons.append("Kraftigt dagsfald")

    if weekly_change <= -5:
        score += 20
        reasons.append(f"Ugefald: {weekly_change:.2f}%")

    if weekly_change <= -8:
        score += 30
        reasons.append("Kraftigt ugefald")

    feed = feedparser.parse(
        "https://news.google.com/rss/search?q=Novo+Nordisk+stock+OR+Wegovy+OR+Ozempic&hl=en-US&gl=US&ceid=US:en"
    )

    negative_words = [
        "falls", "drops", "lawsuit", "warning", "cuts",
        "misses", "pressure", "competition", "decline",
        "risk", "probe", "investigation", "side effects",
        "Eli Lilly", "price war"
    ]

    news_matches = []

    for entry in feed.entries[:10]:
        title = entry.title
        if any(word.lower() in title.lower() for word in negative_words):
            news_matches.append(title)

    if news_matches:
        score += min(len(news_matches) * 10, 30)
        reasons.append(f"{len(news_matches)} negative nyhedssignaler")

    score = min(score, 100)

    if score < 30:
        risk_level = "Lav"
    elif score < 60:
        risk_level = "Moderat"
    elif score < 80:
        risk_level = "Høj"
    else:
        risk_level = "Kritisk"

    message = (
        "📊 NOVO AI STATUS\n\n"
        f"Kurs: {latest:.2f}\n"
        f"Dagsændring: {daily_change:.2f}%\n"
        f"Ugeændring: {weekly_change:.2f}%\n\n"
        f"Samlet risiko: {risk_level}\n"
        f"Score: {score}/100\n\n"
        "Årsager:\n"
        + ("\n".join(reasons) if reasons else "Ingen store faresignaler")
    )

    send_telegram(message)

    return {
        "price": round(float(latest), 2),
        "daily_change": round(float(daily_change), 2),
        "weekly_change": round(float(weekly_change), 2),
        "risk_level": risk_level,
        "score": score,
        "reasons": reasons,
        "news_matches": news_matches[:5]
    }

@app.route("/chart")
def chart():
    chart_file = "/tmp/novo_chart.png"

    ticker = get_stock_metadata("NOVO")["ticker"]
    data = provider_get_history(
        ticker,
        period="1mo",
    )

    plt.figure(figsize=(8,4))
    plt.plot(data.index, data["Close"])
    plt.title("Novo Nordisk B - 30 dage")
    plt.grid(True)

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(chart_file, bbox_inches="tight")
    plt.close()

    return send_file(chart_file, mimetype="image/png")




@app.route("/daily-report")
def daily_report():
    import json

    novo_ticker = get_stock_metadata("NOVO")["ticker"]
    novo = get_stock_data(novo_ticker)

    def extract_ai_risk(path):
        try:
            with open(path, "r") as f:
                text = json.load(f).get("ai_analysis", "")
        except Exception:
            text = ""

        if "Risiko: Kritisk" in text:
            return "Kritisk"
        if "Risiko: Høj" in text:
            return "Høj"
        if "Risiko: Moderat" in text:
            return "Moderat"
        return "Lav"

    levels = {"Lav": 1, "Moderat": 2, "Høj": 3, "Kritisk": 4}

    novo_ai_risk = extract_ai_risk(
        log_path("last_ai_news_check.log")
    )

    novo_total_risk = novo["risk_level"]
    if levels[novo_ai_risk] > levels[novo_total_risk]:
        novo_total_risk = novo_ai_risk

    message = (
        "📊 DAGLIG AKTIERAPPORT\n\n"
        "NOVO\n"
        f"Kurs: {novo['price']:.2f} DKK\n"
        f"Dagsændring: {novo['daily_change']:.2f}%\n"
        f"Ugeændring: {novo['weekly_change']:.2f}%\n"
        f"Teknisk risiko: {novo['risk_level']}\n"
        f"AI-risiko: {novo_ai_risk}\n"
        f"Samlet risiko: {novo_total_risk}"
    )

    send_telegram(message)
    return {"status": "Daily report sent"}

@app.route("/smart-alerts")
def smart_alerts():
    import json
    from datetime import datetime

    state_file = state_path(
        "smart_alert_state.json"
    )
    today = datetime.now().strftime("%Y-%m-%d")

    try:
        with open(state_file, "r") as f:
            state = json.load(f)
    except Exception:
        state = {}

    def extract_ai_risk(path):
        try:
            with open(path, "r") as f:
                text = json.load(f).get("ai_analysis", "")
        except Exception:
            text = ""

        if "Risiko: Kritisk" in text:
            return "Kritisk"
        if "Risiko: Høj" in text:
            return "Høj"
        if "Risiko: Moderat" in text:
            return "Moderat"
        return "Lav"

    levels = {"Lav": 1, "Moderat": 2, "Høj": 3, "Kritisk": 4}

    stocks = [
        {
            "name": "NOVO",
            "ticker": get_stock_metadata("NOVO")["ticker"],
            "ai_log": log_path("last_ai_news_check.log"),
        },
    ]

    alerts = []

    for item in stocks:
        data = get_stock_data(item["ticker"])
        ai_risk = extract_ai_risk(item["ai_log"])

        total_risk = data["risk_level"]
        if levels[ai_risk] > levels[total_risk]:
            total_risk = ai_risk

        alert_key = f"{item['name']}_{today}"

        if alert_key not in state:
            should_alert = False
            reasons = []

            if data["daily_change"] <= -3:
                should_alert = True
                reasons.append(f"Dagsfald: {data['daily_change']:.2f}%")

            if data["weekly_change"] <= -7:
                should_alert = True
                reasons.append(f"Ugefald: {data['weekly_change']:.2f}%")

            if total_risk in ["Høj", "Kritisk"]:
                should_alert = True
                reasons.append(f"Samlet risiko: {total_risk}")

            if should_alert:
                message = (
                    f"🚨 SMART AKTIEALARM - {item['name']}\n\n"
                    f"Kurs: {data['price']:.2f} DKK\n"
                    f"Dagsændring: {data['daily_change']:.2f}%\n"
                    f"Ugeændring: {data['weekly_change']:.2f}%\n\n"
                    f"Teknisk risiko: {data['risk_level']}\n"
                    f"AI-risiko: {ai_risk}\n"
                    f"Samlet risiko: {total_risk}\n\n"
                    "Årsager:\n"
                    + "\n".join(reasons)
                )

                send_telegram(message)
                alerts.append(message)
                state[alert_key] = True

    temp_state_file = state_file.with_suffix(
        state_file.suffix + ".tmp"
    )

    with open(
        temp_state_file,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            state,
            f,
            ensure_ascii=False,
        )

        f.flush()
        os.fsync(f.fileno())

    temp_state_file.replace(
        state_file
    )

    return {
        "alerts_sent": len(alerts),
        "alerts": alerts
    }

@app.route("/save-history")
def save_history():
    import csv
    import json
    from datetime import datetime

    def extract_ai_risk(path):
        try:
            with open(path, "r") as f:
                text = json.load(f).get("ai_analysis", "")
        except:
            text = ""

        if "Risiko: Kritisk" in text:
            return "Kritisk"
        elif "Risiko: Høj" in text:
            return "Høj"
        elif "Risiko: Moderat" in text:
            return "Moderat"
        return "Lav"

    levels = {"Lav": 1, "Moderat": 2, "Høj": 3, "Kritisk": 4}

    today = datetime.now().strftime("%Y-%m-%d")

    for stock_name, logfile in [
        ("NOVO", log_path("last_ai_news_check.log")),
        ("NVIDIA", None),
        ("ASML", None),
    ]:
        ticker = get_stock_metadata(stock_name)["ticker"]

        data = get_stock_data(ticker)

        if logfile:
            ai_risk = extract_ai_risk(logfile)
        else:
            ai_risk = data["risk_level"]

        total_risk = data["risk_level"]
        if levels[ai_risk] > levels[total_risk]:
            total_risk = ai_risk

        with open(data_path("history.csv"), "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                today,
                stock_name,
                round(data["price"], 2),
                data["risk_level"],
                ai_risk,
                total_risk
            ])

    return {"status": "history saved"}

@app.route("/history-data")
def history_data():
    stock = request.args.get("stock", "NOVO")

    daily_data = {}

    try:
        with open(data_path("history.csv"), newline="") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                if row["stock"] != stock:
                    continue

                # Overskriver samme dato, så den sidste måling for dagen bevares
                daily_data[row["date"]] = {
                    "date": row["date"],
                    "price": float(row["price"]),
                    "technical_risk": row["technical_risk"],
                    "ai_risk": row["ai_risk"],
                    "total_risk": row["total_risk"],
                }

    except FileNotFoundError:
        return jsonify([])

    data = list(daily_data.values())
    data.sort(key=lambda x: x["date"])

    return jsonify(data)

@app.route("/history")
def history():
    import csv

    rows = []
    error_message = None

    try:
        with open(
            data_path("history.csv"),
            "r",
            encoding="utf-8",
            newline="",
        ) as history_file:
            reader = csv.DictReader(
                history_file
            )
            rows = list(reader)

    except (OSError, csv.Error):
        error_message = (
            "Historikdata kunne ikke indlæses."
        )

    return render_template(
        "history.html",
        rows=rows[-30:],
        history_count=len(rows),
        error_message=error_message,
    )


@app.route("/dashboard")
def dashboard():
    df = pd.read_csv(data_path("history.csv"))
    return render_template(
        "dashboard.html",
        tables=[df.tail(20).to_html(classes="data", index=False)]
    )

@app.route("/history-chart")
def history_chart():
    df = pd.read_csv(data_path("history.csv"))

    novo = df[df["stock"] == "NOVO"]
    dsv = df[df["stock"] == "DSV"]

    plt.figure(figsize=(10,5))
    plt.plot(novo.index, novo["price"], label="NOVO")
    plt.plot(dsv.index, dsv["price"], label="DSV")
    plt.legend()
    plt.grid()

    chart_file = "/tmp/history_chart.png"
    plt.savefig(chart_file)
    plt.close()

    return send_file(chart_file, mimetype="image/png")

    
@app.route("/stock-screener")
def stock_screener_route():
    return service_stock_screener() 
    
@app.route("/stock-screener-report")
def stock_screener_report():
    data = service_stock_screener()
    ranking = data.get("ranking", [])[:3]

    message = "📈 Dagens Aktie Screener Top 3\n\n"

    for i, item in enumerate(ranking, start=1):
        message += (
            f"{i}. {item.get('stock')}\n"
            f"Kurs: {item.get('price')}\n"
            f"Ugeændring: {item.get('weekly_change')}%\n"
            f"Score: {item.get('score')}/100\n\n"
        )

    message += "Dette er teknisk screening og ikke finansiel rådgivning."

    send_telegram(message)

    return {"status": "screener report sent", "top3": ranking}

@app.route("/stock-screener-page")
def stock_screener_page():
    data = service_stock_screener()
    ranking = data.get("ranking", [])

    rows = ""
    for item in ranking:
        if "error" in item:
            rows += f"""
            <tr>
                <td>{item.get('stock')}</td>
                <td colspan="6">Fejl: {item.get('error')}</td>
            </tr>
            """
            continue

        score = item.get("score", 0)
        color = "green" if score >= 60 else "orange" if score >= 45 else "red"

        rows += f"""
        <tr>
            <td><b>{item.get('stock')}</b></td>
            <td>{item.get('price')} DKK</td>
            <td>{item.get('original_price')} {item.get('currency')}</td>
            <td>{item.get('currency')}</td>
            <td>{item.get('weekly_change')}%</td>
            <td style="color:{color}; font-weight:bold;">{score}/100</td>
            <td>{"Interessant" if score >= 60 else "Neutral" if score >= 45 else "Svag"}</td>
        </tr>
        """

    return f"""
    <html>
    <head>
        <title>Aktie Screener</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #eef2f7;
                padding: 40px;
            }}
            .container {{
                max-width: 1100px;
                margin: auto;
            }}
            h1 {{
                color: #111827;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
                border-radius: 14px;
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(0,0,0,0.08);
            }}
            th {{
                background: #111827;
                color: white;
                padding: 14px;
                text-align: left;
            }}
            td {{
                padding: 14px;
                border-bottom: 1px solid #e5e7eb;
            }}
            .note {{
                margin-top: 20px;
                color: #6b7280;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📈 Aktie Screener V2.1</h1>
            <table>
                <tr>
                    <th>Aktie</th>
                    <th>Kurs (DKK)</th>
                    <th>Original kurs</th>
                    <th>Valuta</th>
                    <th>Ugeændring</th>
                    <th>Score</th>
                    <th>AI-hint</th>
                </tr>
                {rows}
            </table>
            <div class="note">
                Dette er en teknisk screening og ikke finansiel rådgivning.
            </div>
        </div>
    </body>
    </html>
    """


@app.route("/stock-news-ai-score")
def stock_news_ai_score():
    return service_stock_news_ai_score(client)


@app.route("/update-stock-news-ai-cache")
def update_stock_news_ai_cache():
    return build_stock_news_ai_cache(client)


@app.route("/stock-news-ai-page")
def stock_news_ai_page():
    data = stock_news_ai_score()
    scores = data.get("news_ai_scores", [])

    rows = ""
    for item in scores:
        if "error" in item:
            rows += f"""
            <tr>
                <td>{item.get('stock')}</td>
                <td colspan="6">Fejl: {item.get('error')}</td>
            </tr>
            """
            continue

        score = item.get("news_score", 0)
        color = "green" if score >= 75 else "orange" if score >= 60 else "red"

        rows += f"""
        <tr>
            <td><b>{item.get('stock')}</b></td>
            <td style="color:{color}; font-weight:bold;">{score}/100</td>
            <td><pre>{item.get('ai_analysis')}</pre></td>
        </tr>
        """

    return f"""
    <html>
    <head>
        <title>AI Nyhedsranking</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #eef2f7;
                padding: 40px;
            }}
            .container {{
                max-width: 1200px;
                margin: auto;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
                border-radius: 14px;
                overflow: hidden;
            }}
            th {{
                background: #111827;
                color: white;
                padding: 14px;
                text-align: left;
            }}
            td {{
                padding: 14px;
                border-bottom: 1px solid #e5e7eb;
                vertical-align: top;
            }}
            pre {{
                white-space: pre-wrap;
                font-family: Arial, sans-serif;
                margin: 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧠 AI Nyhedsranking V2.4.1</h1>
            <table>
                <tr>
                    <th>Aktie</th>
                    <th>Nyhedsscore</th>
                    <th>AI-analyse</th>
                </tr>
                {rows}
            </table>
            <p>Dette er AI-baseret nyhedsscreening og ikke finansiel rådgivning.</p>
        </div>
    </body>
    </html>
    """
    
@app.route("/combined-stock-score")
def combined_stock_score():
    tech_data = service_stock_screener()
    news_data = stock_news_ai_score()

    tech_map = {
        item.get("stock"): item
        for item in tech_data.get("ranking", [])
        if "stock" in item
    }

    news_map = {
        item.get("stock"): item
        for item in news_data.get("news_ai_scores", [])
        if "stock" in item
    }

    results = []

    for stock_name, tech_item in tech_map.items():
        news_item = news_map.get(stock_name, {})

        technical_score = tech_item.get("score", 0)
        news_score = news_item.get("news_score", 50)

        combined_score = round((technical_score * 0.6) + (news_score * 0.4), 2)

        if combined_score >= 75:
            rating = "Stærk kandidat"
        elif combined_score >= 60:
            rating = "Kandidat"
        elif combined_score >= 45:
            rating = "Neutral"
        else:
            rating = "Svag kandidat"

        results.append({
            "stock": stock_name,
            "price": tech_item.get("price"),
            "original_price": tech_item.get("original_price"),
            "currency": tech_item.get("currency"),
            "weekly_change": tech_item.get("weekly_change"),
            "technical_score": technical_score,
            "news_score": news_score,
            "combined_score": combined_score,
            "rating": rating,
            "ai_analysis": news_item.get("ai_analysis", "")
        })

    results = sorted(results, key=lambda x: x.get("combined_score", 0), reverse=True)

    return {"combined_ranking": results}


@app.route("/combined-stock-score-page")
def combined_stock_score_page():
    data = combined_stock_score()
    ranking = data.get("combined_ranking", [])

    rows = ""
    for i, item in enumerate(ranking, start=1):
        score = item.get("combined_score", 0)
        color = "green" if score >= 75 else "orange" if score >= 60 else "red"

        rows += f"""
        <tr>
            <td>{i}</td>
            <td><b>{item.get('stock')}</b></td>
            <td>{item.get('price')} DKK</td>
            <td>{item.get('original_price')} {item.get('currency')}</td>
            <td>{item.get('currency')}</td>
            <td style="color:{color}; font-weight:bold;">{score}/100</td>
            <td>{item.get('technical_score')}/100</td>
            <td>{item.get('news_score')}/100</td>
            <td>{item.get('weekly_change')}%</td>
            <td><b>{item.get('rating')}</b></td>
        </tr>
        """

    return f"""
    <html>
    <head>
        <title>AI Investeringsranking</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #eef2f7;
                padding: 40px;
            }}
            .container {{
                max-width: 1200px;
                margin: auto;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
                border-radius: 14px;
                overflow: hidden;
            }}
            th {{
                background: #111827;
                color: white;
                padding: 14px;
                text-align: left;
            }}
            td {{
                padding: 14px;
                border-bottom: 1px solid #e5e7eb;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏆 AI Investeringsranking V2.6.1</h1>
            <table>
                <tr>
                    <th>Rang</th>
                    <th>Aktie</th>
                    <th>Kurs (DKK)</th>
                    <th>Original kurs</th>
                    <th>Valuta</th>
                    <th>Samlet score</th>
                    <th>Teknisk score</th>
                    <th>AI nyhedsscore</th>
                    <th>Ugeændring</th>
                    <th>Vurdering</th>
                </tr>
                {rows}
            </table>
            <p>Samlet score = 60% teknisk score + 40% AI-nyhedsscore. Ikke finansiel rådgivning.</p>
        </div>
    </body>
    </html>
    """


@app.route("/combined-stock-score-report")
def combined_stock_score_report():
    data = combined_stock_score()
    ranking = data.get("combined_ranking", [])

    top5 = ranking[:5]

    msg = "🏆 DAGLIG AI INVESTERINGSRAPPORT\n\n"

    for i, item in enumerate(top5, start=1):
        msg += (
            f"{i}. {item['stock']}\n"
            f"Samlet score: {item['combined_score']}/100\n"
            f"Vurdering: {item['rating']}\n"
            f"Teknisk: {item['technical_score']}/100\n"
            f"AI nyheder: {item['news_score']}/100\n\n"
        )

    msg += "Dette er AI-baseret analyse og ikke finansiel rådgivning."

    send_telegram(msg)

    return {
        "status": "screener report sent",
        "top5": top5
    }

@app.route("/watchlist-page")
def watchlist_page():
    data = combined_stock_score()
    ranking = data.get("combined_ranking", [])

    rows = ""
    for item in ranking:
        score = item.get("combined_score", 0)
        color = "green" if score >= 75 else "orange" if score >= 60 else "red"

        rows += f"""
        <tr>
            <td><b>{item.get('stock')}</b></td>
            <td>{item.get('price')} DKK</td>
            <td>{item.get('original_price')} {item.get('currency')}</td>
            <td>{item.get('currency')}</td>
            <td>{item.get('weekly_change')}%</td>
            <td>{item.get('technical_score')}/100</td>
            <td>{item.get('news_score')}/100</td>
            <td style="color:{color}; font-weight:bold;">{score}/100</td>
            <td><b>{item.get('rating')}</b></td>
        </tr>
        """

    return f"""
    <html>
    <head>
        <title>AI Watchlist</title>
        <style>
            body {{ font-family: Arial, sans-serif; background:#eef2f7; padding:40px; }}
            .container {{ max-width:1200px; margin:auto; }}
            table {{ width:100%; border-collapse:collapse; background:white; border-radius:14px; overflow:hidden; }}
            th {{ background:#111827; color:white; padding:14px; text-align:left; }}
            td {{ padding:14px; border-bottom:1px solid #e5e7eb; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⭐ AI Watchlist V3.3</h1>
            <table>
                <tr>
                    <th>Aktie</th>
                    <th>Kurs (DKK)</th>
                    <th>Original kurs</th>
                    <th>Valuta</th>
                    <th>Ugeændring</th>
                    <th>Teknisk</th>
                    <th>AI nyheder</th>
                    <th>Samlet score</th>
                    <th>Vurdering</th>
                </tr>
                {rows}
            </table>
            <p>Dette er AI-baseret watchlist og ikke finansiel rådgivning.</p>
        </div>
    </body>
    </html>
    """


@app.route("/trading-signals-page")
def trading_signals_page():
    data = combined_stock_score()
    ranking = data.get("combined_ranking", [])

    rows = ""

    for item in ranking:
        score = item.get("combined_score", 0)
        weekly = item.get("weekly_change", 0)

        if score >= 75 and weekly >= 0:
            signal = "KØB"
            confidence = "Høj"
            color = "green"
        elif score >= 60:
            signal = "HOLD / KANDIDAT"
            confidence = "Moderat"
            color = "orange"
        elif score >= 45:
            signal = "OBS"
            confidence = "Lav"
            color = "orange"
        else:
            signal = "SÆLG / UNDGÅ"
            confidence = "Lav"
            color = "red"

        rows += f"""
        <tr>
            <td><b>{item.get('stock')}</b></td>
            <td>{item.get('price')} DKK</td>
            <td>{item.get('original_price')} {item.get('currency')}</td>
            <td>{item.get('currency')}</td>
            <td>{weekly}%</td>
            <td>{item.get('technical_score')}/100</td>
            <td>{item.get('news_score')}/100</td>
            <td>{score}/100</td>
            <td style="color:{color}; font-weight:bold;">{signal}</td>
            <td>{confidence}</td>
        </tr>
        """

    return f"""
    <html>
    <head>
        <title>AI Trading Signals</title>
        <style>
            body {{ font-family: Arial, sans-serif; background:#eef2f7; padding:40px; }}
            .container {{ max-width:1200px; margin:auto; }}
            .card {{ background:white; padding:24px; border-radius:14px; margin-bottom:20px; box-shadow:0 10px 30px rgba(0,0,0,0.08); }}
            table {{ width:100%; border-collapse:collapse; background:white; border-radius:14px; overflow:hidden; }}
            th {{ background:#111827; color:white; padding:14px; text-align:left; }}
            td {{ padding:14px; border-bottom:1px solid #e5e7eb; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚦 AI Købs-/Salgssignaler V3.4</h1>

            <div class="card">
                <p><b>Regler:</b></p>
                <p>KØB = samlet score ≥ 75 og positiv ugeudvikling</p>
                <p>HOLD / KANDIDAT = samlet score ≥ 60</p>
                <p>OBS = samlet score 45-59</p>
                <p>SÆLG / UNDGÅ = samlet score under 45</p>
            </div>

            <table>
                <tr>
                    <th>Aktie</th>
                    <th>Kurs (DKK)</th>
                    <th>Original kurs</th>
                    <th>Valuta</th>
                    <th>Ugeændring</th>
                    <th>Teknisk</th>
                    <th>AI nyheder</th>
                    <th>Samlet score</th>
                    <th>Signal</th>
                    <th>Tillid</th>
                </tr>
                {rows}
            </table>

            <p>Dette er AI-baserede signaler og ikke finansiel rådgivning.</p>
        </div>
    </body>
    </html>
    """

@app.route("/update-dashboard-cache")
def update_dashboard_cache():
    from dashboard_cache_builder import build_dashboard_cache
    from dashboard_cache_service import save_dashboard_cache

    data = build_dashboard_cache()
    save_dashboard_cache(data)

    return {"status": "dashboard cache updated"}

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3000)
