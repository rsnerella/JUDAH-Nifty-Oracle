"""
engine/pcr_reversal_trainer.py — PCR Reversal Predictor Trainer
==============================================================
Detects high-probability mean-reversion points when the Put-Call Ratio (PCR) hits extremes.
"Contrarian edge" for entry timing.

Usage: python -m engine.pcr_reversal_trainer
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, precision_score
from datetime import datetime

# Ensure project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from engine.core import build_features, FEATURE_COLS

MODEL_DIR = os.path.join(ROOT_DIR, "data", "models", "pcr_reversal")
HORIZONS = [3, 5, 7]

def train_pcr_reversal_model(df, horizon=5):
    if not os.path.exists(MODEL_DIR): 
        os.makedirs(MODEL_DIR)

    available_features = [c for c in FEATURE_COLS if c in df.columns]
    
    df_model = df.copy()
    
    # 1. Target Construction: Success of a contrarian move
    # Thresholds for 'EXTREME'
    hi_pcr = df_model['pcr_z'] > 1.5
    lo_pcr = df_model['pcr_z'] < -1.5
    
    fwd_ret = df_model[f'fwd_{horizon}d']
    
    # Successful Bullish Reversal: PCR was high AND market went UP
    bull_rev = hi_pcr & (fwd_ret > 0.005)
    # Successful Bearish Reversal: PCR was low AND market went DOWN
    bear_rev = lo_pcr & (fwd_ret < -0.005)
    
    df_model['target_reversal'] = (bull_rev | bear_rev).astype(int)
    
    # Drop rows where target is NaN
    cols_needed = available_features + ['target_reversal']
    model_df = df_model[cols_needed].dropna()
    
    rev_freq = model_df['target_reversal'].mean() * 100
    print(f"\n  [PIVOT] Training PCR Reversal Predictor ({horizon}d)")
    print(f"  Reversal Success Freq: {rev_freq:.2f}%")

    X = model_df[available_features]
    y = model_df['target_reversal']

    tscv = TimeSeriesSplit(n_splits=5)
    cv_accs = []
    
    params = {
        'n_estimators': 300,
        'max_depth': 4,
        'learning_rate': 0.03,
        'subsample': 0.8,
        'colsample_bytree': 0.7,
        'scale_pos_weight': (100 - rev_freq) / max(rev_freq, 1),
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
    print(f"  CV Accuracy: {avg_acc:.1%}")

    # Final Train
    split = int(len(X) * 0.85)
    final_model = xgb.XGBClassifier(**params)
    final_model.fit(X.iloc[:split], y.iloc[:split], eval_set=[(X.iloc[split:], y.iloc[split:])], verbose=False)
    
    # Save
    model_path = os.path.join(MODEL_DIR, f"xgb_pcr_rev_{horizon}d.pkl")
    joblib.dump(final_model, model_path)
    
    # Importance
    imp = pd.DataFrame({
        'feature': available_features,
        'importance': final_model.feature_importances_
    }).sort_values('importance', ascending=False)
    imp.to_csv(os.path.join(MODEL_DIR, f"importance_pcr_rev_{horizon}d.csv"), index=False)
    
    return {
        "cv_accuracy": float(avg_acc),
        "rev_freq": float(rev_freq),
        "n_samples": len(X)
    }

def train_all():
    print("\n" + "="*50)
    print("TRAINING PCR REVERSAL MODELS")
    print("="*50)
    df = build_features()
    if df is None or df.empty:
        return

    results = {}
    for h in HORIZONS:
        res = train_pcr_reversal_model(df, horizon=h)
        if res:
            results[h] = res
            
    import json
    summary = {
        "last_trained": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "horizons": results
    }
    with open(os.path.join(MODEL_DIR, "pcr_rev_summary.json"), 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\nSummary saved to {MODEL_DIR}")

if __name__ == "__main__":
    train_all()
