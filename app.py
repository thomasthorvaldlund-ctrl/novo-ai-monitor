import json
from urllib.parse import quote_plus
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt
from flask import send_file, render_template

from flask import request, Response

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from flask import send_file

import os
from openai import OpenAI

import feedparser

from flask import Flask
import yfinance as yf
from stock_utils import get_history
import requests

import os
import time

app = Flask(__name__)

USERS = {
    "thomas": "84autoKamp19#",
    "admin": "Suramitr2627",
    "guest": "GuestSeatrout59#"
}

def check_auth(username, password):
    return username in USERS and USERS[username] == password

def require_auth():
    return Response(
        "Login required",
        401,
        {"WWW-Authenticate": 'Basic realm="Novo AI Monitor"'}
    )


@app.before_request
def before_request():
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
    ]:
        return

    auth = request.authorization

    if not auth or not check_auth(auth.username, auth.password):
        return require_auth()

BOT_TOKEN = "8860628701:AAFQuL3nUBkL_eVCVDhnjJzbOahqfFOhKhU"
CHAT_ID = "8532274659"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })

def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="10d")

    latest = data["Close"].iloc[-1]
    yesterday = data["Close"].iloc[-2]
    week_ago = data["Close"].iloc[-6]

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
    stock = yf.Ticker("NOVO-B.CO")
    data = stock.history(period="10d")

    latest = data["Close"].iloc[-1]
    yesterday = data["Close"].iloc[-2]
    week_ago = data["Close"].iloc[-6]

    daily_change = ((latest - yesterday) / yesterday) * 100
    weekly_change = ((latest - week_ago) / week_ago) * 100

    dsv = yf.Ticker("DSV.CO")
    dsv_data = dsv.history(period="10d")

    dsv_latest = dsv_data["Close"].iloc[-1]
    dsv_yesterday = dsv_data["Close"].iloc[-2]
    dsv_week_ago = dsv_data["Close"].iloc[-6]

    dsv_daily_change = ((dsv_latest - dsv_yesterday) / dsv_yesterday) * 100
    dsv_weekly_change = ((dsv_latest - dsv_week_ago) / dsv_week_ago) * 100
    novo_qty = 23
    novo_buy_price = 301.3
    novo_value = latest * novo_qty
    novo_cost = novo_buy_price * novo_qty
    novo_profit = novo_value - novo_cost
    novo_profit_pct = (novo_profit / novo_cost) * 100

    dsv_qty = 4
    dsv_buy_price = 1588.5
    dsv_value = dsv_latest * dsv_qty
    dsv_cost = dsv_buy_price * dsv_qty
    dsv_profit = dsv_value - dsv_cost
    dsv_profit_pct = (dsv_profit / dsv_cost) * 100

    total_cost = novo_cost + dsv_cost
    total_value = novo_value + dsv_value
    total_profit = novo_profit + dsv_profit
    total_profit_pct = (total_profit / total_cost) * 100
    novo_profit_color = "green" if novo_profit >= 0 else "red"
    dsv_profit_color = "green" if dsv_profit >= 0 else "red"
    portfolio_profit_color = "green" if total_profit >= 0 else "red"



    dsv_score = 0

    if dsv_daily_change <= -2:
        dsv_score += 15
    if dsv_daily_change <= -4:
        dsv_score += 25
    if dsv_weekly_change <= -5:
        dsv_score += 20
    if dsv_weekly_change <= -8:
        dsv_score += 30

    if dsv_score < 30:
        dsv_risk_level = "Lav"
        dsv_color = "green"
    elif dsv_score < 60:
        dsv_risk_level = "Moderat"
        dsv_color = "orange"
    elif dsv_score < 80:
        dsv_risk_level = "Høj"
        dsv_color = "red"
    else:
        dsv_risk_level = "Kritisk"
        dsv_color = "darkred"

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

    import json

    try:
        with open("/root/novo-ai-monitor/last_ai_news_check.log", "r") as f:
            data = json.load(f)
            ai_status = data.get("ai_analysis", "Ingen analyse")
    except Exception:
        ai_status = "Ingen AI-analyse endnu."

    try:
        with open("/root/novo-ai-monitor/last_dsv_ai_news_check.log", "r") as f:
            dsv_data = json.load(f)
            dsv_ai_status = dsv_data.get("ai_analysis", "Ingen DSV-analyse")
    except Exception:
        dsv_ai_status = "Ingen DSV AI-analyse endnu."

    ai_risk = "Lav"
    if "Risiko: Kritisk" in ai_status:
        ai_risk = "Kritisk"
    elif "Risiko: Høj" in ai_status:
        ai_risk = "Høj"
    elif "Risiko: Moderat" in ai_status:
        ai_risk = "Moderat"

    dsv_ai_risk = "Lav"
    if "Risiko: Kritisk" in dsv_ai_status:
        dsv_ai_risk = "Kritisk"
    elif "Risiko: Høj" in dsv_ai_status:
        dsv_ai_risk = "Høj"
    elif "Risiko: Moderat" in dsv_ai_status:
        dsv_ai_risk = "Moderat"

    levels = {"Lav": 1, "Moderat": 2, "Høj": 3, "Kritisk": 4}

    novo_total_risk = risk_level
    if levels[ai_risk] > levels[risk_level]:
        novo_total_risk = ai_risk

    dsv_total_risk = dsv_risk_level
    if levels[dsv_ai_risk] > levels[dsv_risk_level]:
        dsv_total_risk = dsv_ai_risk


    # Dynamiske porteføljekort fra portfolio.csv
    dashboard_portfolio_cards = ""

    try:
        import csv
        fx_rates = get_fx_rates()

        with open("/root/novo-ai-monitor/portfolio.csv", "r") as f:
            reader = csv.DictReader(f)

            for row in reader:
                stock_name = row["stock"]
                ticker = row["ticker"]
                qty = float(row["qty"])
                buy_price = float(row["buy_price"])

                price_data = yf.Ticker(ticker).history(period="10d")
                latest_price = float(price_data["Close"].iloc[-1])

                currency = get_currency(ticker)
                latest_dkk = convert_to_dkk(latest_price, currency, fx_rates)
                buy_price_dkk = convert_to_dkk(buy_price, currency, fx_rates)

                value_dkk = latest_dkk * qty
                cost_dkk = buy_price_dkk * qty
                profit_dkk = value_dkk - cost_dkk
                profit_pct = (profit_dkk / cost_dkk) * 100 if cost_dkk else 0
                profit_color = "green" if profit_dkk >= 0 else "red"

                dashboard_portfolio_cards += f"""
                <div class="card">
                    <div class="title">📌 {stock_name}</div>
                    <p class="metric">Ticker: <b>{ticker}</b></p>
                    <p class="metric">Aktuel kurs: <b>{latest_price:.2f} {currency}</b></p>
                    <p class="metric">Aktuel kurs DKK: <b>{latest_dkk:.2f} DKK</b></p>
                    <p class="metric">Beholdning: <b>{qty} stk.</b></p>
                    <p class="metric">Markedsværdi: <b>{value_dkk:.2f} DKK</b></p>
                    <p class="metric">Gevinst/tab: <b style="color:{profit_color};">{profit_dkk:.2f} DKK ({profit_pct:.2f}%)</b></p>
                </div>
                """

    except Exception as e:
        dashboard_portfolio_cards = f"""
        <div class="card">
            <div class="title">⚠️ Portfolio fejl</div>
            <p class="metric">{e}</p>
        </div>
        """

    return f"""
    <html>
    <head>
        <title>Aktie AI Monitor</title>
        <meta http-equiv="refresh" content="300">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
                background: #eef2f7;
                margin: 0;
                color: #111827;
            }}
            .container {{
                max-width: 1180px;
                margin: auto;
            }}
            .header {{
                margin-bottom: 24px;
            }}
            .header h1 {{
                font-size: 34px;
                margin: 0;
            }}
            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
                gap: 20px;
            }}
            .card {{
                background: white;
                padding: 26px;
                border-radius: 18px;
                box-shadow: 0 8px 24px rgba(15,23,42,0.08);
            }}
            .title {{
                font-size: 26px;
                font-weight: 800;
                margin-bottom: 18px;
            }}
            .metric {{
                font-size: 18px;
                margin: 10px 0;
            }}
            .risk {{
                font-size: 30px;
                font-weight: 900;
                margin-top: 20px;
            }}
            .charts {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }}
            .charts img {{
                width: 100%;
                border-radius: 14px;
                background: white;
            }}
            .ai-box {{
                white-space: pre-wrap;
                background: #f8fafc;
                padding: 20px;
                border-radius: 14px;
                line-height: 1.6;
                font-size: 15px;
            }}
            .links {{
                display: flex;
                flex-wrap: wrap;
                gap: 15px;
                margin-top: 30px;
                justify-content: center;
            }}
            .links a {{
                background: white;
                padding: 12px 20px;
                border-radius: 10px;
                text-decoration: none;
                font-weight: bold;
                color: #2563eb;
                box-shadow: 0 4px 10px rgba(0,0,0,0.08);
                transition: all 0.2s ease;
            }}
            .links a:hover {{
                transform: translateY(-2px);
                background: #2563eb;
                color: white;
            }}
        </style>
    </head>
    <body>
            <div class="card" style="margin-bottom:20px;">
                <div class="title">💼 Samlet portefølje</div>
                <p class="metric">Samlet investeret: <b>{total_cost:.2f} DKK</b></p>
                <p class="metric">Aktuel værdi: <b>{total_value:.2f} DKK</b></p>
                <p class="metric">Samlet gevinst/tab: <b>{total_profit:.2f} DKK ({total_profit_pct:.2f}%)</b></p>
            </div>

        <div class="container">
            <div class="card" style="margin-bottom:20px;">
                <div class="title">💼 Porteføljeoversigt</div>
                <p class="metric">Samlet værdi: <b>{total_value:.2f} DKK</b></p>
                <p class="metric">Samlet gevinst/tab: <b style="color:{portfolio_profit_color};">{total_profit:.2f} DKK ({total_profit_pct:.2f}%)</b></p>
            </div>

            <div class="grid" style="margin-top:20px;">
                {dashboard_portfolio_cards}
            </div>

            <div class="header">
                <h1>📊 Aktie AI Monitor V3.6.2</h1>
            </div>

            <div class="grid">
                <div class="card">
                    <div class="title">📊 Novo AI Monitor</div>
                    <p class="metric">Aktuel kurs: <b>{latest:.2f} DKK</b></p>
                    <p class="metric">Dagsændring: <b>{daily_change:.2f}%</b></p>
                    <p class="metric">Ugeændring: <b>{weekly_change:.2f}%</b></p>
                    <hr>
                    <p class="metric">Beholdning: <b>{novo_qty} stk.</b></p>
                    <p class="metric">Købskurs: <b>{novo_buy_price:.2f} DKK</b></p>
                    <p class="metric">Markedsværdi: <b>{novo_value:.2f} DKK</b></p>
                    <p class="metric">Gevinst/tab: <b>{novo_profit:.2f} DKK ({novo_profit_pct:.2f}%)</b></p>
                <div class="risk" style="color:{color};">
                    <p class="metric">Teknisk score: <b>{score}/100</b></p>
    		    Teknisk risiko: {risk_level}<br>
                    AI-risiko: {ai_risk}<br>
                    Samlet risiko: {novo_total_risk}
		</div>
                </div>

                <div class="card">
                    <div class="title">🚚 DSV AI Monitor</div>
                    <p class="metric">Aktuel kurs: <b>{dsv_latest:.2f} DKK</b></p>
                    <p class="metric">Dagsændring: <b>{dsv_daily_change:.2f}%</b></p>
                    <p class="metric">Ugeændring: <b>{dsv_weekly_change:.2f}%</b></p>
                    <hr>
                    <p class="metric">Beholdning: <b>{dsv_qty} stk.</b></p>
                    <p class="metric">Købskurs: <b>{dsv_buy_price:.2f} DKK</b></p>
                    <p class="metric">Markedsværdi: <b>{dsv_value:.2f} DKK</b></p>
                    <p class="metric">Gevinst/tab: <b>{dsv_profit:.2f} DKK ({dsv_profit_pct:.2f}%)</b></p>
                    <p class="metric">Teknisk score: <b>{dsv_score}/100</b></p>
                <div class="risk" style="color:{dsv_color};">
                    Teknisk risiko: {dsv_risk_level}<br>
    		    AI-risiko: {dsv_ai_risk}<br>
    		    Samlet risiko: {dsv_total_risk}
		</div>
                </div>
            </div>

            <div class="charts">
                <div class="card"><a href="/chart" target="_blank" style="font-size:22px; font-weight:bold;">Åbn NOVO-graf</a></div>
                <div class="card"><a href="/dsv-chart" target="_blank" style="font-size:22px; font-weight:bold;">Åbn DSV-graf</a></div>
            </div>

            <div class="grid" style="margin-top:20px;">
                <div class="card">
                    <div class="title">🧠 Novo AI-status</div>
                    <div class="ai-box">{ai_status}</div>
                </div>

                <div class="card">
                    <div class="title">🚚 DSV AI-status</div>
                    <div class="ai-box">{dsv_ai_status}</div>
                </div>
            </div>

            <div class="grid" style="margin-top:20px;">
                <div class="card">
                    <div class="title">📈 AI Aktie Screener</div>
                    <p class="metric">Se dagens tekniske aktie-ranking med danske og udenlandske aktier.</p>
                    <a href="/stock-screener-page" style="font-size:22px; font-weight:bold;">Åbn Aktie Screener</a>
                </div>

                <div class="card">
                    <div class="title">🧠 AI Nyhedsranking</div>
                    <p class="metric">Detaljeret AI-analyse af aktier baseret på nyheder.</p>
                    <a href="/stock-news-ai-page" style="font-size:22px; font-weight:bold;">Åbn AI Nyhedsranking</a>
                </div>

                <div class="card">
                    <div class="title">🏆 AI Investeringsranking</div>
                    <p class="metric">Samlet ranking baseret på teknisk score og AI-nyhedsscore.</p>
                    <a href="/combined-stock-score-page" style="font-size:22px; font-weight:bold;">Åbn AI Investeringsranking</a>
                </div>

                <div class="card">
                    <div class="title">💼 Portfolio Manager</div>
                    <p class="metric">Se beholdninger, værdi, gevinst/tab og vægt fra portfolio.csv.</p>
                    <a href="/portfolio-manager-page" style="font-size:22px; font-weight:bold;">Åbn Portfolio Manager</a>
                </div>

            <div class="card">
                    <div class="title">💼 Porteføljeanalyse</div>
                    <p class="metric">Se fordeling, risiko og diversificering i din portefølje.</p>
                    <a href="/portfolio-analysis-page" style="font-size:22px; font-weight:bold;">Åbn Porteføljeanalyse</a>
                </div>
            </div>

            <div class="card" style="margin-top:20px;">
                <div class="title">🌍 Global Market Dashboard</div>
                <p class="metric">Se S&P 500, Nasdaq, OMXC25, DAX og samlet markedssignal.</p>
                <a href="/market-dashboard" style="font-size:22px; font-weight:bold;">Åbn Global Market Dashboard</a>
            </div>

            <div class="links">
                <a href="/">📊 Dashboard</a>
                <a href="/stock-screener-page">📈 Aktie Screener</a>
                <a href="/stock-news-ai-page">🧠 AI Nyhedsranking</a>
                <a href="/combined-stock-score-page">🏆 AI Investeringsranking</a>
                <a href="/portfolio-manager-page">💼 Portfolio Manager</a>
                <a href="/portfolio-analysis-page">💼 Porteføljeanalyse</a>
                <a href="/market-dashboard">🌍 Global Market Dashboard</a>
                <a href="/trading-signals-page">🚦 AI Signaler</a>
                <a href="/watchlist-page">⭐ AI Watchlist</a>
                <a href="/system-status-page">⚙️ Systemstatus</a>
                <a href="/test-alert">📲 Test Telegram</a>
           </div>
        </div>
    </body>
    </html>

    """

