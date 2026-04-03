"""
engine/gap_risk_trainer.py — Gap Risk ML Trainer
================================================
Predicts if there will be a >1% gap at tomorrow's open.
Gaps are the biggest risk for overnight credit spreads.

Usage: python -m engine.gap_risk_trainer
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from datetime import datetime

# Ensure project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from engine.core import FEATURE_COLS
from engine.core import build_features

MODEL_DIR = os.path.join(ROOT_DIR, "data", "models", "gap_risk")
GAP_THRESHOLD = 0.01 # 1% gap

def train_gap_risk_model(df):
    if not os.path.exists(MODEL_DIR): os.makedirs(MODEL_DIR)

    available_features = [c for c in FEATURE_COLS if c in df.columns]
    
    # Target: tomorrow's gap
    # gap_pct = abs(open_tomorrow - close_today) / close_today
    df_model = df.copy()
    df_model['next_open'] = df_model['open'].shift(-1)
    df_model['gap_size'] = (df_model['next_open'] - df_model['close']).abs() / df_model['close']
    df_model['target_gap'] = (df_model['gap_size'] > GAP_THRESHOLD).astype(int)
    
    cols_needed = available_features + ['target_gap', 'gap_size']
    if 'source' in df_model.columns: cols_needed.append('source')
    model_df = df_model[cols_needed].dropna()
    if 'source' in model_df.columns: model_df = model_df[model_df['source'] == 'real']

    if len(model_df) < 500:
        print(f"  ONLY {len(model_df)} rows — skipping.")
        return None

    X = model_df[available_features]
    y = model_df['target_gap']

    # Class balance
    gap_freq = y.mean() * 100
    print(f"  Gap Frequency (>1%): {gap_freq:.1f}%")

    # Time Series CV
    tscv = TimeSeriesSplit(n_splits=5)
    cv_accs = []
    cv_prec = []
    
    # We use a classifier for the gap risk
    params = {
        'n_estimators': 400,
        'max_depth': 4,
        'learning_rate': 0.02,
        'subsample': 0.8,
        'colsample_bytree': 0.7,
        'scale_pos_weight': (100 - gap_freq) / max(gap_freq, 1), # Handle imbalance
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
        
        preds = m.predict(X_test)
        cv_accs.append(accuracy_score(y_test, preds))
        cv_prec.append(precision_score(y_test, preds, zero_division=0))

    avg_acc = np.mean(cv_accs)
    avg_prec = np.mean(cv_prec)
    print(f"  OK Gap Risk -> CV Acc: {avg_acc:.2%}, CV Precision: {avg_prec:.2%}")

    # Final Train
    split = int(len(X) * 0.85)
    final_model = xgb.XGBClassifier(**params)
    final_model.fit(X.iloc[:split], y.iloc[:split], eval_set=[(X.iloc[split:], y.iloc[split:])], verbose=False)
    
    # Save
    joblib.dump(final_model, os.path.join(MODEL_DIR, "xgb_gap_risk.pkl"))
    
    # Importance
    importance = pd.DataFrame({'feature': available_features, 'importance': final_model.feature_importances_}).sort_values('importance', ascending=False)
    importance.to_csv(os.path.join(MODEL_DIR, "importance_gap_risk.csv"), index=False)
    
    return {
        "cv_accuracy": float(avg_acc),
        "cv_precision": float(avg_prec),
        "gap_freq": float(gap_freq),
        "n_samples": len(X)
    }

def train_gap_risk_regression(df):
    # Optional: predict exact gap size
    available_features = [c for c in FEATURE_COLS if c in df.columns]
    df_model = df.copy()
    df_model['next_open'] = df_model['open'].shift(-1)
    df_model['target_gap_size'] = (df_model['next_open'] - df_model['close']).abs() / df_model['close'] * 100 # in %
    model_df = df_model[available_features + ['target_gap_size']].dropna()
    if 'source' in model_df.columns: model_df = model_df[model_df['source'] == 'real']
    
    X = model_df[available_features]
    y = model_df['target_gap_size']
    
    params = {
        'n_estimators': 300,
        'max_depth': 4,
        'learning_rate': 0.03,
        'objective': 'reg:squarederror',
        'random_state': 42,
        'eval_metric': 'mae',
        'early_stopping_rounds': 25
    }
    
    split = int(len(X) * 0.85)
    m = xgb.XGBRegressor(**params)
    m.fit(X.iloc[:split], y.iloc[:split], eval_set=[(X.iloc[split:], y.iloc[split:])], verbose=False)
    joblib.dump(m, os.path.join(MODEL_DIR, "xgb_gap_size_reg.pkl"))
    return True

def train_all_gap_models():
    print("\n" + "="*50)
    print("TRAINING GAP RISK MODELS")
    print("="*50)
    df = build_features()
    if df is None or df.empty:
        print("FAILED to load features.")
        return

    res_cls = train_gap_risk_model(df)
    train_gap_risk_regression(df)
            
    import json
    summary = {
        "last_trained": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "metrics": res_cls
    }
    with open(os.path.join(MODEL_DIR, "gap_summary.json"), 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\nGap Summary saved to {MODEL_DIR}")

if __name__ == "__main__":
    train_all_gap_models()
