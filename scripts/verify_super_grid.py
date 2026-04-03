import os
import sys
import pandas as pd
import numpy as np

# Ensure the project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.offline_grid_trainer import run_super_grid_search
from engine.core import build_features

def verify_super_grid():
    print("🛠️ Verifying Super Grid logic with 3-d horizon...")
    df = build_features()
    if df is None:
        print("❌ FAILED: Features empty.")
        return

    # Temporarily override GRID for a fast test (just 2 runs)
    import scripts.offline_grid_trainer as ogt
    original_grid = ogt.GRID
    ogt.GRID = {
        'n_estimators': [50],
        'max_depth': [3],
        'learning_rate': [0.1],
        'subsample': [0.8, 1.0]
    }
    
    try:
        best_p = run_super_grid_search(df, horizon=3)
        if best_p:
            print(f"✅ SUCCESS: Super Grid logic found params: {best_p}")
        else:
            print("❌ FAILED: No parameters found.")
    finally:
        ogt.GRID = original_grid # Restore original

if __name__ == "__main__":
    verify_super_grid()
