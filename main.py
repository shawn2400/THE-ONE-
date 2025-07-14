def update_data():
    while True:
        print("[*] עדכון נתונים...")  # לוג 1
        live_data = {}
        for symbol in SYMBOLS:
            try:
                print(f"[*] מושך נתונים עבור {symbol}")
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
                print(f"[!] שגיאה עם {symbol}: {str(e)}")  # לוג 2
                live_data[symbol] = {"error": str(e)}

        try:
            with open("live.json", "w") as f:
                json.dump(live_data, f, indent=2)
            print("[✓] live.json עודכן בהצלחה\n")
        except Exception as e:
            print(f"[!] שגיאה בכתיבת live.json: {str(e)}")

        time.sleep(2)

