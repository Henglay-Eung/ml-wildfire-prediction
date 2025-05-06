import os
import pandas as pd
import matplotlib.pyplot as plt

def analyze_fire_count_by_precipitation_in_inches():
    file_path = 'processed_datasets/merge_data/cleaned_merged_data.csv'
    csv_file = os.path.join('static/reports', 'fire_count_prcp.csv')
    
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return


    df = pd.read_csv(file_path)
    df = df.dropna(subset=['prcp'])

    bins_mm = [0, 25, 50, 75, 100, float('inf')]

    def mm_to_inch_label(start_mm, end_mm):
        start_in = round(start_mm / 25.4, 2)
        end_in = round(end_mm / 25.4, 2)
        return f"{start_in}–{end_in}\""

    labels_inches = [
        mm_to_inch_label(0, 25),
        mm_to_inch_label(25, 50),
        mm_to_inch_label(50, 75),
        mm_to_inch_label(75, 100),
        ">3.94\""
    ]

    df['prcp_bin'] = pd.cut(df['prcp'], bins=bins_mm, labels=labels_inches, right=False)

    # Group and count number of fires per bin
    grouped = df.groupby('prcp_bin').size().reset_index(name='fire_count')

    # Save data to CSV
    grouped.to_csv(csv_file, index=False)
    print(f"Data saved to {csv_file}")

    # Plot
    plt.figure(figsize=(10, 6))
    plt.bar(grouped['prcp_bin'].astype(str), grouped['fire_count'], color='orange')
    plt.xlabel('Precipitation Range (inches)')
    plt.ylabel('Fire Count')
    plt.title('Number of Wildfires by Precipitation Range')
    plt.tight_layout()
    plt.show()
    plt.close()


# Run the updated analysis
analyze_fire_count_by_precipitation_in_inches()
