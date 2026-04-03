"""
engine/tail_risk_trainer.py — Tail Risk Predictor Trainer
==========================================================
Predicts if Nifty will experience a catastrophic move (>3 standard deviations) in next N days.
"Nuclear alarm" for options sellers.

Usage: python -m engine.tail_risk_trainer
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import recall_score, f1_score, precision_score
from sklearn.calibration import CalibratedClassifierCV
from datetime import datetime

# Ensure project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from engine.core import build_features, FEATURE_COLS

MODEL_DIR = os.path.join(ROOT_DIR, "data", "models", "tail_risk")
HORIZONS = [3, 5, 7]

def train_tail_risk_model(df, horizon=7):
    if not os.path.exists(MODEL_DIR): 
        os.makedirs(MODEL_DIR)

    available_features = [c for c in FEATURE_COLS if c in df.columns]
    
    df_model = df.copy()
    # 1. Compute 20d standard deviation of returns
    df_model['daily_ret'] = df_model['close'].pct_change()
    df_model['std_20d'] = df_model['daily_ret'].rolling(20).std().shift(1)
    
    # 2. Target: 1 if absolute forward return exceeds 3x volatility
    # Use actual forward returns
    fwd_col = f'fwd_{horizon}d'
    if fwd_col not in df_model.columns:
        df_model[fwd_col] = df_model['close'].shift(-horizon) / df_model['close'] - 1
        
    df_model['target_tail'] = (df_model[fwd_col].abs() > 3 * df_model['std_20d']).astype(int)
    
    # Drop rows where target is NaN or std is NaN
    cols_needed = available_features + ['target_tail', 'std_20d']
    model_df = df_model[cols_needed].dropna()
    
    tail_freq = model_df['target_tail'].mean() * 100
    print(f"\n  [NUCLEAR] Training Tail Risk Detector ({horizon}d)")
    print(f"  Tail Event Frequency: {tail_freq:.2f}%")

    if tail_freq == 0:
        print(f"  SKIPPING {horizon}d: No tail events found in data.")
        return None

    X = model_df[available_features]
    y = model_df['target_tail']

    tscv = TimeSeriesSplit(n_splits=5)
    cv_recalls = []
    
    # Critical: Use scale_pos_weight for highly imbalanced tail events
    params = {
        'n_estimators': 400,
        'max_depth': 4,
        'learning_rate': 0.02,
        'subsample': 0.8,
        'colsample_bytree': 0.7,
        'scale_pos_weight': 20.0, # Favor recall over precision
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
        y_pred = m.predict(X_test)
        cv_recalls.append(recall_score(y_test, y_pred, zero_division=0))

    avg_recall = np.mean(cv_recalls)
    print(f"  CV Recall (Sensitivity): {avg_recall:.2%}")

    # Final Train
    split = int(len(X) * 0.85)
    final_model = xgb.XGBClassifier(**params)
    final_model.fit(X.iloc[:split], y.iloc[:split], eval_set=[(X.iloc[split:], y.iloc[split:])], verbose=False)
    
    try:
        from sklearn.calibration import FrozenEstimator
        calibrated_final = CalibratedClassifierCV(estimator=FrozenEstimator(final_model), method='isotonic')
    except ImportError:
        calibrated_final = CalibratedClassifierCV(final_model, cv='prefit', method='isotonic')
        
    calibrated_final.fit(X.iloc[split:], y.iloc[split:])
    # Propagate feature names so dashboard modules can align features
    if hasattr(final_model, 'feature_names_in_'):
        calibrated_final.feature_names_in_ = final_model.feature_names_in_
    
    # Save
    model_path = os.path.join(MODEL_DIR, f"xgb_tail_risk_{horizon}d.pkl")
    joblib.dump(calibrated_final, model_path)
    
    # Importance
    importance = pd.DataFrame({
        'feature': available_features, 
        'importance': final_model.feature_importances_
    }).sort_values('importance', ascending=False)
    importance.to_csv(os.path.join(MODEL_DIR, f"importance_tail_{horizon}d.csv"), index=False)
    
    return {
        "cv_recall": float(avg_recall),
        "tail_freq": float(tail_freq),
        "n_samples": len(X)
    }

def train_all():
    print("\n" + "="*50)
    print("TRAINING TAIL RISK DETECTOR")
    print("="*50)
    df = build_features()
    if df is None or df.empty:
        return

    results = {}
    for h in HORIZONS:
        res = train_tail_risk_model(df, horizon=h)
        if res:
            results[h] = res
            
    import json
    summary = {
        "last_trained": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "horizons": results
    }
    with open(os.path.join(MODEL_DIR, "tail_summary.json"), 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\nSummary saved to {MODEL_DIR}")

if __name__ == "__main__":
    train_all()
