import os, sys
import pandas as pd
import joblib

base_dir = r"c:\Users\hp\Desktop\New_ML\JUDAH"
sys.path.insert(0, base_dir)
from engine.core import build_features, FEATURE_COLS

df = build_features()
row = df.iloc[-1]
h_int = 7
model_path = os.path.join(base_dir, "data", "models", f"xgb_direction_{h_int}d.pkl")
imp_path = os.path.join(base_dir, "data", "models", f"importance_{h_int}d.csv")

try:
    model = joblib.load(model_path)
    if hasattr(model, "feature_names_in_"):
        active_features = model.feature_names_in_
    else:
        active_features = [f for f in FEATURE_COLS if f in row.index]
        
    features = [float(row.get(f, 0) or 0) for f in active_features]
    X = pd.DataFrame([features], columns=active_features)
    
    probs_raw = model.predict_proba(X)[0]
    prob_up = probs_raw[1]
    
    # Extract Local Drivers
    drivers = []
    if os.path.exists(imp_path):
        import numpy as np
        imp_df = pd.read_csv(imp_path)
        if not imp_df.empty:
            top_features = imp_df.head(6).to_dict('records')
            for f_info in top_features:
                fname = f_info['feature']
                val = float(row.get(fname, 0) or 0)
                label = fname.replace("_z", "").replace("_"," ").title()
                
                icon = "⬜"; sentiment = "Neutral"
                if fname in ['fii_z', 'trend', 'rsi', 'intraday_trend', 'ret_3d']:
                    sentiment = "Bullish" if val > 0 else "Bearish"
                    icon = "🟩" if val > 0 else "🟥"
                elif fname in ['vix', 'vix_change', 'pcr_z', 'z20']:
                    sentiment = "Bearish" if val > 0 else "Bullish"
                    icon = "🟥" if val > 0 else "🟩"
                
                drivers.append({"feature": label, "value": f"{val:.2f}", "icon": icon, "sentiment": sentiment})
                
    direction = "UP" if prob_up > 0.50 else "DOWN"
    confidence = prob_up * 100 if direction == "UP" else (1 - prob_up) * 100
    
    probs = [1 - prob_up, 0.0, prob_up]
    
    print(direction, confidence)
except Exception as e:
    import traceback
    traceback.print_exc()
