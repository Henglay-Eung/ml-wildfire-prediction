import pandas as pd
import joblib
import json

# Load the model and scaler
model = joblib.load('./training/wildfire_prediction_xgboost.pkl')
scaler = joblib.load('./training/feature_scaler.pkl')

# Load feature names
with open('./training/random_forest_feature_names.json', 'r') as f:
    feature_names = json.load(f)

# Load new data
input_csv_path = "future_weather_data_with_fuel.csv"  # Replace with your input file
df_original = pd.read_csv(input_csv_path)

# Save original index for mapping predictions back
df_original["__original_index__"] = df_original.index

# Copy and prepare for feature engineering
df = df_original.copy()
df["date"] = pd.to_datetime(df["date"])
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df["day"] = df["date"].dt.day
df["dayofyear"] = df["date"].dt.dayofyear

# Drop rows with missing values and duplicates
df_cleaned = df.dropna().drop_duplicates()

# Extract features and scale
X_input = df_cleaned[feature_names]
X_scaled = scaler.transform(X_input)

# Make predictions
predictions = model.predict(X_scaled)

# Assign predictions to the cleaned DataFrame
df_cleaned["fire_size"] = predictions

# Merge predictions back to the original DataFrame using original indices
df_result = pd.merge(
    df_original,
    df_cleaned[["__original_index__", "fire_size"]],
    on="__original_index__",
    how="left"
)

# Clean up helper column
df_result.drop(columns=["__original_index__"], inplace=True)

# Save to output CSV
output_csv_path = "predicted_fire_sizes.csv"
df_result.to_csv(output_csv_path, index=False)

print(f"Clean predictions saved to {output_csv_path}")
