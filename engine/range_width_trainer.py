"""
engine/range_width_trainer.py — Range Width ML Trainer
======================================================
Predicts how wide Nifty's range will be over the next N days.
Trains both a classifier (Tight vs Wide) and a regressor (Exact Range %).

Usage: python -m engine.range_width_trainer
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, mean_absolute_error
from datetime import datetime

# Ensure project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from engine.core import FEATURE_COLS
from engine.core import build_features

MODEL_DIR = os.path.join(ROOT_DIR, "data", "models", "range_width")
HORIZONS = [3, 5, 7, 14]
# Thresholds for 'TIGHT' classification (range < target)
THRESHOLDS = {3: 1.2, 5: 1.5, 7: 2.0, 14: 3.5}

def train_range_width_models(df, horizon=7):
    if not os.path.exists(MODEL_DIR): os.makedirs(MODEL_DIR)

    available_features = [c for c in FEATURE_COLS if c in df.columns]
    fhi_col = f"fhi_{horizon}d"
    flo_col = f"flo_{horizon}d"
    
    if fhi_col not in df.columns or flo_col not in df.columns:
        print(f"  SKIPPING {horizon}d: Missing required columns.")
        return None

    df_model = df.copy()
    # Range % = High - Low as % of entry price
    df_model['target_range'] = (df_model[fhi_col] - df_model[flo_col]) * 100
    
    # Binary Target: 1 if range < threshold (TIGHT)
    threshold = THRESHOLDS[horizon]
    df_model['target_tight'] = (df_model['target_range'] < threshold).astype(int)
    
    cols_needed = available_features + ['target_range', 'target_tight']
    if 'source' in df_model.columns: cols_needed.append('source')
    model_df = df_model[cols_needed].dropna()
    if 'source' in model_df.columns: model_df = model_df[model_df['source'] == 'real']

    if len(model_df) < 200:
        print(f"  ONLY {len(model_df)} rows — skipping.")
        return None

    X = model_df[available_features]
    y_reg = model_df['target_range']
    y_cls = model_df['target_tight']

    # --- Classifier ---
    print(f"  Training Classifier ({horizon}d, Threshold < {threshold}%)...")
    tscv = TimeSeriesSplit(n_splits=5)
    cv_accs = []
    
    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y_cls.iloc[train_idx], y_cls.iloc[test_idx]
        m = xgb.XGBClassifier(n_estimators=300, max_depth=4, learning_rate=0.03, objective='binary:logistic', random_state=42, eval_metric='logloss', early_stopping_rounds=25)
        m.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
        cv_accs.append(accuracy_score(y_test, m.predict(X_test)))
    
    final_cls = xgb.XGBClassifier(n_estimators=300, max_depth=4, learning_rate=0.03, objective='binary:logistic', random_state=42, eval_metric='logloss', early_stopping_rounds=25)
    split = int(len(X) * 0.85)
    final_cls.fit(X.iloc[:split], y_cls.iloc[:split], eval_set=[(X.iloc[split:], y_cls.iloc[split:])], verbose=False)
    
    # --- Regressor ---
    print(f"  Training Regressor ({horizon}d)...")
    cv_maes = []
    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y_reg.iloc[train_idx], y_reg.iloc[test_idx]
        m = xgb.XGBRegressor(n_estimators=300, max_depth=4, learning_rate=0.03, objective='reg:squarederror', random_state=42, eval_metric='mae', early_stopping_rounds=25)
        m.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
        cv_maes.append(mean_absolute_error(y_test, m.predict(X_test)))

    final_reg = xgb.XGBRegressor(n_estimators=300, max_depth=4, learning_rate=0.03, objective='reg:squarederror', random_state=42, eval_metric='mae', early_stopping_rounds=25)
    final_reg.fit(X.iloc[:split], y_reg.iloc[:split], eval_set=[(X.iloc[split:], y_reg.iloc[split:])], verbose=False)

    # Save
    joblib.dump(final_cls, os.path.join(MODEL_DIR, f"xgb_range_cls_{horizon}d.pkl"))
    joblib.dump(final_reg, os.path.join(MODEL_DIR, f"xgb_range_reg_{horizon}d.pkl"))
    
    # Feature Importance (Classifier)
    importance = pd.DataFrame({'feature': available_features, 'importance': final_cls.feature_importances_}).sort_values('importance', ascending=False)
    importance.to_csv(os.path.join(MODEL_DIR, f"importance_range_cls_{horizon}d.csv"), index=False)

    print(f"  OK {horizon}d -> CV Acc: {np.mean(cv_accs):.1%}, MAE: {np.mean(cv_maes):.2f}%")
    return {
        "cv_accuracy": float(np.mean(cv_accs)),
        "cv_mae": float(np.mean(cv_maes)),
        "threshold": threshold,
        "n_samples": len(X)
    }

def train_all_range_models():
    print("\n" + "="*50)
    print("TRAINING RANGE WIDTH MODELS")
    print("="*50)
    df = build_features()
    if df is None or df.empty:
        print("FAILED to load features.")
        return

    results = {}
    for h in HORIZONS:
        res = train_range_width_models(df, horizon=h)
        if res: results[h] = res
            
    import json
    summary = {"last_trained": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "horizons": results}
    with open(os.path.join(MODEL_DIR, "range_summary.json"), 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\nRange Summary saved to {MODEL_DIR}")

if __name__ == "__main__":
    train_all_range_models()
