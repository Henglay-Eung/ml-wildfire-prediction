import pandas as pd

# This script is used for calculating average for rows with same FIPS and date.

# Read the CSV file
df = pd.read_csv('./wildfire.csv')

# Convert date columns to datetime
df['date'] = pd.to_datetime(df['date'])
df['end_date'] = pd.to_datetime(df['end_date'])

# Store expanded fire records
expanded_rows = []

for _, row in df.iterrows():
    start_date = row['date']
    end_date = row['end_date']
    fire_size = row['FIRE_SIZE']
    fips = row['fips']
    
    # Create daily date range for this fire
    active_dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Average fire size per day
    daily_fire_size = fire_size / len(active_dates)

    for date in active_dates:
        expanded_rows.append({
            'date': date,
            'FIRE_SIZE': daily_fire_size,
            'fips': fips,
            'lon': row['lon'],
            'lat': row['lat']
        })

# Create DataFrame from expanded records
expanded_df = pd.DataFrame(expanded_rows)

# Group by FIPS and date to sum all fire sizes
aggregated_df = expanded_df.groupby(['fips', 'date'], as_index=False).agg({
    'FIRE_SIZE': 'sum',
    'lon': 'first',
    'lat': 'first'
})

# Save to CSV
aggregated_df.to_csv('aggregated_daily_fire_size.csv', index=False)

print("Aggregation complete! Saved to 'aggregated_daily_fire_size.csv'.")
