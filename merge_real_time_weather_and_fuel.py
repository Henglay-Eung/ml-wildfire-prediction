import pandas as pd

# Load the fuel and weather data
fuel_data = pd.read_csv('./filled_fips_fuel_data.csv')
weather_data = pd.read_csv('./weather_data.csv')

# Ensure 'date' is parsed as a date object
fuel_data['date'] = pd.to_datetime(fuel_data['date']).dt.date
weather_data['date'] = pd.to_datetime(weather_data['date']).dt.date

# Step 1: Left join weather to fuel to keep all weather rows
merged_data = pd.merge(weather_data, fuel_data, on=['fips', 'date'], how='left')

# Step 2: Fill missing 'fmc' by finding the latest available for the same 'fips'
# Get the latest available FMC per fips
latest_fuel = fuel_data.sort_values('date').drop_duplicates('fips', keep='last')[['fips', 'fmc']]
latest_fuel = latest_fuel.rename(columns={'fmc': 'latest_fmc'})

# Merge latest_fuel back into merged_data
merged_data = pd.merge(merged_data, latest_fuel, on='fips', how='left')

# If original fmc is NaN, use latest_fmc
merged_data['fmc'] = merged_data['fmc'].fillna(merged_data['latest_fmc'])

# Drop the helper column
merged_data.drop(columns='latest_fmc', inplace=True)

# Save to CSV
merged_data.to_csv('future_weather_data_with_fuel.csv', index=False)

print("Filled missing fuel data and saved to 'future_weather_data_with_fuel.csv'")
print(f"Number of rows: {len(merged_data)}")
print(merged_data.head())
