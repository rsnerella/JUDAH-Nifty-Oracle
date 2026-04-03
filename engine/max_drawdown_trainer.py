"""
engine/max_drawdown_trainer.py — Max Drawdown Predictor Trainer
==============================================================
Predicts the worst-case intraday drop (Floor) and rally (Ceiling) in points.
Provides a continuous safety buffer for strike selection.

Usage: python -m engine.max_drawdown_trainer
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, r2_score
from datetime import datetime

# Ensure project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from engine.core import build_features, FEATURE_COLS

MODEL_DIR = os.path.join(ROOT_DIR, "data", "models", "max_drawdown")
HORIZONS = [3, 5, 7, 14]

def train_drawdown_model(df, horizon=7, side='down'):
    if not os.path.exists(MODEL_DIR): 
        os.makedirs(MODEL_DIR)

    available_features = [c for c in FEATURE_COLS if c in df.columns]
    
    df_model = df.copy()
    
    # Target Construction
    # flo_Nd is % change to the lowest low in next N days
    # fhi_Nd is % change to the highest high in next N days
    col = f'flo_{horizon}d' if side == 'down' else f'fhi_{horizon}d'
    
    if col not in df_model.columns:
        if side == 'down':
            df_model[col] = df_model['low'].rolling(horizon).min().shift(-horizon) / df_model['close'] - 1
        else:
            df_model[col] = df_model['high'].rolling(horizon).max().shift(-horizon) / df_model['close'] - 1

    # Convert to points
    target_name = f'target_{side}_{horizon}d'
    df_model[target_name] = df_model[col] * df_model['close']
    
    # Drop rows where target is NaN
    cols_needed = available_features + [target_name]
    model_df = df_model[cols_needed].dropna()
    
    print(f"\n  [RULER] Training Max {side.upper()} Predictor ({horizon}d)")
    
    X = model_df[available_features]
    y = model_df[target_name]

    tscv = TimeSeriesSplit(n_splits=5)
    cv_maes = []
    
    params = {
        'n_estimators': 300,
        'max_depth': 4,
        'learning_rate': 0.03,
        'subsample': 0.8,
        'colsample_bytree': 0.7,
        'objective': 'reg:absoluteerror', # We want to minimize MAE (points)
        'random_state': 42,
        'eval_metric': 'mae',
        'early_stopping_rounds': 30
    }

    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        
        m = xgb.XGBRegressor(**params)
        m.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
        cv_maes.append(mean_absolute_error(y_test, m.predict(X_test)))

    avg_mae = np.mean(cv_maes)
    print(f"  CV MAE: {avg_mae:.2f} pts")

    # Final Train
    split = int(len(X) * 0.85)
    final_model = xgb.XGBRegressor(**params)
    final_model.fit(X.iloc[:split], y.iloc[:split], eval_set=[(X.iloc[split:], y.iloc[split:])], verbose=False)
    
    # Save
    model_path = os.path.join(MODEL_DIR, f"xgb_dd_{side}_{horizon}d.pkl")
    joblib.dump(final_model, model_path)
    
    return {
        "cv_mae": float(avg_mae),
        "n_samples": len(X)
    }

def train_all():
    print("\n" + "="*50)
    print("TRAINING MAX DRAWDOWN REGRESSORS")
    print("="*50)
    df = build_features()
    if df is None or df.empty:
        return

    results = {}
    for h in HORIZONS:
        results[h] = {
            "down": train_drawdown_model(df, horizon=h, side='down'),
            "up": train_drawdown_model(df, horizon=h, side='up')
        }
            
    import json
    summary = {
        "last_trained": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "horizons": results
    }
    with open(os.path.join(MODEL_DIR, "drawdown_summary.json"), 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\nSummary saved to {MODEL_DIR}")

if __name__ == "__main__":
    train_all()
