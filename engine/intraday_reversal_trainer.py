"""
engine/intraday_reversal_trainer.py — Intraday Reversal Predictor Trainer
==========================================================================
Predicts if a morning drop (Panic) will recover by the market close.
Crucial for dip-buying and overnight hold decisions.

Usage: python -m engine.intraday_reversal_trainer
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

from engine.core import build_features, FEATURE_COLS

MODEL_DIR = os.path.join(ROOT_DIR, "data", "models", "intraday_reversal")

def train_reversal_model(df):
    if not os.path.exists(MODEL_DIR): 
        os.makedirs(MODEL_DIR)

    available_features = [c for c in FEATURE_COLS if c in df.columns]
    
    df_model = df.copy()
    
    # Target Construction: Reversal Success
    # 1 if (Morning was DOWN and Close > Midpoint) OR (Morning was UP and Close < Midpoint)
    # We use 'gap_pct' and 'first_hour_range' as morning indicators
    # We use 'close_position' (0=low, 1=high) as the recovery indicator
    
    # SHIFT THE TARGET: We want to predict TODAY'S reversal using YESTERDAY'S features.
    # In df_model, features are already shifted (row i has data from i-1).
    # So we look at row i+1 to see the actual outcome of 'today'.
    real_gap = df_model['gap_pct'].shift(-1)
    real_close_pos = df_model['close_position'].shift(-1)
    
    bull_rev = (real_gap < -0.005) & (real_close_pos > 0.6)
    bear_rev = (real_gap > 0.005) & (real_close_pos < 0.4)
    
    df_model['target_reversal'] = (bull_rev | bear_rev).astype(int)
    
    # Check if we have any targets
    if df_model['target_reversal'].sum() == 0:
        # Fallback: looser thresholds if data is scarce
        bull_rev = (real_gap < -0.003) & (real_close_pos > 0.55)
        bear_rev = (real_gap > 0.003) & (real_close_pos < 0.45)
        df_model['target_reversal'] = (bull_rev | bear_rev).astype(int)
    
    # Drop rows where target is NaN
    cols_needed = available_features + ['target_reversal']
    model_df = df_model[cols_needed].dropna()
    
    rev_freq = model_df['target_reversal'].mean() * 100
    print(f"\n  [PIVOT] Training Intraday Reversal Predictor")
    print(f"  Reversal Freq (Gap Reversal): {rev_freq:.1f}%")

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
    model_path = os.path.join(MODEL_DIR, "xgb_intraday_rev.pkl")
    joblib.dump(final_model, model_path)
    
    # Importance
    imp = pd.DataFrame({
        'feature': available_features,
        'importance': final_model.feature_importances_
    }).sort_values('importance', ascending=False)
    imp.to_csv(os.path.join(MODEL_DIR, "importance_reversal.csv"), index=False)

    import json
    summary = {
        "last_trained": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "metrics": {
            "cv_accuracy": float(avg_acc),
            "rev_freq": float(rev_freq),
            "n_samples": len(X)
        }
    }
    with open(os.path.join(MODEL_DIR, "reversal_summary.json"), 'w') as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    df = build_features()
    if df is not None and not df.empty:
        train_reversal_model(df)
