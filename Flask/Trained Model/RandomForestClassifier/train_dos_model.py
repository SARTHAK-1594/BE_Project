# train_dos_model.py

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# Step 1: Load dataset (Replace 'dos_dataset.csv' with your actual file)
df = pd.read_csv("dos_dataset.csv")

# Step 2: Features and label
X = df[['request_count', 'average_interval']]  # You can add more features
y = df['is_dos']  # 1 = DoS, 0 = Normal

# Step 3: Split into train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 4: Train the model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Step 5: Evaluate
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

# Step 6: Save model
joblib.dump(model, "dos_model.pkl")
print("✅ Model saved as dos_model.pkl")
