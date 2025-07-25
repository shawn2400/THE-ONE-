from flask import Flask, jsonify
from binance.client import Client
import threading
import json
import time
import os
import traceback

app = Flask(__name__)

# מפתחות Binance
BINANCE_API_KEY = "jJnAfHZd0EWQpX0CA0QNxRnrtsrnW10GQMg6Dx8d9O63mZSzZV7ixSBLNEqTeMIh"
BINANCE_SECRET_KEY = "soQYlzu6jYiQj8ZLxlXNPWHWTLPRb0EXLK239iFVz1XmnX9EvtDaG7D9zGabCVEq"

client = Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_SECRET_KEY)

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "MATICUSDT", "COTIUSDT"]

def calculate_rsi(prices, period=14):
    deltas = [prices[i + 1] - prices[i] for i in range(len(prices) - 1)]
    gains = [d for d in deltas if d > 0]
    losses = [-d for d in deltas if d < 0]

    avg_gain = sum(gains[-period:]) / period if gains else 0
    avg_loss = sum(losses[-period:]) / period if losses else 1
    rs = avg_gain / avg_loss if avg_loss else 0
    rsi = 100 - (100 / (1 + rs)) if rs else 0
    return round(rsi, 2)

def calculate_ema(prices, period=21):
    k = 2 / (period + 1)
    ema = prices[0]
    for price in prices[1:]:
        ema = price * k + ema * (1 - k)
    return round(ema, 4)

def update_data():
    while True:
        try:
            print("[*] מתחיל עדכון live.json...")
            live_data = {}
            for symbol in SYMBOLS:
                try:
                    print(f"[+] מושך {symbol}")
                    klines = client.futures_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=100)
                    close_prices = [float(k[4]) for k in klines]
                    volume = float(klines[-1][5])
                    mark_price = float(client.futures_mark_price(symbol=symbol)['markPrice'])
                    rsi = calculate_rsi(close_prices)
                    ema = calculate_ema(close_prices)
                    live_data[symbol] = {
                        "price": mark_price,
                        "rsi": rsi,
                        "ema": ema,
                        "volume": volume
                    }
                except Exception as e:
                    print(f"[!] שגיאה עם {symbol}: {e}")
                    traceback.print_exc()
                    live_data[symbol] = {"error": str(e)}

            with open("live.json", "w") as f:
                json.dump(live_data, f, indent=2)
            print("[✓] live.json עודכן\n")

            time.sleep(2)

        except Exception as e:
            print(f"[CRITICAL] שגיאה כללית: {e}")
            traceback.print_exc()
            time.sleep(5)

@app.route("/")
def home():
    return jsonify({"status": "OK", "message": "Live server is running"})

@app.route("/live")
def get_live_data():
    if not os.path.exists("live.json"):
        return jsonify({"error": "live.json does not exist yet"})

    try:
        with open("live.json", "r") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": f"failed to read live.json: {str(e)}"})

if __name__ == "__main__":
    try:
        threading.Thread(target=update_data, daemon=True).start()
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
    except Exception as e:
        print(f"[FATAL] שגיאה בהפעלה: {e}")
        traceback.print_exc()


