import pandas as pd

# Load your CSV file
filename = "processed_datasets/merge_data/merged_data.csv"  # <-- Change this to your actual file name
df = pd.read_csv(filename)

# Remove rows where fire_size > 5000
df_cleaned = df[df['fire_size'] <= 1000]

# Save the cleaned data to a new CSV file
output_filename = "cleaned_merged_data.csv"  # Specify the new file name
df_cleaned.to_csv(output_filename, index=False)

# Print a success message
print(f"✅ Cleaned data saved to '{output_filename}'")