@app.route("/test-alert")
def test_alert():
    send_telegram("✅ Novo AI Monitor test-alarm virker!")
    return {"status": "Telegram test sent"}

@app.route("/risk-check")
def risk_check():
    stock = yf.Ticker("NOVO-B.CO")
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
            "🚨 NOVO RISIKOALARM 🚨\n"
            "Risiko: HØJ\n\n"
            + "\n".join(reasons)
        )
        send_telegram(message)

    return {
        "stock": "Novo Nordisk",
        "price": round(float(latest), 2),
        "daily_change": round(float(daily_change), 2),
        "weekly_change": round(float(weekly_change), 2),
        "alarm_sent": alarm_sent,
        "reasons": reasons
    }

@app.route("/news-check")
def news_check():

    seen_file = "/root/novo-ai-monitor/seen_news.txt"

    try:
        with open(seen_file, "r") as f:
            seen = set(line.strip() for line in f.readlines())
    except:
        seen = set()

    feed = feedparser.parse(
        "https://news.google.com/rss/search?q=Novo+Nordisk+stock+OR+Wegovy+OR+Ozempic&hl=en-US&gl=US&ceid=US:en"
    )

    negative_words = [
        "falls", "drops", "lawsuit", "warning", "cuts",
        "misses", "pressure", "competition", "decline",
        "risk", "probe", "investigation", "side effects",
        "Eli Lilly", "price war"
    ]

    matches = []

    for entry in feed.entries[:10]:
        title = entry.title
        title_lower = title.lower()

        if (
            title not in seen
            and any(word.lower() in title_lower for word in negative_words)
        ):
            matches.append(title)
            seen.add(title)

    if matches:
        message = (
            "📰 NOVO NYHEDSALARM\n"
            "Muligt negativt nyhedssignal:\n\n"
            + "\n\n".join(matches[:5])
        )
        send_telegram(message)

    with open(seen_file, "w") as f:
        for title in seen:
            f.write(title + "\n")

    return {
        "checked_articles": len(feed.entries[:10]),
        "negative_matches": matches[:5],
        "alarm_sent": bool(matches)
    }

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

    novo = get_stock_data("NOVO-B.CO")
    dsv = get_stock_data("DSV.CO")

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
            "ticker": "NOVO-B.CO",
            "ai_log": "/root/novo-ai-monitor/last_ai_news_check.log"
        },
        {
            "name": "DSV",
            "ticker": "DSV.CO",
            "ai_log": "/root/novo-ai-monitor/last_dsv_ai_news_check.log"
        }
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

    for stock_name, ticker, logfile in [
        ("NOVO", "NOVO-B.CO", "/root/novo-ai-monitor/last_ai_news_check.log"),
        ("DSV", "DSV.CO", "/root/novo-ai-monitor/last_dsv_ai_news_check.log")
    ]:

        data = get_stock_data(ticker)

        ai_risk = extract_ai_risk(logfile)

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
def stock_screener():

    watchlist = {
        "NOVO": "NOVO-B.CO",
        "DSV": "DSV.CO",
        "VESTAS": "VWS.CO",
        "GENMAB": "GMAB.CO",
        "CARLSBERG": "CARL-B.CO",
        "MAERSK": "MAERSK-B.CO",
        "ORSTED": "ORSTED.CO",
        "PANDORA": "PNDORA.CO",
        "APPLE": "AAPL",
        "MICROSOFT": "MSFT",
        "NVIDIA": "NVDA",
        "ASML": "ASML.AS",
        "TESLA": "TSLA",
        "AMAZON": "AMZN",
        "META": "META",
        "GOOGLE": "GOOGL"
    }

    fx_rates = get_fx_rates()
    results = []

    for name, ticker in watchlist.items():
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period="10d")

            latest = float(data["Close"].iloc[-1])
            week_ago = float(data["Close"].iloc[-6])

            currency = get_currency(ticker)
            latest_dkk = convert_to_dkk(latest, currency, fx_rates)

            weekly_change = ((latest - week_ago) / week_ago) * 100

            score = 50

            if weekly_change > 5:
                score += 20
            elif weekly_change > 2:
                score += 10

            if weekly_change < -5:
                score -= 20

            results.append({
                "stock": name,
                "price": round(latest_dkk, 2),
                "original_price": round(latest, 2),
                "currency": currency,
                "weekly_change": round(weekly_change, 2),
                "score": score
            })

        except Exception as e:
            results.append({
                "stock": name,
                "error": str(e)
            })

    results = sorted(
        results,
        key=lambda x: x.get("score", 0),
        reverse=True
    )

    return {"ranking": results}




