from flask import Flask
import yfinance as yf

app = Flask(__name__)

@app.route("/")
def home():

    stock = yf.Ticker("NVO")

    data = stock.history(period="5d")

    latest = data['Close'].iloc[-1]

    return {
        "stock": "Novo Nordisk",
        "price": round(float(latest), 2),
        "status": "AI monitor active"
    }

app.run(host="0.0.0.0", port=3000)