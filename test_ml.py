import os, sys
import pandas as pd
import joblib

base_dir = r"c:\Users\hp\Desktop\New_ML\JUDAH"
sys.path.insert(0, base_dir)
from engine.core import build_features

df = build_features()
row = df.iloc[-1]
h_int = 7
model_path = os.path.join(base_dir, "data", "models", f"xgb_direction_{h_int}d.pkl")

try:
    model = joblib.load(model_path)
    if hasattr(model, "feature_names_in_"):
        active_features = model.feature_names_in_
    else:
        active_features = [f for f in ['rsi'] if f in row.index] # Just dummy fallback
        
    features = [float(row.get(f, 0) or 0) for f in active_features]
    X = pd.DataFrame([features], columns=active_features)
    probs_raw = model.predict_proba(X)[0]
    print(f"Prediction successful! UP: {probs_raw[1]:.2%}")
except Exception as e:
    import traceback
    traceback.print_exc()