@app.route("/stock-screener-report")
def stock_screener_report():
    data = stock_screener()
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
    data = stock_screener()
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
    cache_seconds = 1800

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
    tech_data = stock_screener()
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


@app.route("/portfolio-analysis")
def portfolio_analysis():
    novo_qty = 23
    novo_buy_price = 301.3
    dsv_qty = 4
    dsv_buy_price = 1588.5

    novo_price = float(yf.Ticker("NOVO-B.CO").history(period="10d")["Close"].iloc[-1])
    dsv_price = float(yf.Ticker("DSV.CO").history(period="10d")["Close"].iloc[-1])

    novo_value = novo_qty * novo_price
    dsv_value = dsv_qty * dsv_price
    total_value = novo_value + dsv_value

    novo_weight = (novo_value / total_value) * 100
    dsv_weight = (dsv_value / total_value) * 100

    novo_profit = novo_value - (novo_qty * novo_buy_price)
    dsv_profit = dsv_value - (dsv_qty * dsv_buy_price)
    total_profit = novo_profit + dsv_profit

    if max(novo_weight, dsv_weight) > 65:
        concentration = "Høj"
    elif max(novo_weight, dsv_weight) > 50:
        concentration = "Moderat"
    else:
        concentration = "Lav"

    analysis = f"""
Porteføljeanalyse:

Samlet værdi: {total_value:.2f} DKK
Samlet gevinst/tab: {total_profit:.2f} DKK

Fordeling:
NOVO: {novo_weight:.1f}%
DSV: {dsv_weight:.1f}%

Koncentrationsrisiko: {concentration}

AI-forslag:
- Porteføljen består kun af 2 aktier.
- Diversificering er lav.
- Overvej at sprede på flere sektorer og lande.
- Mulige kategorier: teknologi, industri, energi, indeksfond/ETF.
- Dette er ikke finansiel rådgivning.
"""

    return {
        "total_value": round(total_value, 2),
        "total_profit": round(total_profit, 2),
        "novo_weight": round(novo_weight, 1),
        "dsv_weight": round(dsv_weight, 1),
        "concentration_risk": concentration,
        "analysis": analysis
    }


