import json
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
from openai_service import client

import feedparser

import yfinance as yf
from stock_utils import get_history
from portfolio import get_portfolio_summary
from portfolio_manager_routes import portfolio_manager_bp
from portfolio_analysis_routes import portfolio_analysis_bp
from market_dashboard_routes import market_dashboard_bp
from watchlist_routes import watchlist_bp
from combined_score_routes import combined_score_bp
from command_center_routes import command_center_bp
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
import requests


import time

app = Flask(__name__)
from routes.system_status import system_status_bp
app.register_blueprint(system_status_bp)
app.register_blueprint(portfolio_manager_bp)
app.register_blueprint(portfolio_analysis_bp)
app.register_blueprint(market_dashboard_bp)
app.register_blueprint(watchlist_bp)
app.register_blueprint(combined_score_bp)
app.register_blueprint(command_center_bp)
app.register_blueprint(job_status_bp)
app.register_blueprint(signal_history_bp)
app.register_blueprint(ai_performance_bp)
app.register_blueprint(stock_universe_bp)

USERS = {
    "thomas": "59autoKamp19#",
    "admin": "Suramitr8267",
    "guest": "GuestSeatrout68#"
}

def check_auth(username, password):
    return username in USERS and USERS[username] == password

def require_auth():
    return Response(
        "Login required",
        401,
        {"WWW-Authenticate": 'Basic realm="Stock AI Monitor"'}
    )


@app.before_request
def before_request():
    if request.path.startswith("/static/"):
        return
    
    if request.path.startswith("/stock-universe/"):
        return

    if request.path in [
        "/test-alert",
        "/risk-check",
        "/news-check",
        "/ai-news-check",
        "/status-report",
        "/chart",
        "/dsv",
     	"/dsv-ai-news-check",
        "/dsv-chart",
        "/daily-report",
        "/smart-alerts",
	    "/save-history",
        "/stock-screener",
        "/stock-screener-page",
        "/portfolio-alerts",
        "/history",
        "/stock-news-ai-page",
        "/combined-stock-score",
        "/combined-stock-score-report",
        "/portfolio-analysis",
        "/portfolio-analysis-page",
        "/market-dashboard",
        "/system-status-page",
        "/watchlist-page",
        "/trading-signals-page",
        "/portfolio-manager-page",
        "/combined-stock-score-page",
        "/stock-news-ai-score",
        "/stock-screener-report",
        "/watchlist-page",
        "/trading-signals-page",
        "/portfolio-manager-page",
        "/combined-stock-score-page",
        "/stock-news-ai-score",
        "/stock-screener-report",
        "/history-data",
        "/portfolio-history",
        "/update-dashboard-cache",
        "/job-status",
        "/signal-history",
        "/market-score-history",
        "/command-center-v2",
        "/ai-performance",
        "/stock-universe",
        "/stock-universe-filter",
    ]:
        return

    auth = request.authorization

    if not auth or not check_auth(auth.username, auth.password):
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
    stock = yf.Ticker(ticker)
    data = stock.history(period="10d")

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

def get_fx_rates():
    """
    Henter valutakurser til DKK.
    Bruger fallback hvis yfinance fejler.
    """
    def fx(pair, fallback):
        try:
            data = yf.Ticker(pair).history(period="5d")
            return float(data["Close"].iloc[-1])
        except Exception:
            return fallback

    return {
        "DKK": 1.0,
        "USD": fx("USDDKK=X", 6.95),
        "EUR": fx("EURDKK=X", 7.46),
    }


def get_currency(ticker):
    """
    Finder aktiens handelsvaluta ud fra ticker.
    """
    if ticker.endswith(".CO"):
        return "DKK"
    if ticker.endswith(".AS"):
        return "EUR"
    return "USD"


def convert_to_dkk(price, currency, fx_rates=None):
    """
    Konverterer pris til DKK.
    """
    if fx_rates is None:
        fx_rates = get_fx_rates()

    return float(price) * fx_rates.get(currency, 1.0)


def format_dkk(amount):
    """
    Formaterer beløb pænt som DKK.
    """
    return f"{amount:,.2f} DKK".replace(",", "X").replace(".", ",").replace("X", ".")


@app.route("/")
def home():
    return redirect("/command-center-v2")

