import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import xgboost as xgb  # Install with: pip install xgboost
import joblib
import json

# Load CSV
df = pd.read_csv("../processed_datasets/merge_data/cleaned_merged_data_2020.csv")  # Replace with your CSV path

# Step 1: Quick data check
print("First few rows:\n", df.head())
print("\nData Summary:\n", df.describe())
print("\nMissing values:\n", df.isnull().sum())

# Drop rows with missing values (or impute if preferred)
df = df.dropna()
df = df.drop_duplicates()

# Check if fire_size has variation
if df["fire_size"].nunique() <= 1:
    print("fire_size has no variation. Cannot train a model.")
    exit()

# Feature engineering: Extract date components
df["date"] = pd.to_datetime(df["date"])
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df["day"] = df["date"].dt.day
df["dayofyear"] = df["date"].dt.dayofyear
df = df.drop(columns=["date"])

# Step 2: Feature selection
X = df.drop(columns=["fire_size"])
y = df["fire_size"]

# Check correlation (optional)
print("\nCorrelation with fire_size:\n", df.corr()["fire_size"].sort_values(ascending=False))

# Step 3: Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Standardize features (important for gradient boosting)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Step 4: Train XGBoost model
model = xgb.XGBRegressor(
    n_estimators=2000,  # Number of boosting rounds
    learning_rate=0.1,  # Step size shrinkage
    max_depth=5,       # Tree depth
    random_state=42,
    verbosity=1,       # XGBoost verbosity (1=warnings, 2=info, 3=debug)
    early_stopping_rounds=10,  # Stop if no improvement
    eval_metric="rmse"  # Metric to track
)

# Fit with verbose progress
print("\nTraining XGBoost model...")
model.fit(
    X_train_scaled, 
    y_train,
    eval_set=[(X_test_scaled, y_test)],  # Track validation performance
    verbose=True  # Show progress during training
)

# Step 5: Evaluate
y_pred = model.predict(X_test_scaled)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"\nModel Performance:")
print(f"✅ MSE: {mse:.4f}")
print(f"✅ R² Score: {r2:.4f}")

# Save artifacts
joblib.dump(model, 'wildfire_prediction_xgboost.pkl')
joblib.dump(scaler, 'feature_scaler.pkl')
with open('feature_names.json', 'w') as f:
    json.dump(list(X.columns), f)

print("✅ Saved artifacts:")
print("- wildfire_prediction_xgboost.pkl (XGBoost model)")
print("- feature_scaler.pkl")
print("- feature_names.json")

# Plot predictions vs actual
plt.figure(figsize=(8, 5))
plt.scatter(y_test, y_pred, alpha=0.7)
plt.xlabel("Actual Fire Size")
plt.ylabel("Predicted Fire Size")
plt.title("XGBoost: Actual vs Predicted Fire Size")
plt.grid(True)
plt.show()

# Feature importance (XGBoost-specific)
xgb.plot_importance(model)
plt.show()