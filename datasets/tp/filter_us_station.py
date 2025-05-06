import pandas as pd

# This script is used for extracting US TP station  'station', 'latitude', 'longitude', 'elevation', 'state', 'name'

# File path for the station data
station_file = './ghcnd-stations.csv' 
output_file = './filtered_us_stations.csv'

# Define column names
column_names = ['station', 'latitude', 'longitude', 'elevation', 'state', 'name']

# Load the station data with error handling to skip rows with mismatched columns
station_df = pd.read_csv(station_file, header=None, names=column_names, on_bad_lines='skip')

# Filter for rows where the 'station' starts with 'US'
filtered_station_df = station_df[station_df['station'].str.startswith('US')]

# Export the filtered data to a new CSV file
filtered_station_df.to_csv(output_file, index=False)

print(f'Filtered data exported to {output_file}')