import pandas as pd
import logging

''' 
    This script is used for:
    - Calculate average for rows with same FIPS and date.
    - Filter out rows with NA values in any column.
'''

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the CSV file
logging.info("Loading data...")
df = pd.read_csv('./fips_wind_data.csv')
initial_rows = len(df)
logging.info(f"Initial number of rows: {initial_rows}")

# Check for duplicates before averaging
duplicates = df.groupby(['fips', 'date']).size().reset_index(name='count')
duplicates = duplicates[duplicates['count'] > 1]
logging.info(f"\nFound {len(duplicates)} FIPS-date combinations with duplicates")
if len(duplicates) > 0:
    logging.info("\nSample of duplicates:")
    print(duplicates.head())
    logging.info("\nSample of duplicate values:")
    sample_duplicates = duplicates.head(3)
    for _, row in sample_duplicates.iterrows():
        fips = row['fips']
        date = row['date']
        count = row['count']
        logging.info(f"\nFIPS: {fips}, Date: {date}, Count: {count}")
        print(df[(df['fips'] == fips) & (df['date'] == date)])

# Calculate average for rows with same FIPS and date
logging.info("\nCalculating averages for rows with same FIPS and date...")
df_averaged = df.groupby(['fips', 'date']).agg({
    'wind_speed': 'mean'
}).reset_index()

logging.info(f"Rows after averaging: {len(df_averaged)}")
logging.info(f"Removed {initial_rows - len(df_averaged)} duplicate rows")

# Check for NA values in each column
logging.info("\nChecking for NA values in each column:")
for column in df_averaged.columns:
    na_count = df_averaged[column].isna().sum()
    na_percentage = (na_count / len(df_averaged)) * 100
    logging.info(f"{column}: {na_count} NA values ({na_percentage:.2f}%)")

# Filter out rows with NA values in any column
logging.info("\nFiltering out rows with NA values...")
filtered_df = df_averaged.dropna()

# Print statistics about removed rows
removed_rows = len(df_averaged) - len(filtered_df)
removed_percentage = (removed_rows / len(df_averaged)) * 100
logging.info(f"\nRemoved {removed_rows} rows with NA values ({removed_percentage:.2f}% of total)")
logging.info(f"Remaining rows: {len(filtered_df)}")

# Save the filtered DataFrame
logging.info("\nSaving filtered data...")
filtered_df.to_csv('fips_wind_no_na_averaged.csv', index=False)
logging.info("Filtered data saved to 'fips_wind_no_na_averaged.csv'")