@app.route("/portfolio-analysis-page")
def portfolio_analysis_page():
    data = portfolio_analysis()

    return f"""
    <html>
    <head>
        <title>Porteføljeanalyse</title>
        <style>
            body {{ font-family: Arial, sans-serif; background:#eef2f7; padding:40px; }}
            .container {{ max-width:1000px; margin:auto; }}
            .card {{ background:white; padding:24px; border-radius:14px; margin-bottom:20px; box-shadow:0 10px 30px rgba(0,0,0,0.08); }}
            .metric {{ font-size:20px; }}
            pre {{ white-space:pre-wrap; font-family:Arial, sans-serif; line-height:1.6; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>💼 Porteføljeanalyse V2.9.1</h1>

            <div class="card">
                <p class="metric">Samlet værdi: <b>{data.get("total_value")} DKK</b></p>
                <p class="metric">Samlet gevinst/tab: <b>{data.get("total_profit")} DKK</b></p>
                <p class="metric">NOVO vægt: <b>{data.get("novo_weight")}%</b></p>
                <p class="metric">DSV vægt: <b>{data.get("dsv_weight")}%</b></p>
                <p class="metric">Koncentrationsrisiko: <b>{data.get("concentration_risk")}</b></p>
            </div>

            <div class="card">
                <pre>{data.get("analysis")}</pre>
            </div>

            <p>Dette er analyse og ikke finansiel rådgivning.</p>
        </div>
    </body>
    </html>
    """


