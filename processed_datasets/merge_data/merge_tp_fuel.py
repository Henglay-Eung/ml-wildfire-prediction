import pandas as pd

# This script is used for merging TP with Fuel data by FIPS and Date

# Load the data
tp_df = pd.read_csv('../../processed_datasets/tp/fips_tp_no_na_averaged.csv', dtype={'fips': str})
fuel_df = pd.read_csv('../../processed_datasets/fuel/filled_fips_fuel_data.csv', dtype={'fips': str})

# Convert dates to a consistent format (YYYY-MM-DD)
tp_df['date'] = pd.to_datetime(tp_df['date'], format='%Y-%m-%d').dt.strftime('%Y-%m-%d')
fuel_df['date'] = pd.to_datetime(fuel_df['date'], format='%Y-%m-%d').dt.strftime('%Y-%m-%d')

tp_df['fips'] = tp_df['fips'].str.replace(r'\.0$', '', regex=True)
fuel_df['fips'] = fuel_df['fips'].str.replace(r'\.0$', '', regex=True)

# Merge on 'date' and 'fips'
merged_df = pd.merge(fuel_df, tp_df, on=['date', 'fips'], how='inner')

# Keep only the required columns
merged_df = merged_df[['date', 'fmc', 'fips', 'tmax', 'tmin', 'prcp']]

# **Find the average of rows with the same date and fips**
averaged_df = merged_df.groupby(['date', 'fips'], as_index=False).mean()

# Save the averaged data
averaged_df.to_csv('merged_tp_fuel.csv', index=False)

print(averaged_df.head())
