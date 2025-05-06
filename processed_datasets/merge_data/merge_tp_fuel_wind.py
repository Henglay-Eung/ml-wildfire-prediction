import pandas as pd

# This script is used for merging TP, Fuel, and Wind data by FIPS and Date

# Load the data
data_df = pd.read_csv('../merge_data/merged_tp_fuel.csv')
wind_df = pd.read_csv('../../processed_datasets/wind/filled_fips_wind_data.csv')

# Convert dates to a consistent format
data_df['date'] = pd.to_datetime(data_df['date']).dt.strftime('%Y-%m-%d')
wind_df['date'] = pd.to_datetime(wind_df['date']).dt.strftime('%Y-%m-%d')

# Merge on 'date' and 'fips'
merged_df = pd.merge(data_df, wind_df, on=['date', 'fips'], how='inner')

# Keep only the required columns
merged_df = merged_df[['date', 'fmc', 'fips', 'tmax', 'tmin', 'prcp', 'wind_speed']]

# Save the merged data
merged_df.to_csv('merged_tp_fuel_wind.csv', index=False)

print(merged_df.head())
