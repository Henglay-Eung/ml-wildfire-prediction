import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

# Load CSV
df = pd.read_csv("../processed_datasets/merge_data/cleaned_merged_data_2020.csv")  # Replace with your CSV path

# Step 1: Quick data check
print("First few rows:\n", df.head())
print("\nData Summary:\n", df.describe())
print("\nMissing values:\n", df.isnull().sum())

# Drop rows with missing values (you could also impute)
df = df.dropna()

# Drop duplicates
df = df.drop_duplicates()

# Check if fire_size has only zeros (nothing to predict!)
if df["fire_size"].nunique() <= 1:
    print("fire_size has only one unique value. Not enough variation to train a model.")
    exit()
df["date"] = pd.to_datetime(df["date"])
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df["day"] = df["date"].dt.day
df["dayofyear"] = df["date"].dt.dayofyear
df = df.drop(columns=["date"]) 
# Step 2: Feature selection
X = df.drop(columns=["fire_size"])  # drop non-numeric or target columns
y = df["fire_size"]

# Optional: check correlation
print("\nCorrelation with fire_size:\n", df.corr()["fire_size"].sort_values(ascending=False))

# Step 3: Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Optional: Standardize features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Step 4: Train model
model = RandomForestRegressor(n_estimators=100, random_state=42, verbose=2)
model.fit(X_train_scaled, y_train)

# Step 5: Evaluate
y_pred = model.predict(X_test_scaled)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"\nModel Performance:")
print(f"MSE: {mse:.4f}")
print(f"R² Score: {r2:.4f}")

import joblib
import json

# 1. Save the trained model
joblib.dump(model, 'wildfire_prediction_random_forest_model.pkl')

# 2. Save the scaler
joblib.dump(scaler, 'random_forest_feature_scaler.pkl')

# 3. Save feature names
feature_names = list(X.columns)
with open('random_forest_feature_names.json', 'w') as f:
    json.dump(feature_names, f)

print("Saved model artifacts:")
print("- wildfire_prediction_model.pkl (trained model)")
print("- feature_scaler.pkl (feature scaler)")
print("- random_forest_feature_names.json (feature names)")

