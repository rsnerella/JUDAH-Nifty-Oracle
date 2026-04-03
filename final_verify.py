import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add engine to path (project root derived from this file)
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from engine import core

# Mock row data
mock_row = {f: 0.0 for f in core.FEATURE_COLS}
mock_row['date'] = '2026-03-28'
mock_row['rsi'] = 55.0
mock_row['vix'] = 18.0
mock_row['close'] = 22000.0
mock_df = pd.DataFrame([mock_row])

print("--- TESTING ML LOADING ---")
for h in [3, 5, 7, 14]:
    try:
        direction, conf, raw = core._ml_direction_score(mock_row, mock_df, horizon=h)
        print(f"Horizon {h}d: {direction} ({conf:.2f}%) - Type: {raw['type']}")
    except Exception as e:
        print(f"Horizon {h}d: FAILED with error: {str(e)}")

print("\n--- TESTING ORACLE ---")
try:
    res = core.compute_oracle(horizon=7)
    print(f"Oracle Result: {res['direction']} ({res['confidence']:.2f}%)")
    print(f"Strategy: {res['strategy']['strategy']}")
    print(f"ML Source: {res['engine_ml']['raw']['type']}")
except Exception as e:
    print(f"Oracle FAILED with error: {str(e)}")
