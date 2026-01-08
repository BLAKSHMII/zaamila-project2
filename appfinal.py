from flask import Flask, render_template
from flask_socketio import SocketIO, join_room
import requests
import random
import time

# ---------------- APP SETUP ----------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

# SocketIO setup
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# ---------------- CONFIG: FINNHUB ----------------
FINNHUB_API_KEY = "d5fnph1r01qnjhodfvfgd5fnph1r01qnjhodfvg0"  # Replace with your Finnhub API key
BASE_URL = "https://finnhub.io/api/v1/quote"

# ---------------- BACKGROUND TASK ----------------
started = False
last_prices = {}  # track last prices to simulate green/red changes

def get_real_price(symbol):
    """Fetch real stock price from Finnhub"""
    try:
        response = requests.get(BASE_URL, params={
            "symbol": symbol,
            "token": FINNHUB_API_KEY
        }, timeout=5)
        response.raise_for_status()
        price = round(response.json().get("c", 0), 2)
        # Add tiny random fluctuation for demo (to see green/red flash)
        price += random.uniform(-1, 1)
        return round(price, 2)
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        # fallback to random mock price
        return round(random.uniform(100, 300), 2)

def stock_stream():
    """Emit stock prices to subscribed clients every 2 seconds"""
    stocks = ["AAPL", "TSLA", "GOOGL"]
    while True:
        for stock in stocks:
            price = get_real_price(stock)
            socketio.emit("stock_update", {"stock": stock, "price": price}, room=stock)
        socketio.sleep(2)  # update interval

# ---------------- ROUTE ----------------
@app.route('/')
def index():
    return render_template('indexfinal.html')

# ---------------- SOCKET EVENTS ----------------
@socketio.on("connect")
def handle_connect():
    global started
    print("Client connected")
    if not started:
        socketio.start_background_task(stock_stream)
        started = True

@socketio.on("subscribe")
def handle_subscribe(data):
    stock = data["stock"].upper()
    join_room(stock)
    print(f"Subscribed to {stock}")

# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    socketio.run(app,debug=True)
