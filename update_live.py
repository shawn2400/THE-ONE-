import json
import time
from binance.client import Client
from datetime import datetime

# מפתחות Binance שלך (שים לב - בטוח לא לחשוף בפומבי!)
API_KEY = "jJnAfHZd0EWQpX0CA0QNxRnrtsrnW10GQMg6Dx8d9O63mZSzZV7ixSBLNEqTeMIh"
API_SECRET = "soQYlzu6jYiQj8ZLxlXNPWHWTLPRb0EXLK239iFVz1XmnX9EvtDaG7D9zGabCVEq"

client = Client(API_KEY, API_SECRET)

def fetch_data():
    futures = client.futures_ticker_price()
    symbols = [s for s in futures if s['symbol'].endswith('USDT') and not s['symbol'].endswith('1000USDT')]

    result = []
    for sym in symbols:
        symbol = sym['symbol']
        try:
            klines = client.futures_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=21)
            closes = [float(k[4]) for k in klines]
            volume = float(klines[-1][5])
            price = float(closes[-1])
            rsi = compute_rsi(closes)
            ema9 = sum(closes[-9:]) / 9
            ema21 = sum(closes[-21:]) / 21

            result.append({
                "symbol": symbol,
                "price": round(price, 4),
                "rsi": round(rsi, 2),
                "ema9": round(ema9, 4),
                "ema21": round(ema21, 4),
                "volume": volume,
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            })
        except Exception as e:
            continue

    return result

def compute_rsi(closes, period=14):
    deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
    ups = [d for d in deltas if d > 0]
    downs = [-d for d in deltas if d < 0]

    avg_gain = sum(ups[-period:]) / period if len(ups) >= period else 0
    avg_loss = sum(downs[-period:]) / period if len(downs) >= period else 1  # למניעת חלוקה ב-0

    rs = avg_gain / avg_loss if avg_loss != 0 else 0
    rsi = 100 - (100 / (1 + rs))
    return rsi

while True:
    try:
        data = fetch_data()
        with open("live.json", "w") as f:
            json.dump({"status": "ok", "data": data}, f, indent=2)
        print(f"✔ Updated live.json with {len(data)} symbols.")
    except Exception as e:
        print("Error updating live.json:", e)
    time.sleep(2)
