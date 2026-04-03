"""
engine/monthly_breach_trainer.py — Monthly Credit Spread Breach Trainer
========================================================================
Predicts survival of 4% OTM strikes for 21d and 30d horizons.

Usage: python -m engine.monthly_breach_trainer
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score
from datetime import datetime

# Ensure project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from engine.core import FEATURE_COLS
from engine.core import build_features

MODEL_DIR = os.path.join(ROOT_DIR, "data", "models", "monthly_breach")
BREACH_THRESHOLD_PCT = 0.04 # 4%
HORIZONS = [28]

def train_monthly_breach_models(df, horizon=28):
    if not os.path.exists(MODEL_DIR): os.makedirs(MODEL_DIR)

    available_features = [c for c in FEATURE_COLS if c in df.columns]
    flo_col = f"flo_{horizon}d"
    fhi_col = f"fhi_{horizon}d"
    
    if flo_col not in df.columns or fhi_col not in df.columns:
        print(f"  SKIPPING {horizon}d: Missing columns.")
        return None

    results = {}
    for side, target_col, is_put in [("PUT", flo_col, True), ("CALL", fhi_col, False)]:
        print(f"  Training {side} SAFETY ({horizon}d, 4%)...")
        df_model = df.copy()
        if is_put:
            df_model['target_breach'] = (df_model[target_col] > -BREACH_THRESHOLD_PCT).astype(int)
        else:
            df_model['target_breach'] = (df_model[target_col] < BREACH_THRESHOLD_PCT).astype(int)
        
        cols_needed = available_features + ['target_breach']
        if 'source' in df_model.columns: cols_needed.append('source')
        model_df = df_model[cols_needed].dropna()
        if 'source' in model_df.columns: model_df = model_df[model_df['source'] == 'real']

        if len(model_df) < 500:
            print(f"  ONLY {len(model_df)} rows — skipping {side}.")
            continue

        X = model_df[available_features]
        y = model_df['target_breach']
        
        safe_pct = y.mean() * 100
        breach_pct = 100 - safe_pct
        
        params = {
            'n_estimators': 400,
            'max_depth': 4,
            'learning_rate': 0.03,
            'scale_pos_weight': breach_pct / max(safe_pct, 1),
            'objective': 'binary:logistic',
            'random_state': 42,
            'eval_metric': 'logloss',
            'early_stopping_rounds': 25
        }

        tscv = TimeSeriesSplit(n_splits=5)
        cv_accs = []
        for train_idx, test_idx in tscv.split(X):
            X_tr, X_te = X.iloc[train_idx], X.iloc[test_idx]
            y_tr, y_te = y.iloc[train_idx], y.iloc[test_idx]
            m = xgb.XGBClassifier(**params)
            m.fit(X_tr, y_tr, eval_set=[(X_te, y_te)], verbose=False)
            cv_accs.append(accuracy_score(y_te, m.predict(X_te)))
        
        avg_acc = np.mean(cv_accs)
        print(f"  OK {side} -> CV Acc: {avg_acc:.2%}")
        
        final_model = xgb.XGBClassifier(**params)
        split = int(len(X) * 0.85)
        final_model.fit(X.iloc[:split], y.iloc[:split], eval_set=[(X.iloc[split:], y.iloc[split:])], verbose=False)
        
        model_name = f"xgb_monthly_breach_{side.lower()}_{horizon}d.pkl"
        joblib.dump(final_model, os.path.join(MODEL_DIR, model_name))
        
        results[side] = {
            "cv_accuracy": float(avg_acc),
            "safe_pct": float(safe_pct),
            "n_samples": len(X)
        }
    return results

def train_all_monthly_models():
    print("\n" + "="*50)
    print("TRAINING MONTHLY BREACH MODELS (4% THRESHOLD)")
    print("="*50)
    df = build_features()
    if df is None or df.empty:
        print("FAILED to load features.")
        return

    all_res = {}
    for h in HORIZONS:
        res = train_monthly_breach_models(df, horizon=h)
        if res: all_res[h] = res
            
    import json
    summary = {
        "last_trained": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "threshold_pct": BREACH_THRESHOLD_PCT * 100,
        "horizons": all_res
    }
    with open(os.path.join(MODEL_DIR, "monthly_breach_summary.json"), 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\nMonthly Breach Summary saved to {MODEL_DIR}")

if __name__ == "__main__":
    train_all_monthly_models()
