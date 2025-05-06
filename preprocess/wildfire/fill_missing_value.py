import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import logging

''' 
    This script is used for adding 0 to wildfire column if one FIPS is missing data at some date.
    For example, if FIPS 10011 is missing data at 1992-01-01, the wildfire size at FIPS 10011 and 1992-01-01 is 0
'''

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def fill_missing_dates(input_file, output_file, start_date='1992-01-01', end_date='2020-12-31'):
    """
    Fill missing dates with zeros for each FIPS code in the wildfire dataset.
    
    Parameters:
    -----------
    input_file : str
        Path to the input CSV file containing wildfire data
    output_file : str
        Path to save the output CSV file with filled missing dates
    start_date : str
        Start date in 'YYYY-MM-DD' format
    end_date : str
        End date in 'YYYY-MM-DD' format
    """
    try:
        # Load the data
        logging.info(f"Loading data from {input_file}")
        df = pd.read_csv(input_file)
        
        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Get unique FIPS codes
        fips_codes = df['fips'].unique()
        logging.info(f"Found {len(fips_codes)} unique FIPS codes")
        
        # Create date range
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        logging.info(f"Created date range from {start_date} to {end_date} with {len(date_range)} days")
        
        # Create a dictionary to store FIPS coordinates
        fips_coords = {}
        for fips in fips_codes:
            # Get the first occurrence of this FIPS code to extract coordinates
            fips_data = df[df['fips'] == fips].iloc[0]
            fips_coords[fips] = (fips_data['lon'], fips_data['lat'])
        
        # Create a new dataframe to store the filled data
        filled_data = []
        
        # Process each FIPS code
        for i, fips in enumerate(fips_codes):
            logging.info(f"Processing FIPS code {fips} ({i+1}/{len(fips_codes)})")
            
            # Get data for this FIPS code
            fips_data = df[df['fips'] == fips].copy()
            
            # Create a dictionary of existing dates and their fire sizes
            existing_dates = {}
            for _, row in fips_data.iterrows():
                existing_dates[row['date']] = row['FIRE_SIZE']
            
            # Get coordinates for this FIPS code
            lon, lat = fips_coords[fips]
            
            # Fill missing dates with zeros
            for date in date_range:
                if date in existing_dates:
                    # Use existing data
                    filled_data.append({
                        'fips': fips,
                        'date': date,
                        'FIRE_SIZE': existing_dates[date],
                        'lon': lon,
                        'lat': lat
                    })
                else:
                    # Fill with zero
                    filled_data.append({
                        'fips': fips,
                        'date': date,
                        'FIRE_SIZE': 0,
                        'lon': lon,
                        'lat': lat
                    })
        
        # Convert to dataframe
        filled_df = pd.DataFrame(filled_data)
        
        # Sort by FIPS and date
        filled_df = filled_df.sort_values(['fips', 'date'])
        
        # Save to CSV
        filled_df.to_csv(output_file, index=False)
        logging.info(f"Saved filled data to {output_file}")
        
        # Print some statistics
        total_records = len(filled_df)
        zero_records = len(filled_df[filled_df['FIRE_SIZE'] == 0])
        non_zero_records = total_records - zero_records
        
        logging.info(f"Total records: {total_records}")
        logging.info(f"Zero records: {zero_records} ({zero_records/total_records*100:.2f}%)")
        logging.info(f"Non-zero records: {non_zero_records} ({non_zero_records/total_records*100:.2f}%)")
        
        return filled_df
    
    except Exception as e:
        logging.error(f"Error filling missing dates: {str(e)}")
        return None

if __name__ == "__main__":
    # Define input and output file paths
    input_file = "aggregated_daily_fire_size.csv"
    output_file = "aggregated_daily_fire_size_filled.csv"
    
    # Fill missing dates
    filled_df = fill_missing_dates(input_file, output_file)
    
    if filled_df is not None:
        # Display a sample of the filled data
        print("\nSample of filled data:")
        print(filled_df.head(10))
        
        # Check for a specific FIPS code
        sample_fips = filled_df['fips'].iloc[0]
        sample_data = filled_df[filled_df['fips'] == sample_fips].head(10)
        print(f"\nSample data for FIPS code {sample_fips}:")
        print(sample_data) 
    