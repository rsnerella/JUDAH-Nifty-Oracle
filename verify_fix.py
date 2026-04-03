import pandas as pd
import os

files = [
    r"C:\Users\hp\Desktop\New_ML\JUDAH-Nifty-Oracle-main\data\INDIAVIX_15minute_2001_now.csv",
    r"C:\Users\hp\Desktop\New_ML\JUDAH-Nifty-Oracle-main\data\usdinr_daily.csv"
]

for file_path in files:
    print(f"Checking {os.path.basename(file_path)}...")
    try:
        df = pd.read_csv(file_path)
        # Check for conflict markers in the whole dataframe as strings
        mask = df.apply(lambda x: x.astype(str).str.contains("<<<<<<<|=======|>>>>>>>")).any(axis=1)
        conflicts = df[mask]
        if not conflicts.empty:
            print(f"FAILED: Found conflict markers in {os.path.basename(file_path)} at rows: {conflicts.index.tolist()}")
        else:
            # Try to convert date column to datetime
            if 'date' in df.columns:
                pd.to_datetime(df['date'])
                print(f"SUCCESS: {os.path.basename(file_path)} parsed correctly.")
            else:
                print(f"WARNING: 'date' column not found in {os.path.basename(file_path)}")
    except Exception as e:
        print(f"ERROR processing {os.path.basename(file_path)}: {str(e)}")
