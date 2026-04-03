import os, sys
import pandas as pd

base_dir = r"c:\Users\hp\Desktop\New_ML\JUDAH"
sys.path.insert(0, base_dir)
from engine.core import build_features, _ml_direction_score

df = build_features()
row = df.iloc[-1]
h_int = 7

try:
    direction, conf, details = _ml_direction_score(row, df, horizon=h_int)
    print("Direction:", direction)
    print("Confidence:", conf)
    print("Details type:", details["type"])
    print("Is Proxy:", details.get("is_proxy"))
except Exception as e:
    import traceback
    traceback.print_exc()
