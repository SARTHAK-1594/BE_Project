import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib

# Load your clean, normal sensor data
df = pd.read_csv('normal_data.csv')  # Make sure this file exists

# Features
X = df[['temperature', 'humidity', 'soil_moisture', 'fan_status']]

# Train Isolation Forest
model = IsolationForest(contamination=0.02, random_state=42)
model.fit(X)

# Save model to .pkl
joblib.dump(model, 'anomaly_model.pkl')

print("Model trained and saved as anomaly_model.pkl")
