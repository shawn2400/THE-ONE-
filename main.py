from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "🔧 Flask proxy is running!"

@app.route('/live')
def live():
    try:
        with open("live.json", "r") as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return "live.json not found", 404

import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))


    print("🔗 Proxy is running at: https://" + os.environ.get("REPL_SLUG", "your-url") + "." + os.environ.get("REPL_OWNER", "your-user") + ".repl.co/live")
    app.run(host='0.0.0.0', port=10000)