@app.route("/market-dashboard")
def market_dashboard():
    markets = {
        "S&P 500": "^GSPC",
        "Nasdaq": "^IXIC",
        "OMXC25": "^OMXC25",
        "DAX": "^GDAXI"
    }

    results = []
    positive = 0

    for name, ticker in markets.items():
        try:
            data = yf.Ticker(ticker).history(period="5d")
            latest = float(data["Close"].iloc[-1])
            previous = float(data["Close"].iloc[-2])
            change = ((latest - previous) / previous) * 100

            if change > 0:
                positive += 1

            results.append({
                "market": name,
                "price": round(latest, 2),
                "change": round(change, 2)
            })
        except Exception as e:
            results.append({
                "market": name,
                "error": str(e)
            })

    if positive >= 3:
        signal = "Bullish"
        color = "green"
    elif positive == 2:
        signal = "Neutral"
        color = "orange"
    else:
        signal = "Bearish"
        color = "red"

    rows = ""
    for item in results:
        if "error" in item:
            rows += f"<tr><td>{item['market']}</td><td colspan='2'>Fejl: {item['error']}</td></tr>"
        else:
            c = "green" if item["change"] >= 0 else "red"
            rows += f"""
            <tr>
                <td><b>{item['market']}</b></td>
                <td>{item['price']}</td>
                <td style="color:{c}; font-weight:bold;">{item['change']}%</td>
            </tr>
            """

    return f"""
    <html>
    <head>
        <title>Global Market Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; background:#eef2f7; padding:40px; }}
            .container {{ max-width:1000px; margin:auto; }}
            .card {{ background:white; padding:24px; border-radius:14px; margin-bottom:20px; box-shadow:0 10px 30px rgba(0,0,0,0.08); }}
            table {{ width:100%; border-collapse:collapse; background:white; }}
            th {{ background:#111827; color:white; padding:14px; text-align:left; }}
            td {{ padding:14px; border-bottom:1px solid #e5e7eb; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌍 Global Market Dashboard V3.1</h1>

            <div class="card">
                <h2 style="color:{color};">AI Markedssignal: {signal}</h2>
                <p>Baseret på dagsudvikling i globale indeks.</p>
            </div>

            <table>
                <tr>
                    <th>Marked</th>
                    <th>Niveau</th>
                    <th>Dagsændring</th>
                </tr>
                {rows}
            </table>

            <p>Dette er markedsoversigt og ikke finansiel rådgivning.</p>
        </div>
    </body>
    </html>
    """


