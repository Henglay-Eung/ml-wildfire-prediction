import pandas as pd
import numpy as np
import logging

''' 
    This script is used for adding the missing value. For example, if FIPS 10010 is missing at 1992-01-01,
    the script will find data from 10009, 10011 and etc at 1992-01-01
'''

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Read the complete list of FIPS codes
logging.info("Loading complete FIPS code list...")
all_fips_df = pd.read_csv('../all_fips_code.csv')
all_fips_df['fips'] = all_fips_df['fips'].astype(int)  # Convert to integer
logging.info(f"Loaded {len(all_fips_df)} FIPS codes")

# Read the CSV file into a DataFrame
logging.info("Loading wind data...")
df = pd.read_csv('./fips_wind_no_na_averaged.csv')
df['fips'] = df['fips'].astype(int)  # Convert to integer
logging.info(f"Loaded {len(df)} wind data points")

# Ensure the date column is in datetime format
logging.info("Converting date format...")
df['date'] = pd.to_datetime(df['date'])

# Ensure the wind_speed column is numeric
logging.info("Converting wind speed to numeric...")
df['wind_speed'] = pd.to_numeric(df['wind_speed'], errors='coerce')

# Create a full date range for the target year
logging.info("Creating date range...")
full_date_range = pd.date_range(start='1992-01-01', end='2020-12-31')
logging.info(f"Created date range from {full_date_range[0]} to {full_date_range[-1]}")

# Get all FIPS codes from the complete list
all_fips = all_fips_df['fips'].unique()
logging.info(f"Found {len(all_fips)} unique FIPS codes")

# Create all (fips, date) combinations using the complete FIPS list
logging.info("Creating FIPS and date combinations...")
all_combinations = pd.MultiIndex.from_product(
    [all_fips, full_date_range], names=['fips', 'date']
).to_frame(index=False)

# Convert 'date' column in all_combinations to datetime format
all_combinations['date'] = pd.to_datetime(all_combinations['date'])

# Merge with existing data to identify missing values
logging.info("Merging data...")
combined = all_combinations.merge(df, on=['fips', 'date'], how='left')

# Print initial statistics
logging.info(f"Total combinations: {len(combined)}")
logging.info(f"Missing values before filling: {combined['wind_speed'].isna().sum()}")

# Step 1: Fill missing data using the nearest value within the same fips
logging.info("Step 1: Filling missing values within same FIPS...")
combined['wind_speed'] = combined.groupby('fips')['wind_speed'].transform(
    lambda x: x.interpolate(method='nearest', limit_direction='both')
)

# Step 2: If still missing, try nearby fips values (within ±10 range)
missing_after_step1 = combined['wind_speed'].isna().sum()
if missing_after_step1 > 0:
    logging.info(f"Step 2: Filling {missing_after_step1} remaining missing values using nearby FIPS...")
    
    # Create a copy of the original data for nearby FIPS lookup
    nearby_fips = pd.concat(
        [df.assign(fips=df['fips'] + i) for i in range(-10, 11) if i != 0]
    ).sort_values(by=['fips', 'date'])

    # Convert 'date' column in nearby_fips to datetime format
    nearby_fips['date'] = pd.to_datetime(nearby_fips['date'])

    # Fill missing values using nearby FIPS
    missing_mask = combined['wind_speed'].isna()
    missing_data = combined[missing_mask].sort_values(by='date')
    
    if len(missing_data) > 0:
        fallback_filled = pd.merge_asof(
            missing_data,
            nearby_fips.sort_values(by='date'),
            on='date',
            by='fips',
            direction='nearest'
        )
        
        # Update only the missing values
        combined.loc[missing_mask, 'wind_speed'] = fallback_filled['wind_speed_y']

# Step 3: Fill any remaining missing values using overall mean for that date
remaining_missing = combined['wind_speed'].isna().sum()
if remaining_missing > 0:
    logging.info(f"Step 3: Filling {remaining_missing} remaining missing values with daily means...")
    combined['wind_speed'] = combined['wind_speed'].fillna(
        combined.groupby('date')['wind_speed'].transform('mean')
    )

# Finalize and sort data
logging.info("Finalizing data...")
filled_df = combined.sort_values(by=['fips', 'date']).reset_index(drop=True)

# Verify data completeness for each FIPS
logging.info("\nVerifying data completeness...")
fips_completeness = filled_df.groupby('fips').apply(
    lambda x: (x['date'].min() == full_date_range[0]) and 
              (x['date'].max() == full_date_range[-1]) and 
              (len(x) == len(full_date_range))
).reset_index(name='complete')

incomplete_fips = fips_completeness[fips_completeness['complete'] == False]['fips'].tolist()
if incomplete_fips:
    logging.warning(f"Found {len(incomplete_fips)} FIPS codes with incomplete data:")
    print(sorted(incomplete_fips))
else:
    logging.info("All FIPS codes have complete data for 2020")

# Verify all FIPS codes are present
final_fips = set(filled_df['fips'].unique())
all_fips_set = set(all_fips)
missing_final = all_fips_set - final_fips

logging.info("\nFinal Statistics:")
logging.info(f"Total FIPS codes in final data: {len(final_fips)}")
logging.info(f"Total FIPS codes in complete list: {len(all_fips_set)}")
logging.info(f"Missing FIPS codes in final data: {len(missing_final)}")
logging.info(f"Total days per FIPS: {len(full_date_range)}")
logging.info(f"Total records: {len(filled_df)}")

if missing_final:
    logging.warning("\nMissing FIPS codes:")
    print(sorted(list(missing_final)))

# Save to CSV
logging.info("Saving results...")
filled_df.to_csv('./filled_fips_wind_data.csv', index=False)
logging.info("Data saved to 'filled_fips_wind_data.csv'")
