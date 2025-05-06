import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def extract_2020_data(input_file, output_file):
    """
    Extract rows from merged_data.csv that correspond to the year 2020.
    
    Parameters:
    -----------
    input_file : str
        Path to the input CSV file containing merged data
    output_file : str
        Path to save the output CSV file with only 2020 data
    """
    try:
        # Load the data
        logging.info(f"Loading data from {input_file}")
        
        # Use chunksize to handle large files efficiently
        chunk_size = 100000  # Adjust based on available memory
        chunks = pd.read_csv(input_file, chunksize=chunk_size)
        
        # Create an empty list to store 2020 data
        data_2020 = []
        
        # Process each chunk
        for i, chunk in enumerate(chunks):
            logging.info(f"Processing chunk {i+1}")
            
            # Convert date column to datetime if it's not already
            if 'date' in chunk.columns:
                chunk['date'] = pd.to_datetime(chunk['date'])
                
                # Filter for 2020
                chunk_2020 = chunk[
                    (chunk['date'].dt.year == 2020) |
                    (chunk['date'].dt.year == 2018) |
                    (chunk['date'].dt.year == 2019)
                ]
                # Append to the list
                data_2020.append(chunk_2020)
                
                logging.info(f"Found {len(chunk_2020)} rows from 2020 in chunk {i+1}")
            else:
                logging.warning("No 'date' column found in the data")
        
        # Combine all chunks
        if data_2020:
            df_2020 = pd.concat(data_2020, ignore_index=True)
            
            # Sort by date
            if 'date' in df_2020.columns:
                df_2020 = df_2020.sort_values('date')
            
            # Save to CSV
            df_2020.to_csv(output_file, index=False)
            logging.info(f"Saved 2020 data to {output_file}")
            
            # Print some statistics
            logging.info(f"Total rows in 2020 data: {len(df_2020)}")
            
            # Print sample data
            logging.info("Sample of 2020 data:")
            print(df_2020.head())
            
            return df_2020
        else:
            logging.warning("No data from 2020 found")
            return None
    
    except Exception as e:
        logging.error(f"Error extracting 2020 data: {str(e)}")
        return None

if __name__ == "__main__":
    # Define input and output file paths
    input_file = "merged_data.csv"
    output_file = "merged_data_2020.csv"
    
    # Extract 2020 data
    df_2020 = extract_2020_data(input_file, output_file)
    
    if df_2020 is not None:
        # Print some basic statistics
        print("\nBasic statistics for 2020 data:")
        print(f"Number of rows: {len(df_2020)}")
        print(f"Number of columns: {len(df_2020.columns)}")
        print(f"Columns: {', '.join(df_2020.columns)}")
        
        # Check for missing values
        missing_values = df_2020.isnull().sum()
        print("\nMissing values per column:")
        print(missing_values[missing_values > 0])
        
        # Check date range
        if 'date' in df_2020.columns:
            min_date = df_2020['date'].min()
            max_date = df_2020['date'].max()
            print(f"\nDate range: {min_date} to {max_date}")
        
        # Check for FIRE_SIZE distribution
        if 'FIRE_SIZE' in df_2020.columns:
            print("\nFIRE_SIZE statistics:")
            print(df_2020['FIRE_SIZE'].describe())
            
            # Count zeros
            zero_count = (df_2020['FIRE_SIZE'] == 0).sum()
            print(f"Number of zeros in FIRE_SIZE: {zero_count} ({zero_count/len(df_2020)*100:.2f}%)") 