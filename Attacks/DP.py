# simulate_fake_sensor_data.py
import requests
import time
import random

FLASK_SERVER_URL = "http://192.168.53.242:5000/iot-data"  # Change as needed

# Simulate for 20 seconds
for _ in range(1):
    fake_data = {
        "temperature": random.choice([75, 85, 100]),  # Abnormally high
        "humidity": random.choice([5, 100]),            # Too low or high
        "soil_moisture": random.choice([90, 100]),      # Edge values
        "fan_status": 0                                 # Maliciously off
    }

    try:
        r = requests.post(FLASK_SERVER_URL, json=fake_data, timeout=1)
        print(f"Injected fake data: {fake_data}, Response: {r.status_code}")
    except Exception as e:
        print("Failed to send:", e)

    time.sleep(2)
