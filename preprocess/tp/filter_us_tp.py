import pandas as pd


# This script is used for extracting station, date, tmin (Min temperature), prcp (Precipitaion), and tmax (Max temperature) from weather data csv files


# Adjust file names accordingly
input_file = '../../datasets/tp/2019.csv'
output_file = '../../preprocess/tp/filtered_us_tp_2019.csv'

# Read the CSV file with only relevant columns
df = pd.read_csv(input_file, header=None, usecols=[0, 1, 2, 3], names=['station', 'date', 'type', 'value'])

# Filter rows where the station code starts with 'US' and type is 'PRCP', 'TMAX', 'TMIN'
filtered_df = df[
    (df['station'].str.startswith('US')) &
    (df['type'].isin(['PRCP', 'TMAX', 'TMIN']))
]

# Pivot table to merge rows with the same station and date
merged_df = filtered_df.pivot(index=['station', 'date'], columns='type', values='value').reset_index()

# Convert 'date' column to datetime format and then to 'YYYY-MM-DD' string format
merged_df['date'] = pd.to_datetime(merged_df['date'], format='%Y%m%d').dt.strftime('%Y-%m-%d')

# Reorder and keep only the desired columns
merged_df = merged_df[['station', 'date', 'TMIN', 'PRCP', 'TMAX']]

# Rename columns
merged_df = merged_df.rename(columns={'TMIN': 'tmin', 'PRCP': 'prcp', 'TMAX': 'tmax'})

# Remove rows with NaN values in 'tmin', 'prcp', or 'tmax'
merged_df = merged_df.dropna(subset=['tmin', 'prcp', 'tmax'])

# Step 1: Filter rows where 'tmin' or 'tmax' are outside the range -900 to 1000
valid_range = (-900, 1000)
merged_df = merged_df[
    (merged_df['tmin'].between(*valid_range)) &
    (merged_df['tmax'].between(*valid_range))
]

# Step 2: Convert 'tmin' and 'tmax' to normal Celsius by dividing by 10
merged_df['tmin'] = merged_df['tmin'] / 10
merged_df['tmax'] = merged_df['tmax'] / 10

# Step 3: Filter rows where 'prcp' is outside the range -100 to 1000
temp_valid_range = (-70, 60)
prcp_valid_range = (0, 1500)
merged_df = merged_df[
    (merged_df['tmin'].between(*temp_valid_range)) &
    (merged_df['tmax'].between(*temp_valid_range)) &
    (merged_df['prcp'].between(*prcp_valid_range))
]

# Export the merged data to a new CSV file
merged_df.to_csv(output_file, index=False)

print(f'Merged records exported to {output_file}')