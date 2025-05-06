import pandas as pd

# This script is used for merging TP, Fuel, Wind, and Wildfire data by FIPS and Date

# Load the data
data_df = pd.read_csv('../merge_data/merged_tp_fuel_wind.csv')
fire_df = pd.read_csv('../../processed_datasets/wildfire/aggregated_daily_fire_size_filled.csv')

# Convert FIPS_CODE in fire data to integer to match format in data
fire_df = fire_df.dropna(subset=['fips'])
fire_df['fips'] = fire_df['fips'].astype(int)

data_df['fips'] = data_df['fips'].astype(int)

# Merge data on both 'fips' and 'date'
merged_df = pd.merge(data_df, fire_df, on=['fips', 'date'], how='inner')

# Print columns after merge to verify
print("Columns in merged_df:", fire_df.columns.tolist())

# Keep only the required columns
merged_df = merged_df[['date', 'fmc', 'fips', 'tmax', 'tmin', 'prcp', 'wind_speed', 'FIRE_SIZE', 'lat', 'lon']]
merged_df = merged_df.rename(columns={'FIRE_SIZE': 'fire_size'})

# Save the merged data
merged_df.to_csv('merged_data.csv', index=False)

print(merged_df.head())