@app.route("/test-alert")
def test_alert():
    send_telegram("✅ Stock AI Monitor test-alarm virker!")
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
    stock = yf.Ticker(ticker)
    data = stock.history(period="10d")

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

    seen_file = "/root/novo-ai-monitor/seen_news.txt"

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

    with open(seen_file, "w") as f:
        for title in seen:
            f.write(title + "\n")

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
    )

@app.route("/ai-news-check")
def ai_news_check():
    feed = feedparser.parse(
        "https://news.google.com/rss/search?q=Novo+Nordisk+stock+OR+Wegovy+OR+Ozempic&hl=en-US&gl=US&ceid=US:en"
    )

    titles = [entry.title for entry in feed.entries[:8]]

    text = "\n".join(titles)

    response = client.chat.completions.create(
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

    if "Høj" in ai_text or "Kritisk" in ai_text:
        send_telegram("🧠 NOVO AI NYHEDSALARM\n\n" + ai_text)

    return {
        "checked_articles": len(titles),
        "ai_analysis": ai_text
    }

@app.route("/status-report")
def status_report():
    stock = yf.Ticker("NOVO-B.CO")
    data = stock.history(period="10d")

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

    stock = yf.Ticker("NOVO-B.CO")
    data = stock.history(period="1mo")

    plt.figure(figsize=(8,4))
    plt.plot(data.index, data["Close"])
    plt.title("Novo Nordisk B - 30 dage")
    plt.grid(True)

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(chart_file, bbox_inches="tight")
    plt.close()

    return send_file(chart_file, mimetype="image/png")

@app.route("/dsv-chart")
def dsv_chart():
    stock = yf.Ticker("DSV.CO")
    data = stock.history(period="1mo")

    plt.figure(figsize=(8,4))
    plt.plot(data.index, data["Close"])
    plt.title("DSV - 30 dage")
    plt.grid(True)

    chart_file = "/tmp/dsv_chart.png"
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(chart_file, bbox_inches="tight")
    plt.close()

    return send_file(chart_file, mimetype="image/png")

@app.route("/dsv")
def dsv_status():
    stock = yf.Ticker("DSV.CO")
    data = stock.history(period="10d")

    latest = data["Close"].iloc[-1]
    yesterday = data["Close"].iloc[-2]
    week_ago = data["Close"].iloc[-6]

    daily_change = ((latest - yesterday) / yesterday) * 100
    weekly_change = ((latest - week_ago) / week_ago) * 100

    return {
        "stock": "DSV",
        "price": round(float(latest), 2),
        "daily_change": round(float(daily_change), 2),
        "weekly_change": round(float(weekly_change), 2)
    }

@app.route("/dsv-ai-news-check")
def dsv_ai_news_check():
    feed = feedparser.parse(
        "https://news.google.com/rss/search?q=DSV+stock+OR+DSV+transport+OR+DSV+logistics&hl=en-US&gl=US&ceid=US:en"
    )

    titles = [entry.title for entry in feed.entries[:8]]
    text = "\n".join(titles)

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "Du er en forsigtig aktie- og nyhedsanalytiker. Du vurderer risiko for større fald i DSV-aktien."
            },
            {
                "role": "user",
                "content": f"""
Analyser disse nyhedsoverskrifter om DSV, transport, logistik og konkurrenter.

Svar på dansk i dette format:

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

    with open("/root/novo-ai-monitor/last_dsv_ai_news_check.log", "w") as f:
        import json
        json.dump({
            "ai_analysis": ai_text,
            "checked_articles": len(titles)
        }, f)

    if "Høj" in ai_text or "Kritisk" in ai_text:
        send_telegram("🧠 DSV AI NYHEDSALARM\n\n" + ai_text)

    return {
        "checked_articles": len(titles),
        "ai_analysis": ai_text
    }

@app.route("/daily-report")
def daily_report():
    import json

    novo_ticker = get_stock_metadata("NOVO")["ticker"]
    dsv_ticker = get_stock_metadata("DSV")["ticker"]

    novo = get_stock_data(novo_ticker)
    dsv = get_stock_data(dsv_ticker)

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

    novo_ai_risk = extract_ai_risk("/root/novo-ai-monitor/last_ai_news_check.log")
    dsv_ai_risk = extract_ai_risk("/root/novo-ai-monitor/last_dsv_ai_news_check.log")

    novo_total_risk = novo["risk_level"]
    if levels[novo_ai_risk] > levels[novo_total_risk]:
        novo_total_risk = novo_ai_risk

    dsv_total_risk = dsv["risk_level"]
    if levels[dsv_ai_risk] > levels[dsv_total_risk]:
        dsv_total_risk = dsv_ai_risk

    message = (
        "📊 DAGLIG AKTIERAPPORT\n\n"
        "NOVO\n"
        f"Kurs: {novo['price']:.2f} DKK\n"
        f"Dagsændring: {novo['daily_change']:.2f}%\n"
        f"Ugeændring: {novo['weekly_change']:.2f}%\n"
        f"Teknisk risiko: {novo['risk_level']}\n"
        f"AI-risiko: {novo_ai_risk}\n"
        f"Samlet risiko: {novo_total_risk}\n\n"
        "DSV\n"
        f"Kurs: {dsv['price']:.2f} DKK\n"
        f"Dagsændring: {dsv['daily_change']:.2f}%\n"
        f"Ugeændring: {dsv['weekly_change']:.2f}%\n"
        f"Teknisk risiko: {dsv['risk_level']}\n"
        f"AI-risiko: {dsv_ai_risk}\n"
        f"Samlet risiko: {dsv_total_risk}"
    )

    send_telegram(message)
    return {"status": "Daily report sent"}

@app.route("/smart-alerts")
def smart_alerts():
    import json
    from datetime import datetime

    state_file = "/root/novo-ai-monitor/smart_alert_state.json"
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
            "ai_log": "/root/novo-ai-monitor/last_ai_news_check.log",
        },
        {
            "name": "DSV",
            "ticker": get_stock_metadata("DSV")["ticker"],
            "ai_log": "/root/novo-ai-monitor/last_dsv_ai_news_check.log",
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

    with open(state_file, "w") as f:
        json.dump(state, f)

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
        ("NOVO", "/root/novo-ai-monitor/last_ai_news_check.log"),
        ("DSV", "/root/novo-ai-monitor/last_dsv_ai_news_check.log"),
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

        with open("/root/novo-ai-monitor/history.csv", "a", newline="") as f:
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
        with open("history.csv", newline="") as csvfile:
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

    try:
        with open("/root/novo-ai-monitor/history.csv", "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception:
        rows = []

    table_rows = ""

    for row in rows[-30:]:
        table_rows += f"""
        <tr>
            <td>{row.get('date')}</td>
            <td>{row.get('stock')}</td>
            <td>{row.get('price')}</td>
            <td>{row.get('technical_risk')}</td>
            <td>{row.get('ai_risk')}</td>
            <td>{row.get('total_risk')}</td>
        </tr>
        """

    return f"""
    <html>
    <head>
        <title>Historik</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #eef2f7;
                padding: 40px;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                background: white;
            }}
            th, td {{
                padding: 12px;
                border-bottom: 1px solid #ddd;
                text-align: left;
            }}
            th {{
                background: #111827;
                color: white;
            }}
        </style>
    </head>
    <body>
        <h1>📈 Aktiehistorik</h1>
        <table>
            <tr>
                <th>Dato</th>
                <th>Aktie</th>
                <th>Kurs</th>
                <th>Teknisk risiko</th>
                <th>AI-risiko</th>
                <th>Samlet risiko</th>
            </tr>
            {table_rows}
        </table>
    </body>
    </html>
    """


@app.route("/dashboard")
def dashboard():
    df = pd.read_csv("history.csv")
    return render_template(
        "dashboard.html",
        tables=[df.tail(20).to_html(classes="data", index=False)]
    )

@app.route("/history-chart")
def history_chart():
    df = pd.read_csv("history.csv")

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

@app.route("/portfolio-alerts")
def portfolio_alerts():
    today = datetime.now().strftime("%Y-%m-%d")
    sent_file = "/root/novo-ai-monitor/portfolio_alerts_sent.txt"

    try:
        with open(sent_file, "r") as f:
            sent_today = set(line.strip() for line in f.readlines())
    except FileNotFoundError:
        sent_today = set()

    stock = yf.Ticker("NOVO-B.CO")
    data = stock.history(period="10d")
    latest = data["Close"].iloc[-1]

    dsv = yf.Ticker("DSV.CO")
    dsv_data = dsv.history(period="10d")
    dsv_latest = dsv_data["Close"].iloc[-1]

    novo_buy_price = 301.3
    dsv_buy_price = 1588.5

    novo_profit_pct = ((latest - novo_buy_price) / novo_buy_price) * 100
    dsv_profit_pct = ((dsv_latest - dsv_buy_price) / dsv_buy_price) * 100

    alerts = []

    if novo_profit_pct <= -5:
        alert_key = f"{today}-NOVO-minus5"
        msg = f"⚠️ NOVO er {novo_profit_pct:.2f}% under købskursen. Kurs: {latest:.2f} DKK"
        if alert_key not in sent_today:
            send_telegram(msg)
            alerts.append(msg)
            with open(sent_file, "a") as f:
                f.write(alert_key + "\n")

    if dsv_profit_pct <= -5:
        alert_key = f"{today}-DSV-minus5"
        msg = f"⚠️ DSV er {dsv_profit_pct:.2f}% under købskursen. Kurs: {dsv_latest:.2f} DKK"
        if alert_key not in sent_today:
            send_telegram(msg)
            alerts.append(msg)
            with open(sent_file, "a") as f:
                f.write(alert_key + "\n")

    return {"status": "portfolio alerts checked", "alerts": alerts}
    
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
    cache_file = "/root/novo-ai-monitor/stock_news_ai_cache.json"
    cache_seconds = 21600

    if os.path.exists(cache_file) and time.time() - os.path.getmtime(cache_file) < cache_seconds:
        with open(cache_file, "r") as f:
            return json.load(f)

    watchlist = {
        "NOVO": "Novo Nordisk stock Wegovy Ozempic",
        "DSV": "DSV stock transport logistics",
        "VESTAS": "Vestas stock wind energy",
        "GENMAB": "Genmab stock biotech",
        "CARLSBERG": "Carlsberg stock beverage",
        "MAERSK": "Maersk stock shipping logistics",
        "ORSTED": "Orsted stock renewable energy",
        "PANDORA": "Pandora stock jewelry",
        "APPLE": "Apple stock",
        "MICROSOFT": "Microsoft stock AI cloud",
        "NVIDIA": "Nvidia stock AI chips",
        "ASML": "ASML stock semiconductors",
        "TESLA": "Tesla stock electric vehicles",
        "AMAZON": "Amazon stock cloud ecommerce",
        "META": "Meta stock AI advertising",
        "GOOGLE": "Alphabet Google stock AI cloud"
    }

    results = []

    for stock_name, query in watchlist.items():
        try:
            feed = feedparser.parse(
                f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
            )

            titles = [entry.title for entry in feed.entries[:5]]
            text = "\n".join(titles)

            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Du er en forsigtig aktieanalytiker. Giv ikke direkte køb/salg-råd. Vurder kun nyhedssentiment og risiko."
                    },
                    {
                        "role": "user",
                        "content": f"""
