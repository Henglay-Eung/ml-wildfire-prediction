import pandas as pd

# This script is used for extracting fuel moisture content, and averaging by SiteId, and Date

# Load the CSV file
df = pd.read_csv("../../datasets/fuel/field_sample.csv")

# Filter the columns
filtered_df = df[["Date-Time (ex. 2024-01-26T00:00:00+00:00)", "SiteId", "Fuel Type", "Category", "Sample Avg Value"]]

# Rename the Date-Time column for simplicity
filtered_df = filtered_df.rename(columns={"Date-Time (ex. 2024-01-26T00:00:00+00:00)": "Date-Time"})

# Convert Date-Time to only date (YYYY-MM-DD)
filtered_df["Date"] = pd.to_datetime(filtered_df["Date-Time"]).dt.date

# Drop the original Date-Time column (optional)
filtered_df = filtered_df.drop(columns=["Date-Time"])

# Drop Fuel Type and Category columns
filtered_df = filtered_df.drop(columns=["Fuel Type", "Category"])

# Group by 'SiteId' and 'Date', then calculate the mean of 'Sample Avg Value'
grouped_df = filtered_df.groupby(["SiteId", "Date"], as_index=False)["Sample Avg Value"].mean()

# Save the grouped data to a new CSV file
grouped_df.to_csv("filtered_data_with_date_and_average.csv", index=False)

print("Filtered CSV with averaged values saved as 'filtered_data_with_date_and_average.csv'")