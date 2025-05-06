import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import joblib
import json

# =============================================
# 1. Data Loading and Preparation
# =============================================
print("Loading and preparing data...")
df = pd.read_csv("../processed_datasets/merge_data/cleaned_merged_data_2020.csv")

# Basic data checks
print("\nData Summary:")
print(f"- Shape: {df.shape}")
print(f"- Columns: {df.columns.tolist()}")
print(f"- Missing Values:\n{df.isnull().sum()}")

# Data cleaning
df = df.dropna().drop_duplicates()
if df["fire_size"].nunique() <= 1:
    raise ValueError("Target variable 'fire_size' has no variation!")

# Feature engineering
df["date"] = pd.to_datetime(df["date"])
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df["day"] = df["date"].dt.day
df["dayofyear"] = df["date"].dt.dayofyear
df = df.drop(columns=["date"])

# =============================================
# 2. Train-Test Split & Scaling
# =============================================
X = df.drop(columns=["fire_size"])
y = df["fire_size"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, shuffle=True
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# =============================================
# 3. Train Model with Pre-Tuned Parameters
# =============================================
best_params = {
    'colsample_bytree': 0.9795542149013333,
    'gamma': 9.656320330745594,
    'learning_rate': 0.2525192044349383,
    'max_depth': 11,
    'min_child_weight': 2,
    'n_estimators': 1463,
    'reg_alpha': 2.410255660260117,
    'reg_lambda': 6.8326361882545825,
    'subsample': 0.8439986631130484
}

print("\n🚀 Training final model with optimized parameters...")
final_model = xgb.XGBRegressor(
    **best_params,
    random_state=42,
    n_jobs=-1,
    early_stopping_rounds=50,
    eval_metric='rmse'
)

final_model.fit(
    X_train_scaled, 
    y_train,
    eval_set=[(X_test_scaled, y_test)],
    verbose=10
)

# =============================================
# 4. Model Evaluation
# =============================================
def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    
    mse = mean_squared_error(y_test, y_pred)
    metrics = {
        'MSE': mse,
        'RMSE': np.sqrt(mse),
        'MAE': mean_absolute_error(y_test, y_pred),
        'R²': r2_score(y_test, y_pred)
    }
    
    return metrics

print("\nModel Evaluation:")
metrics = evaluate_model(final_model, X_test_scaled, y_test)
for name, value in metrics.items():
    print(f"{name}: {value:.4f}")

# =============================================
# 5. Save Model Artifacts
# =============================================
artifacts = {
    'model': 'wildfire_prediction_xgboost.pkl',
    'scaler': 'feature_scaler.pkl',
    'features': 'feature_names.json',
    'params': 'best_params.json'
}

joblib.dump(final_model, artifacts['model'])
joblib.dump(scaler, artifacts['scaler'])
with open(artifacts['features'], 'w') as f:
    json.dump(X.columns.tolist(), f)
with open(artifacts['params'], 'w') as f:
    json.dump(best_params, f)
