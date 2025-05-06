import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
import time

# 1. Load and prepare data
print("Loading data...")
df = pd.read_csv('../processed_datasets/merge_data/cleaned_merged_data_2018_2020.csv').dropna()

# Convert date string to datetime and extract features
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'])
    df['day'] = df['date'].dt.day
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    print("Extracted day, month, year from date column")
else:
    print("Warning: 'date' column not found. Make sure temporal features exist.")
    
features = ['day', 'month', 'year', 'fmc', 'tmax', 'tmin', 'prcp', 'wind_speed', 'lat', 'lon']
X = df[features]
y = df['fire_size']

# 2. Train-test split and scaling
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 3. Train and evaluate Linear Regression model
print("\nTraining Linear Regression model...")
start_time = time.time()
linear_model = LinearRegression()
linear_model.fit(X_train_scaled, y_train)
y_pred = linear_model.predict(X_test_scaled)

print(f"Linear Regression RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.2f}")
print(f"Linear Regression R²: {r2_score(y_test, y_pred):.2f}")
print(f"Training time: {(time.time() - start_time):.2f} seconds")

# 4. Feature coefficients analysis
coefficients = pd.DataFrame({
    'Feature': features,
    'Coefficient': linear_model.coef_
})
# Sort by absolute coefficient value for importance
coefficients['Abs_Coefficient'] = coefficients['Coefficient'].abs()
coefficients = coefficients.sort_values('Abs_Coefficient', ascending=False)

print("\n=== Feature Coefficients ===")
print(coefficients)
# 9. Prediction function
def predict_fire_size(new_data):
    """
    Linear regression prediction function
    
    Parameters:
    new_data (DataFrame): Can either include day, month, year directly OR a date column
    """
    # Copy the dataframe to avoid modifying the original
    data_copy = new_data.copy()
    
    # Check if date column exists, extract features if needed
    if 'date' in data_copy.columns and not all(col in data_copy.columns for col in ['day', 'month', 'year']):
        data_copy['date'] = pd.to_datetime(data_copy['date'])
        data_copy['day'] = data_copy['date'].dt.day
        data_copy['month'] = data_copy['date'].dt.month
        data_copy['year'] = data_copy['date'].dt.year
    
    required_features = ['day', 'month', 'year', 'fmc', 'tmax', 'tmin', 'prcp', 'wind_speed', 'lat', 'lon']
    data_copy = data_copy[required_features]
    data_scaled = scaler.transform(data_copy)
    return linear_model.predict(data_scaled)

# Example usage with date:
test_sample_date = pd.DataFrame([{
    'date': '2023-07-15',
    'fmc': 103.02, 'tmax': 22.25, 'tmin': 13.3,
    'prcp': 132.0, 'wind_speed': 5.94, 'lat': 28.3, 'lon': -80.73
}])
print("\nPredicted fire size (from date):", predict_fire_size(test_sample_date)[0])

# Example usage with day, month, year:
test_sample_explicit = pd.DataFrame([{
    'day': 15, 'month': 7, 'year': 2023,
    'fmc': 103.02, 'tmax': 22.25, 'tmin': 13.3,
    'prcp': 132.0, 'wind_speed': 5.94, 'lat': 28.3, 'lon': -80.73
}])
print("Predicted fire size (explicit day/month/year):", predict_fire_size(test_sample_explicit)[0])