@app.route("/system-status-page")
def system_status_page():
    import os
    from datetime import datetime

    files = {
        "AI cache": "/root/novo-ai-monitor/stock_news_ai_cache.json",
        "Historik log": "/root/novo-ai-monitor/history_save.log",
        "Combined report log": "/root/novo-ai-monitor/combined_report.log",
        "Smart alerts log": "/root/novo-ai-monitor/last_smart_alerts.log",
        "Portfolio alerts log": "/root/novo-ai-monitor/portfolio_alerts.log",
    }

    rows = ""

    for name, path in files.items():
        if os.path.exists(path):
            size = os.path.getsize(path)
            modified = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M:%S")
            status = "✅ OK"
        else:
            size = "-"
            modified = "-"
            status = "⚠️ Mangler"

        rows += f"""
        <tr>
            <td><b>{name}</b></td>
            <td>{status}</td>
            <td>{size}</td>
            <td>{modified}</td>
        </tr>
        """

    return f"""
    <html>
    <head>
        <title>Systemstatus</title>
        <style>
            body {{ font-family: Arial, sans-serif; background:#eef2f7; padding:40px; }}
            .container {{ max-width:1000px; margin:auto; }}
            .card {{ background:white; padding:24px; border-radius:14px; margin-bottom:20px; box-shadow:0 10px 30px rgba(0,0,0,0.08); }}
            table {{ width:100%; border-collapse:collapse; background:white; border-radius:14px; overflow:hidden; }}
            th {{ background:#111827; color:white; padding:14px; text-align:left; }}
            td {{ padding:14px; border-bottom:1px solid #e5e7eb; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚙️ Systemstatus V3.2</h1>

            <div class="card">
                <p><b>Novo AI service:</b> ✅ Aktiv hvis denne side vises</p>
                <p><b>HTTPS/Caddy:</b> ✅ Aktiv hvis siden åbnes via monitor.ethinking.dk</p>
                <p><b>Senest opdateret:</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>

            <table>
                <tr>
                    <th>Komponent</th>
                    <th>Status</th>
                    <th>Størrelse</th>
                    <th>Sidst ændret</th>
                </tr>
                {rows}
            </table>
        </div>
    </body>
    </html>
    """


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


