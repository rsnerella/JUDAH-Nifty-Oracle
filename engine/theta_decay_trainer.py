"""
engine/theta_decay_trainer.py — Theta Decay Predictor Trainer
============================================================
Predicts the "Theta Edge" for each entry day.
Target: 1 if entering a 7-day spread today is historically profitable (Price stays in range).

Usage: python -m engine.theta_decay_trainer
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

MODEL_DIR = os.path.join(ROOT_DIR, "data", "models", "theta_decay")

def train_theta_decay_model(df):
    if not os.path.exists(MODEL_DIR): 
        os.makedirs(MODEL_DIR)

    available_features = [c for c in FEATURE_COLS if c in df.columns]
    
    df_model = df.copy()
    
    # 1. Target Construction: Is 7-day range <= 2%? (Standard Condor Profit)
    # This identifies days where the "Sell Vol" edge is highest.
    df_model['target_theta'] = (df_model['fwd_7d'].abs() <= 0.02).astype(int)
    
    # Drop rows where target is NaN
    cols_needed = available_features + ['target_theta']
    model_df = df_model[cols_needed].dropna()
    
    theta_freq = model_df['target_theta'].mean() * 100
    print(f"\n  [CLOCK] Training Theta Decay Predictor")
    print(f"  Theta Winner Frequency (±2% Range): {theta_freq:.1f}%")

    X = model_df[available_features]
    y = model_df['target_theta']

    print(f"  Training on {len(X)} rows")

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
        'early_stopping_rounds': 30
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
    model_path = os.path.join(MODEL_DIR, "xgb_theta_decay.pkl")
    joblib.dump(final_model, model_path)
    
    # Importance
    imp = pd.DataFrame({
        'feature': available_features,
        'importance': final_model.feature_importances_
    }).sort_values('importance', ascending=False)
    imp.to_csv(os.path.join(MODEL_DIR, "importance_theta.csv"), index=False)

    import json
    summary = {
        "last_trained": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "metrics": {
            "cv_accuracy": float(avg_acc),
            "theta_freq": float(theta_freq),
            "n_samples": len(X)
        }
    }
    with open(os.path.join(MODEL_DIR, "theta_summary.json"), 'w') as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    df = build_features()
    if df is not None and not df.empty:
        train_theta_decay_model(df)
