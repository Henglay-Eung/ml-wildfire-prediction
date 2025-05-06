import pandas as pd

# This script is used for extracting and adding lat and long from the station data to the TP data 

# Load the station data into a DataFrame
station_data = pd.read_csv("../../datasets/tp/filtered_us_stations.csv") 

# Load the TP data into a DataFrame
tp_data = pd.read_csv("../tp/filtered_us_tp.csv")

# Merge the two datasets on the 'station' column
merged_data = pd.merge(
    tp_data,
    station_data[["station", "latitude", "longitude", "elevation", "state", "name"]],
    how="left",
    on="station"
)

# Save the merged data to a new CSV file
merged_data.to_csv("lat_long_tp_data.csv", index=False)
print("Data merged successfully!")