import xarray as xr
import pandas as pd

''' 
    This script is used for:
    - Calculate wind speed: sqrt(u^2 + v^2).
    - Filter the data for the US.
'''

# File paths
u_wind_file = '../../datasets/wind/uwnd.sig995.2019.nc'
v_wind_file = '../../datasets/wind/vwnd.sig995.2019.nc'
output_file = 'wind_with_lat_lon_2019.csv'

# Load the u-wind and v-wind files
u_data = xr.open_dataset(u_wind_file, engine='h5netcdf')
v_data = xr.open_dataset(v_wind_file, engine='h5netcdf')

# Calculate wind speed: sqrt(u^2 + v^2)
wind_speed = (u_data['uwnd']**2 + v_data['vwnd']**2)**0.5

# Define latitude and longitude bounds for the US
# lat_min, lat_max = 24.5, 49.0  # Latitude range for the continental US
# lon_min, lon_max = -125.0, -66.5  # Longitude range for the continental US
lat_min, lat_max = 18.0, 72.0      # From Hawaii to Northern Alaska
lon_min, lon_max = -180.0, -66.0   # From Aleutian Islands (Alaska) to Maine

# Convert longitude to the 0°-360° range used in the dataset
lon_min = lon_min % 360
lon_max = lon_max % 360

# Filter the data for the US
us_wind_speed = wind_speed.sel(
    lat=slice(lat_max, lat_min),  # Latitude is in descending order
    lon=slice(lon_min, lon_max)
)

# Convert the xarray DataArray to a DataFrame
df = us_wind_speed.to_dataframe(name='wind_speed').reset_index()

# Convert longitude from 0°-360° to -180°-180°
df['lon'] = ((df['lon'] + 180) % 360) - 180

# Rename the 'time' column to 'date'
df = df.rename(columns={'time': 'date'})
df = df.rename(columns={'lat': 'latitude'})
df = df.rename(columns={'lon': 'longitude'})

# Save the DataFrame to a CSV file
df.to_csv(output_file, index=False)

print("Wind speed data for the US has been saved to 'us_wind_speed_2020.csv'.")