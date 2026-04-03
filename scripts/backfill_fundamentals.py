import pandas as pd
import numpy as np
import os

def backfill(data_dir):
    nifty_path = os.path.join(data_dir, "nifty_daily.csv")
    out_path = os.path.join(data_dir, "fundamentals.csv")
    
    if not os.path.exists(nifty_path):
        print(f"ERROR: {nifty_path} not found.")
        return

    print(f"Processing {nifty_path}...")
    df = pd.read_csv(nifty_path)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    # Formula: Price relative to its long-term (200d) normalization
    # Historically, Nifty PE is ~22-23 when trading at its SMA200.
    # When it's 2 standard deviations above, PE is ~28+.
    # When it's 2 standard deviations below, PE is ~18-.
    
    ma200 = df['close'].rolling(200, min_periods=50).mean()
    std200 = df['close'].rolling(200, min_periods=50).std()
    
    z_score = (df['close'] - ma200) / (std200 + 1e-9)
    z_score = z_score.fillna(0) # Start neutral
    
    # Map Z-Score to PE Range [16.5, 30.5]
    # Median 22.5 + (Z * 3.5)
    pe_proxy = 22.5 + (z_score * 3.5)
    
    # Hard Caps (Historical Extreme Bounds)
    pe_proxy = pe_proxy.clip(16.5, 30.5)
    
    # Create Fundamentals DF
    fund_df = pd.DataFrame({
        'date': df['date'],
        'pe_ratio': np.round(pe_proxy, 4)
    })
    
    fund_df.to_csv(out_path, index=False)
    print(f"SUCCESS: Saved {len(fund_df)} rows to {out_path}")

if __name__ == "__main__":
    # Backfill JUDAH
    backfill(r"c:\Users\hp\Desktop\New_ML\JUDAH-Nifty-Oracle-main\data")
    
    # Backfill MOSES
    backfill(r"c:\Users\hp\Desktop\New_ML\Moses-RandomForest\data")
