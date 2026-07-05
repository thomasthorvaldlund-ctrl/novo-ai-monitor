from flask import Blueprint
import yfinance as yf

market_dashboard_bp = Blueprint("market_dashboard", __name__)

@market_dashboard_bp.route("/market-dashboard")
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