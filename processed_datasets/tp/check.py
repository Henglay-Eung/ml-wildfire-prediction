import pandas as pd
import numpy as np

# Load your CSV file
df = pd.read_csv('fips_tp_no_na_averaged.csv', parse_dates=['date'])  # Adjust column names

# --- Check 1: Unique FIPS codes ---
unique_fips = df['fips'].nunique()
print(f"Total unique FIPS codes: {unique_fips}")

# --- Check 2: Date range ---
min_date, max_date = df['date'].min(), df['date'].max()
print(f"Date range: {min_date} to {max_date}")

# --- Check 3: Expected days (1992-2020 = 10,592 days) ---
all_dates = pd.date_range(start='1992-01-01', end='2020-12-31')
expected_days = len(all_dates)
print(f"Expected days per FIPS: {expected_days}")

# --- Check 4: Find FIPS with missing days ---
fips_missing_days = []
for fips in df['fips'].unique():
    fips_dates = df[df['fips'] == fips]['date']
    missing = expected_days - fips_dates.nunique()
    if missing > 0:
        fips_missing_days.append((fips, missing))

if fips_missing_days:
    print(f"\n⚠️ {len(fips_missing_days)} FIPS codes have missing days:")
    for fips, missing in fips_missing_days[:10]:  # Show first 10
        print(f"  FIPS {fips}: {missing} missing days")
else:
    print("\n✅ No missing days detected in any FIPS code.")

# --- Check 5: Duplicate entries (same FIPS + date) ---
duplicates = df.duplicated(subset=['fips', 'date'], keep=False)
if duplicates.any():
    print(f"\n⚠️ {duplicates.sum()} duplicate rows (same FIPS + date)")
else:
    print("\n✅ No duplicate FIPS-date entries.")