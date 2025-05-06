import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# This script is used for adding fips to the TP data by lat and long

# Load your data into a DataFrame
data = pd.read_csv("./lat_long_tp_data.csv")

# Load the U.S. county boundaries shapefile
counties = gpd.read_file("./cb_2022_us_county_500k/cb_2022_us_county_500k.shp")

# Convert your data to a GeoDataFrame
geometry = [Point(xy) for xy in zip(data["longitude"], data["latitude"])]
gdf = gpd.GeoDataFrame(data, geometry=geometry, crs="EPSG:4326") 

# Perform a spatial join to find the county for each point
gdf = gpd.sjoin(gdf, counties, how="left", predicate="within") 

# Extract relevant columns (e.g., county name and FIPS code)
gdf = gdf[["date", "tmin", "prcp", "tmax", "GEOID"]]
gdf.rename(columns={"GEOID": "fips"}, inplace=True)

# Save the updated DataFrame to a new CSV file
gdf.to_csv("fips_tp_data.csv", index=False)
print("County and FIPS Code added successfully!")