Analyser nyhedsoverskrifterne for {stock_name}.

Giv svar på dansk i dette format:

Nyhedsscore: 0-100
Sentiment: Meget positiv / Positiv / Neutral / Negativ / Meget negativ

Kort forklaring:
Maks 3 linjer.

Vigtigste positive signaler:
- 
- 

Vigtigste negative signaler:
- 
- 

Kortsigtet vurdering 1-3 måneder:
Bullish / Neutral / Bearish

Langsigtet vurdering 1-5 år:
Bullish / Neutral / Bearish

Risikofaktorer:
- 
- 

Mulige katalysatorer:
- 
- 

Samlet AI-vurdering:
Stærk kandidat / Kandidat / Neutral / Svag kandidat

Overskrifter:
{text}
"""
                    }
                ]
            )

            ai_text = response.choices[0].message.content

            score = 50
            for line in ai_text.splitlines():
                if "Nyhedsscore" in line:
                    digits = "".join(ch for ch in line if ch.isdigit())
                    if digits:
                        score = int(digits[:3])
                        score = max(0, min(score, 100))

            results.append({
                "stock": stock_name,
                "news_score": score,
                "ai_analysis": ai_text,
                "headlines": titles
            })

        except Exception as e:
            results.append({
                "stock": stock_name,
                "error": str(e)
            })

    results = sorted(results, key=lambda x: x.get("news_score", 0), reverse=True)

    output = {"news_ai_scores": results}

    with open(cache_file, "w") as f:
        json.dump(output, f)

    return output


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

    build_dashboard_cache()

    return {"status": "dashboard cache updated"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
    
