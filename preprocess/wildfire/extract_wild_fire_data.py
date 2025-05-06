import sqlite3
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# This script is used to extract wildfire data, and assiging FIPS to missing data

# Path to your SQLite database
db_path = '../../datasets/wildfire/FPA_FOD_20221014.sqlite'

# Connect to the SQLite database
conn = sqlite3.connect(db_path)

# SQL query to fetch data
query = """
SELECT DISCOVERY_DATE, LATITUDE, LONGITUDE, FIPS_CODE, FIRE_SIZE, FIRE_SIZE_CLASS, STATE, CONT_DATE
FROM Fires;
"""

# Load query result into DataFrame
df = pd.read_sql_query(query, conn)

# Close DB connection
conn.close()

# Convert date columns to datetime
df['DISCOVERY_DATE'] = pd.to_datetime(df['DISCOVERY_DATE'], errors='coerce')
df['CONT_DATE'] = pd.to_datetime(df['CONT_DATE'], errors='coerce')

# Use DISCOVERY_DATE as end_date if CONT_DATE is null
df['end_date'] = df['CONT_DATE'].fillna(df['DISCOVERY_DATE'])

# State abbreviation to FIPS code map
state_fips_map = {
    'AL': '01', 'AK': '02', 'AZ': '04', 'AR': '05', 'CA': '06', 'CO': '08', 'CT': '09', 
    'DE': '10', 'FL': '12', 'GA': '13', 'HI': '15', 'ID': '16', 'IL': '17', 'IN': '18', 
    'IA': '19', 'KS': '20', 'KY': '21', 'LA': '22', 'ME': '23', 'MD': '24', 'MA': '25', 
    'MI': '26', 'MN': '27', 'MS': '28', 'MO': '29', 'MT': '30', 'NE': '31', 'NV': '32', 
    'NH': '33', 'NJ': '34', 'NM': '35', 'NY': '36', 'NC': '37', 'ND': '38', 'OH': '39', 
    'OK': '40', 'OR': '41', 'PA': '42', 'RI': '44', 'SC': '45', 'SD': '46', 'TN': '47', 
    'TX': '48', 'UT': '49', 'VT': '50', 'VA': '51', 'WA': '53', 'WV': '54', 'WI': '55', 
    'WY': '56'
}

# Construct full FIPS code
df['FIPS_CODE'] = df.apply(
    lambda row: state_fips_map.get(row['STATE'], '') + str(row['FIPS_CODE']).zfill(3)
    if pd.notna(row['STATE']) and pd.notna(row['FIPS_CODE'])
    else None,
    axis=1
)

# Load U.S. county shapefile
counties = gpd.read_file("../../preprocess/tp/cb_2022_us_county_500k/cb_2022_us_county_500k.shp")

# Convert to GeoDataFrame
geometry = [Point(xy) for xy in zip(df["LONGITUDE"], df["LATITUDE"])]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

# Spatial join with counties
gdf = gpd.sjoin(gdf, counties, how="left", predicate="within")

# Select and rename columnsa
gdf = gdf[["DISCOVERY_DATE", "FIRE_SIZE", "GEOID", "LONGITUDE", "LATITUDE", "end_date"]]
gdf.rename(columns={
    "DISCOVERY_DATE": "date",
    "GEOID": "fips",
    "LONGITUDE": "lon",
    "LATITUDE": "lat"
}, inplace=True)

# Save result
gdf.to_csv("wildfire.csv", index=False)
print("County and FIPS Code added successfully with fallback for end_date!")
