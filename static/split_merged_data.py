import pandas as pd
import os

def split_csv_by_year(input_file):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_file)
    
    # Extract year from the 'date' column
    df['year'] = pd.to_datetime(df['date']).dt.year
    
    # Group by year
    grouped = df.groupby('year')
    
    # Create output directory if it doesn't exist
    os.makedirs('output_by_year', exist_ok=True)
    
    # Save each group to a separate CSV file
    for year, group in grouped:
        output_file = f'output_by_year/merged_data_{year}.csv'
        group.drop('year', axis=1).to_csv(output_file, index=False)
        print(f"Created file: {output_file} with {len(group)} rows")

# Example usage
split_csv_by_year('merged_data.csv')