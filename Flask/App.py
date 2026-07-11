from flask import Flask, request, jsonify
import joblib
import requests
import numpy as np
import time
import pandas as pd

app = Flask(__name__)

# Load AI models
poison_model = joblib.load("anomaly_model.pkl")
dos_model = joblib.load("dos_model.pkl")

# ThingSpeak configuration
THINGSPEAK_API_KEY = "FE1KB58XLVZE7TON"
THINGSPEAK_URL = "https://api.thingspeak.com/update"

# IP request logs and blocking
REQUEST_LOG = {}
BLOCKED_IPS = {}

DOS_TIME_WINDOW = 30
DOS_FEATURE_WINDOW = 10
BLOCK_DURATION = 60

@app.route('/')
def home():
    return "🚀 Flask AI Gateway Running"

@app.route('/iot-data', methods=['POST'])
def receive_data():
    current_time = time.time()
    ip = request.remote_addr

    # ⛔ Check if IP is already blocked
    if ip in BLOCKED_IPS:
        if current_time < BLOCKED_IPS[ip]:
            print(f"⛔ Blocked IP {ip} attempted access.")
            return jsonify({"status": "blocked", "attack": 1}), 403
        else:
            del BLOCKED_IPS[ip]

    # 🔁 Update request timestamps
    if ip not in REQUEST_LOG:
        REQUEST_LOG[ip] = []
    REQUEST_LOG[ip] = [t for t in REQUEST_LOG[ip] if current_time - t < DOS_TIME_WINDOW]
    REQUEST_LOG[ip].append(current_time)

    # 🧠 DoS Detection
    timestamps = REQUEST_LOG[ip]
    request_count = len(timestamps)

    if request_count > 1:
        intervals = [timestamps[i] - timestamps[i - 1] for i in range(1, len(timestamps))]
        average_interval = sum(intervals[-DOS_FEATURE_WINDOW:]) / min(len(intervals), DOS_FEATURE_WINDOW)
    else:
        average_interval = DOS_TIME_WINDOW

    dos_features = pd.DataFrame([{
        'request_count': request_count,
        'average_interval': average_interval
    }])

    dos_attack = int(dos_model.predict(dos_features)[0])

    # ⛔ If DoS attack detected → STOP
    if dos_attack == 1:
        BLOCKED_IPS[ip] = current_time + BLOCK_DURATION
        print(f"🚫 DoS attack detected from {ip}. Blocking for {BLOCK_DURATION} seconds.")

        payload = {
            'api_key': THINGSPEAK_API_KEY,
            'field5': 1   # Attack detected
        }
        requests.post(THINGSPEAK_URL, data=payload)

        return jsonify({
            "status": "blocked",
            "attack": 1,
            "message": "🚫 DoS attack detected. Data not forwarded."
        }), 403

    # ✅ No DoS → Proceed to Poison Detection
    data = request.json
    print("📥 Received from", ip, ":", data)

    poison_features = pd.DataFrame([{
        'temperature': data['temperature'],
        'humidity': data['humidity'],
        'soil_moisture': data['soil_moisture'],
        'fan_status': data['fan_status']
    }])

    raw_prediction = poison_model.predict(poison_features)[0]
    poison_attack = 1 if raw_prediction == -1 else 0

    # ⛔ If Data Poisoning detected → STOP
    if poison_attack == 1:
        print("⚠️ Data poisoning detected. Blocking data.")

        payload = {
            'api_key': THINGSPEAK_API_KEY,
            'field5': 1   # Attack detected
        }
        requests.post(THINGSPEAK_URL, data=payload)

        return jsonify({
            "status": "anomaly",
            "attack": 1,
            "message": "⚠️ Data poisoning detected. Data not forwarded."
        }), 403

    # ✅ CLEAN DATA → Send to ThingSpeak
    payload = {
        'api_key': THINGSPEAK_API_KEY,
        'field1': data['temperature'],
        'field2': data['humidity'],
        'field3': data['soil_moisture'],
        'field4': data['fan_status'],
        'field5': 0   # No attack
    }

    response = requests.post(THINGSPEAK_URL, data=payload)
    print("📡 ThingSpeak Response:", response.text)

    return jsonify({
        "status": "normal",
        "attack": 0,
        "message": "✅ Clean data forwarded"
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)