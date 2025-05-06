import pandas as pd

# Read the file (replace 'filename.txt' with your actual file name)
df = pd.read_csv('../datasets/2024_Gaz_counties_national.txt', sep='\t')

# Strip whitespace from column names
df.columns = df.columns.str.strip()

# Print the available columns for debugging
print("Available columns in the dataset:", df.columns.tolist())

# Extract the 'GEOID' column and rename it to 'fips'
df = df[['GEOID', 'INTPTLAT', 'INTPTLONG']].rename(columns={'GEOID': 'fips', 'INTPTLAT': 'lat', 'INTPTLONG': 'lon'})

# Save to a new file (optional)
df.to_csv('./all_fips_code.csv', index=False)
