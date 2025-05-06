import requests
import pandas as pd
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the CSV file containing FIPS codes and their coordinates
input_csv = "./preprocess/all_fips_code.csv"
df = pd.read_csv(input_csv, usecols=["fips", "lat", "lon"])

# Filter for California counties (FIPS from 6001 to 6115)
df = df[(df['fips'] >= 6001) & (df['fips'] <= 6115)]

# Prepare an empty list for storing results
data_list = []

# Define date range: May 9 to May 20, 2025
start_date = datetime(2025, 5, 6)
end_date = datetime(2025, 5, 8)
date_range = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

logging.info("Starting to fetch weather data for California FIPS codes.")

for single_date in date_range:
    date_str = single_date.strftime('%Y-%m-%d')
    for _, row in df.iterrows():
        fips = row['fips']
        lat = row['lat']
        lon = row['lon']

        # FIPS code sanity check (optional if already filtered)
        if 1001 <= fips <= 72153:
            url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={lat}&longitude={lon}"
                f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max"
                f"&timezone=auto&start_date={date_str}&end_date={date_str}"
            )
            response = requests.get(url)
            if response.status_code != 200:
                logging.error(f"Error fetching data for FIPS {fips} on {date_str}: {response.status_code}")
                continue

            weather_data = response.json().get("daily", {})
            if not weather_data or not weather_data.get("time"):
                logging.warning(f"No weather data returned for FIPS {fips} on {date_str}")
                continue

            tmax = weather_data["temperature_2m_max"][0]
            tmin = weather_data["temperature_2m_min"][0]
            prcp = weather_data["precipitation_sum"][0]
            wind_speed = weather_data["wind_speed_10m_max"][0]

            data_list.append([date_str, fips, lat, lon, tmax, tmin, prcp, wind_speed])
            logging.info(f"Fetched data for FIPS {fips} on {date_str}: tmax={tmax}, tmin={tmin}, prcp={prcp}, wind_speed={wind_speed}")

# Convert to DataFrame
output_df = pd.DataFrame(data_list, columns=["date", "fips", "lat", "lon", "tmax", "tmin", "prcp", "wind_speed"])
print("Converted to DataFrame.")

# Save to CSV
output_csv = "weather_data_CA_2025_05_06_to_2025_05_08.csv"
output_df.to_csv(output_csv, index=False)
print("Saved to CSV.")
print(f"Weather data from May 9 to May 20 saved to '{output_csv}'")
