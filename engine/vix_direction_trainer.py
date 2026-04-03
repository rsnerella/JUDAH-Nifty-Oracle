"""
engine/vix_direction_trainer.py — VIX Direction ML Trainer
==========================================================
Predicts if VIX will rise or fall over the next N days.
Best entry timing: sell credit spreads when VIX is about to fall.

Usage: python -m engine.vix_direction_trainer
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

MODEL_DIR = os.path.join(ROOT_DIR, "data", "models", "vix_direction")
HORIZONS = [1, 3, 5, 7]

def train_vix_direction_models(df, horizon=3):
    if not os.path.exists(MODEL_DIR): os.makedirs(MODEL_DIR)

    available_features = [c for c in FEATURE_COLS if c in df.columns]
    vix_col = 'vix'
    if vix_col not in df.columns:
        print("  SKIPPING: Missing 'vix' column.")
        return None

    df_model = df.copy()
    # Target: 1 if VIX rises, 0 if it falls
    df_model['vix_fwd'] = df_model[vix_col].shift(-horizon)
    df_model['target_vix_up'] = (df_model['vix_fwd'] > df_model[vix_col]).astype(int)
    
    cols_needed = available_features + ['target_vix_up']
    if 'source' in df_model.columns: cols_needed.append('source')
    model_df = df_model[cols_needed].dropna()
    if 'source' in model_df.columns: model_df = model_df[model_df['source'] == 'real']

    if len(model_df) < 500:
        print(f"  ONLY {len(model_df)} rows — skipping.")
        return None

    X = model_df[available_features]
    y = model_df['target_vix_up']

    # Class balance
    vix_up_freq = y.mean() * 100
    print(f"  {horizon}d VIX Up Frequency: {vix_up_freq:.1f}%")

    tscv = TimeSeriesSplit(n_splits=5)
    cv_accs = []
    
    params = {
        'n_estimators': 300,
        'max_depth': 4,
        'learning_rate': 0.03,
        'subsample': 0.8,
        'colsample_bytree': 0.7,
        'objective': 'binary:logistic',
        'random_state': 42,
        'eval_metric': 'logloss',
        'early_stopping_rounds': 25
    }

    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        
        m = xgb.XGBClassifier(**params)
        m.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
        cv_accs.append(accuracy_score(y_test, m.predict(X_test)))

    avg_acc = np.mean(cv_accs)
    print(f"  OK {horizon}d VIX Direction -> CV Acc: {avg_acc:.2%}")

    # Final Train
    split = int(len(X) * 0.85)
    final_model = xgb.XGBClassifier(**params)
    final_model.fit(X.iloc[:split], y.iloc[:split], eval_set=[(X.iloc[split:], y.iloc[split:])], verbose=False)
    
    # Save
    joblib.dump(final_model, os.path.join(MODEL_DIR, f"xgb_vix_dir_{horizon}d.pkl"))
    
    # Importance
    importance = pd.DataFrame({'feature': available_features, 'importance': final_model.feature_importances_}).sort_values('importance', ascending=False)
    importance.to_csv(os.path.join(MODEL_DIR, f"importance_vix_dir_{horizon}d.csv"), index=False)
    
    return {
        "cv_accuracy": float(avg_acc),
        "vix_up_pct": float(vix_up_freq),
        "n_samples": len(X)
    }

def train_all_vix_models():
    print("\n" + "="*50)
    print("TRAINING VIX DIRECTION MODELS")
    print("="*50)
    df = build_features()
    if df is None or df.empty:
        print("FAILED to load features.")
        return

    results = {}
    for h in HORIZONS:
        res = train_vix_direction_models(df, horizon=h)
        if res: results[h] = res
            
    import json
    summary = {
        "last_trained": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "horizons": results
    }
    with open(os.path.join(MODEL_DIR, "vix_summary.json"), 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\nVIX Summary saved to {MODEL_DIR}")

if __name__ == "__main__":
    train_all_vix_models()
