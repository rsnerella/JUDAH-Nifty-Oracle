"""
engine/regime_transition_trainer.py — Regime Transition Predictor Trainer
==========================================================================
Predicts if the market regime (GREEN/YELLOW/RED) will change in the next N days.
Critical for credit spread sellers to exit before a regime shift.

Usage: python -m engine.regime_transition_trainer
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, classification_report
from datetime import datetime

# Ensure project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from engine.core import build_features, FEATURE_COLS, compute_regime_score, classify_regime

MODEL_DIR = os.path.join(ROOT_DIR, "data", "models", "regime_transition")
HORIZONS = [3, 5, 7]

def train_regime_transition_models(df, horizon=5):
    if not os.path.exists(MODEL_DIR): 
        os.makedirs(MODEL_DIR)

    available_features = [c for c in FEATURE_COLS if c in df.columns]
    
    # 1. Compute regime for every day
    regimes = []
    for i in range(len(df)):
        score, _ = compute_regime_score(df.iloc[i])
        regimes.append(classify_regime(score))
    
    df_model = df.copy()
    df_model['regime_today'] = regimes
    # Target: 1 if regime changes in the future
    df_model['regime_future'] = df_model['regime_today'].shift(-horizon)
    df_model['target_shift'] = (df_model['regime_future'] != df_model['regime_today']).astype(int)
    
    # Drop rows where target is NaN (the last 'horizon' rows)
    cols_needed = available_features + ['target_shift']
    if 'source' in df_model.columns:
        cols_needed.append('source')
    
    model_df = df_model[cols_needed].dropna()
    
    # Filter synthetic data if applicable
    if 'source' in model_df.columns:
        model_df = model_df[model_df['source'] == 'real']

    if len(model_df) < 500:
        print(f"  SKIPPING {horizon}d: Only {len(model_df)} rows available.")
        return None

    X = model_df[available_features]
    y = model_df['target_shift']

    shift_freq = y.mean() * 100
    print(f"\n  [SHIELD] Training Regime Shift Classifier ({horizon}d)")
    print(f"  Transition Frequency: {shift_freq:.1f}%")

    tscv = TimeSeriesSplit(n_splits=5)
    cv_accs = []
    
    params = {
        'n_estimators': 300,
        'max_depth': 4,
        'learning_rate': 0.03,
        'subsample': 0.8,
        'colsample_bytree': 0.7,
        'scale_pos_weight': (100 - shift_freq) / max(shift_freq, 1),
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
    print(f"  CV Accuracy: {avg_acc:.2%}")

    # Final Train
    split = int(len(X) * 0.85)
    final_model = xgb.XGBClassifier(**params)
    final_model.fit(X.iloc[:split], y.iloc[:split], eval_set=[(X.iloc[split:], y.iloc[split:])], verbose=False)
    
    # Save
    model_path = os.path.join(MODEL_DIR, f"xgb_regime_shift_{horizon}d.pkl")
    joblib.dump(final_model, model_path)
    
    # Importance
    importance = pd.DataFrame({
        'feature': available_features, 
        'importance': final_model.feature_importances_
    }).sort_values('importance', ascending=False)
    importance.to_csv(os.path.join(MODEL_DIR, f"importance_shift_{horizon}d.csv"), index=False)
    
    return {
        "cv_accuracy": float(avg_acc),
        "shift_freq": float(shift_freq),
        "n_samples": len(X)
    }

def train_all():
    print("\n" + "="*50)
    print("TRAINING REGIME TRANSITION MODELS")
    print("="*50)
    df = build_features()
    if df is None or df.empty:
        print("FAILED to build features.")
        return

    results = {}
    for h in HORIZONS:
        res = train_regime_transition_models(df, horizon=h)
        if res:
            results[h] = res
            
    import json
    summary = {
        "last_trained": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "horizons": results
    }
    with open(os.path.join(MODEL_DIR, "shift_summary.json"), 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\nSummary saved to {MODEL_DIR}")

if __name__ == "__main__":
    train_all()
