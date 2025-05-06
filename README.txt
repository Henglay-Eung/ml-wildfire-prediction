Install the required libraries: "pip install -r libraries.txt" 

FIPS Code data:
- Download:
    - 2024_Gaz_counties_national.txt: FIPS data from https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html
- Run:
    - preprocess/extract_fips.py to extract fips.

TP data:
- Download:
    - TP Data from 1992 to 2020 from https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ncdc:C00861. Extract by using command gunzip 2020.csv.gz
    - ghcnd-stations.csv: Station data from https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.csv
    - cb_2022_us_county_500k: For finding FIPS by Latitude and Longitude from https://catalog.data.gov/dataset/2022-cartographic-boundary-file-shp-current-county-and-equivalent-for-united-states-1-500000
- Run: 
    - Run preprocess/tp/filter_us_tp.py to filter for US and clean tp data. Since I do not have enough space, I maually run the script on data from 1992 to 2020, merge the result, and deleted the original files on by one after each process.
    - Run datasets/tp/filter_us_stations to filter for US stations data.
    - Run preprocess/tp/add_lat_long_to_tp.py to add latitude and longitude to TP data.
    - Run preprocess/tp/add_fips_to_tp.py to add FIPS to TP data.
    - Run preprocess/tp/filter_without_na.py to filter TP data without FIPS.
    - Run preprocess/tp/fill_missing_value.py to add fill data that is missing based on date and FIPS. (Out of memory)

Wind data:
- Download:
    - uwnd.sig995.2025.nc and vwnd.sig995.2025.nc (1992-2025): Wind data from https://downloads.psl.noaa.gov/Datasets/ncep.reanalysis/Dailies/surface/
- Run: 
    - Run preprocess/wind/extract_u_v_and_calculate_wind_speed.py to extract u and v wind and calculate wind speed.
    - Run preprocess/wind/add_fips_to_wind.py to add fips to Wind data.
    - Run preprocess/wind/filter_data_without_fips_and_avg.py to filter data that does not contain fips and calculate mean of wind speed of each county.
    - Run preprocess/wind/assign_missing_wind.py to add missing wind data.

Fuel data:
- Download:
    - field_sample.csv: Fuel data from https://fems.fs2c.usda.gov/download. Select all sites and filter filter.
    - site_metadata.csv: Fuel data from https://fems.fs2c.usda.gov/download for adding site latitude and longitude.
- Run: 
    - Run preprocess/fuel/filter_fuel.py to filter unneccessary data.
    - Run preprocess/fuel/add_lat_long_fuel.py to add lat and long to fuel data.
    - Run preprocess/fuel/add_fips_fuel.py to add fips to fuel data.
    - Run preprocess/fuel/fill_missing_value.py to add missing fuel data.


Wildfire data:
- Download:
    - FPA_FOD_20170508.sqlite: Wildfire data from 1992 to 2020 from https://www.fs.usda.gov/rds/archive/catalog/RDS-2013-0009.6
- Run:
    - Run preprocess/wildfire/extract_wild_fire_data.py to extract wildfire data
    - Run preprocess/wildfire/find_avg_wildfire.py to calculate average fire size in a fips.
    - Run preprocess/wildfire/fill_missing_value.py to add missing wildfire data.

Merged data:
    - Run processed_datasets/merge_data/merge_tp_fuel.py: To merge TP and Fuel data by fips and date
    - Run processed_datasets/merge_data/merge_tp_fuel_wind.py: To merge TP, Fuel, and Wind data by fips and date
    - Run processed_datasets/merge_data/merge_tp_fuel_wind_fire.py: To merge TP, Fuel, Wind, and wildfire data by fips and date
    - Run processed_datasets/merge_data/remove_outliers.py: To remove  outliers from the merged data

Training models:
    - Run training/train_linear_gression.py: To train a model using LinearRegression algorithm
    - Run training/train_xgboost.py: To train a model using eXtreme Gradient Boosting algorithm
    - Run training/train_random_forest.py: To train a model using RandomForest algorithm
    - Run training/train_xgboost_tuning.py: To tune a model using eXtreme Gradient Boosting algorithm
    - Run training/train_xgboost_best_params.py: To train a model using eXtreme Gradient Boosting algorithm and best paramters received from tuning

Obtain real time data:
    - Run obtain_real_time_weather_data.py: To get real-time weather for prediction
    - Run merge_real_time_weather_data_and_fuel: To merge weather data with fuel for prediction

Prediction:
    - Run predict.py to run prediction on the real-time weather data
    - Move predicted_fire_sizes.csv to /static

Backend:
    - Move future_weather_data_with_fuel.csv to /static
    - Move predicted_fire_size.csv to /static
    - Move merged_data.csv to /static
    - Run static/split_merged_data.py: To split data for each year for performance
    - Run backend.py to run the app
