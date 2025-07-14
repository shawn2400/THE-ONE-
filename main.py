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

if _name_ == '_main_':
    print("🔗 Proxy is running...")
    app.run(host='0.0.0.0', port=5000)
