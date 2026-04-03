import os
import sys
import pandas as pd
import numpy as np

# Ensure the project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from engine.core import build_features

def verify_logic():
    print("🛠️ Verifying Train/Val Split Logic...")
    df = build_features()
    if df is None or df.empty:
        print("❌ FAILED: Features empty.")
        return

    # Check Date Filtering
    t_start = df['date'].min()
    t_end   = df['date'].max()
    print(f"Dataset Range: {t_start} to {t_end}")
    
    train_df = df[df['date'] < '2020-01-01']
    val_df   = df[(df['date'] >= '2020-01-01') & (df['date'] < '2025-01-01')]
    test_df  = df[df['date'] >= '2025-01-01']
    
    print(f"Train Rows (<2020): {len(train_df)}")
    print(f"Val Rows (2020-2025): {len(val_df)}")
    print(f"Test Rows (>2025): {len(test_df)}")
    
    if len(train_df) == 0 or len(val_df) == 0:
        print("❌ FAILED: Logic split returned empty sets. Check your date filter format.")
    else:
        print("✅ SUCCESS: Logic split confirmed.")

if __name__ == "__main__":
    verify_logic()
