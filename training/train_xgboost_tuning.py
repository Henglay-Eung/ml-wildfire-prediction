import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
from scipy.stats import randint, uniform
import xgboost as xgb
import joblib
import json
from sklearn.inspection import permutation_importance

# =============================================
# 1. Data Loading and Preparation
# =============================================
print("🔍 Loading and preparing data...")
df = pd.read_csv("../processed_datasets/merge_data/cleaned_merged_data_2020.csv")

# Basic data checks
print("\n📊 Data Summary:")
print(f"- Shape: {df.shape}")
print(f"- Columns: {df.columns.tolist()}")
print(f"- Missing Values:\n{df.isnull().sum()}")

# Data cleaning
df = df.dropna().drop_duplicates()
if df["fire_size"].nunique() <= 1:
    raise ValueError("Target variable 'fire_size' has no variation!")

# Feature engineering - CORRECTED datetime features
df["date"] = pd.to_datetime(df["date"])
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df["day"] = df["date"].dt.day
df["dayofyear"] = df["date"].dt.dayofyear
# Removed weekofyear as it's not a direct attribute
df = df.drop(columns=["date"])

# =============================================
# 2. Feature Analysis
# =============================================
print("\n🔎 Feature Analysis:")
X = df.drop(columns=["fire_size"])
y = df["fire_size"]

# Correlation analysis
corr_matrix = df.corr()
plt.figure(figsize=(12, 8))
sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm")
plt.title("Feature Correlation Matrix")
plt.show()

# =============================================
# 3. Train-Test Split & Scaling
# =============================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, shuffle=True
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# =============================================
# 4. Hyperparameter Tuning (RandomizedSearchCV)
# =============================================
# Define parameter distributions
param_dist = {
    'n_estimators': randint(100, 2000),
    'learning_rate': uniform(0.01, 0.3),
    'max_depth': randint(3, 12),
    'subsample': uniform(0.6, 0.4),  # Range: 0.6-1.0
    'colsample_bytree': uniform(0.6, 0.4),  # Range: 0.6-1.0
    'gamma': uniform(0, 10),
    'reg_lambda': uniform(1e-6, 10),
    'reg_alpha': uniform(1e-6, 10),
    'min_child_weight': randint(1, 20),
}

# Initialize XGBoost model
model = xgb.XGBRegressor(
    random_state=42,
    n_jobs=-1,
    early_stopping_rounds=50,
    eval_metric='rmse'
)

# Initialize RandomizedSearchCV
random_search = RandomizedSearchCV(
    estimator=model,
    param_distributions=param_dist,
    n_iter=50,  # Number of parameter combinations to try
    scoring='neg_mean_squared_error',
    cv=3,
    verbose=2,
    random_state=42,
    n_jobs=-1
)

print("\n🎛 Starting RandomizedSearchCV...")
random_search.fit(
    X_train_scaled, 
    y_train,
    eval_set=[(X_test_scaled, y_test)],
    verbose=False
)

# Get best parameters and model
best_params = random_search.best_params_
best_model = random_search.best_estimator_

print("\n🏆 Best Parameters Found:")
print(best_params)

# =============================================
# 5. Model Evaluation
# =============================================
def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    
    metrics = {
        'MSE': mean_squared_error(y_test, y_pred),
        'RMSE': mean_squared_error(y_test, y_pred, squared=False),
        'MAE': mean_absolute_error(y_test, y_pred),
        'R²': r2_score(y_test, y_pred)
    }
    
    # Plot feature importance
    fig, ax = plt.subplots(1, 2, figsize=(16, 6))
    xgb.plot_importance(model, ax=ax[0])
    ax[0].set_title("XGBoost Feature Importance")
    
    # Plot actual vs predicted
    ax[1].scatter(y_test, y_pred, alpha=0.5)
    ax[1].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
    ax[1].set_xlabel("Actual Fire Size")
    ax[1].set_ylabel("Predicted Fire Size")
    ax[1].set_title("Prediction Accuracy")
    
    plt.tight_layout()
    plt.show()
    
    return metrics

print("\n📊 Model Evaluation:")
metrics = evaluate_model(best_model, X_test_scaled, y_test)
for name, value in metrics.items():
    print(f"{name}: {value:.4f}")

# =============================================
# 6. Save Model Artifacts
# =============================================
artifacts = {
    'model': 'wildfire_prediction_xgboost.pkl',
    'scaler': 'feature_scaler.pkl',
    'features': 'feature_names.json',
    'params': 'best_params.json'
}

joblib.dump(best_model, artifacts['model'])
joblib.dump(scaler, artifacts['scaler'])
with open(artifacts['features'], 'w') as f:
    json.dump(X.columns.tolist(), f)
with open(artifacts['params'], 'w') as f:
    json.dump(best_params, f)

print("\n💾 Saved artifacts:")
for name, path in artifacts.items():
    print(f"- {name}: {path}")

# =============================================
# 7. Learning Curves Visualization
# =============================================
results = best_model.evals_result()
epochs = len(results['validation_0']['rmse'])
x_axis = range(0, epochs)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(x_axis, results['validation_0']['rmse'], label='Train')
ax.plot(x_axis, results['validation_0']['mae'], label='Test')
ax.legend()
plt.ylabel('RMSE/MAE')
plt.title('XGBoost Learning Curve')
plt.show()