@app.route("/portfolio-manager-page")
def portfolio_manager_page():
    import csv

    portfolio_file = "/root/novo-ai-monitor/portfolio.csv"

    def get_fx_rate(pair, fallback):
        try:
            fx = yf.Ticker(pair).history(period="5d")
            return float(fx["Close"].iloc[-1])
        except Exception:
            return fallback

    usd_dkk = get_fx_rate("USDDKK=X", 6.95)
    eur_dkk = get_fx_rate("EURDKK=X", 7.46)

    def currency_for_ticker(ticker):
        if ticker.endswith(".CO"):
            return "DKK"
        if ticker.endswith(".AS"):
            return "EUR"
        return "USD"

    def to_dkk(amount, currency):
        if currency == "USD":
            return amount * usd_dkk
        if currency == "EUR":
            return amount * eur_dkk
        return amount

    holdings = []
    total_value = 0
    total_cost = 0

    with open(portfolio_file, "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            stock_name = row["stock"]
            ticker = row["ticker"]
            qty = float(row["qty"])
            buy_price = float(row["buy_price"])

            data = yf.Ticker(ticker).history(period="10d")
            latest = float(data["Close"].iloc[-1])

            currency = currency_for_ticker(ticker)

            latest_dkk = to_dkk(latest, currency)
            buy_price_dkk = to_dkk(buy_price, currency)

            value = latest_dkk * qty
            cost = buy_price_dkk * qty
            profit = value - cost
            profit_pct = (profit / cost) * 100 if cost else 0

            total_value += value
            total_cost += cost

            holdings.append({
                "stock": stock_name,
                "ticker": ticker,
                "qty": qty,
                "buy_price": buy_price,
                "latest": latest,
                "currency": currency,
                "buy_price_dkk": buy_price_dkk,
                "latest_dkk": latest_dkk,
                "value": value,
                "cost": cost,
                "profit": profit,
                "profit_pct": profit_pct
            })

    rows = ""

    for h in holdings:
        weight = (h["value"] / total_value) * 100 if total_value else 0
        color = "green" if h["profit"] >= 0 else "red"

        rows += f"""
        <tr>
            <td><b>{h['stock']}</b></td>
            <td>{h['ticker']}</td>
            <td>{h['qty']}</td>
            <td>{h['buy_price']:.2f} {h['currency']}<br><small>{h['buy_price_dkk']:.2f} DKK</small></td>
            <td>{h['latest']:.2f} {h['currency']}<br><small>{h['latest_dkk']:.2f} DKK</small></td>
            <td>{h['value']:.2f} DKK</td>
            <td style="color:{color}; font-weight:bold;">{h['profit']:.2f} DKK ({h['profit_pct']:.2f}%)</td>
            <td>{weight:.1f}%</td>
        </tr>
        """

    total_profit = total_value - total_cost
    total_profit_pct = (total_profit / total_cost) * 100 if total_cost else 0
    total_color = "green" if total_profit >= 0 else "red"

    return f"""
    <html>
    <head>
        <title>Portfolio Manager</title>
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
            <h1>💼 Portfolio Manager V3.5</h1>

            <div class="card">
                <p><b>Samlet værdi:</b> {total_value:.2f} DKK</p>
                <p><b>Samlet gevinst/tab:</b> <span style="color:{total_color}; font-weight:bold;">{total_profit:.2f} DKK ({total_profit_pct:.2f}%)</span></p>
                <p><b>Datakilde:</b> portfolio.csv</p>
                <p><b>Valutakurser:</b> USD/DKK {usd_dkk:.2f} · EUR/DKK {eur_dkk:.2f}</p>
            </div>

            <table>
                <tr>
                    <th>Aktie</th>
                    <th>Ticker</th>
                    <th>Antal</th>
                    <th>Købskurs</th>
                    <th>Aktuel kurs</th>
                    <th>Værdi</th>
                    <th>Gevinst/tab</th>
                    <th>Vægt</th>
                </tr>
                {rows}
            </table>

            <p>Rediger beholdninger i: /root/novo-ai-monitor/portfolio.csv</p>
        </div>
    </body>
    </html>
    """

app.run(host="0.0.0.0", port=3000)
