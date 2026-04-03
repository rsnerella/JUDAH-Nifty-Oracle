"""
engine/global_contagion_trainer.py — Global Contagion Predictor Trainer
========================================================================
Predicts Nifty's opening gap using overnight moves in S&P500, Nasdaq, HSI, and Nikkei.
Essential for managing overnight risk in credit spreads.

Usage: python -m engine.global_contagion_trainer
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, accuracy_score
from datetime import datetime

# Ensure project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from engine.core import build_features, FEATURE_COLS

MODEL_DIR = os.path.join(ROOT_DIR, "data", "models", "global_contagion")

def train_contagion_models(df):
    if not os.path.exists(MODEL_DIR): 
        os.makedirs(MODEL_DIR)

    # 1. Target Construction: Next-day Opening Gap
    df_model = df.copy()
    df_model['gap_fwd'] = (df_model['open'].shift(-1) - df_model['close']) / (df_model['close'] + 1e-9) * 100
    df_model['gap_dir_fwd'] = (df_model['gap_fwd'] > 0).astype(int)
    
    # 2. Features: Specifically Global Markets
    global_feats = [
        'sp_ret', 'ndx_ret', 'hsi_ret', 'nikkei_ret', 'shanghai_ret', 
        'dxy_ret', 'us10y_ret', 'us_vix_ret', 'vix'
    ]
    available_features = [f for f in global_feats if f in df_model.columns]
    
    model_df = df_model[available_features + ['gap_fwd', 'gap_dir_fwd']].dropna()
    
    X = model_df[available_features]
    y_reg = model_df['gap_fwd']
    y_cls = model_df['gap_dir_fwd']

    print("\n" + "="*50)
    print("TRAINING GLOBAL CONTAGION MODELS")
    print("="*50)
    print(f"  Training on {len(X)} rows")

    tscv = TimeSeriesSplit(n_splits=5)
    
    # --- REGRESSOR (Gap Size) ---
    print("\n  [GLOBE] Training Gap Regressor...")
    cv_maes = []
    reg_params = {
        'n_estimators': 200,
        'max_depth': 3,
        'learning_rate': 0.05,
        'objective': 'reg:absoluteerror',
        'random_state': 42,
        'eval_metric': 'mae'
    }
    
    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y_reg.iloc[train_idx], y_reg.iloc[test_idx]
        m = xgb.XGBRegressor(**reg_params)
        m.fit(X_train, y_train)
        cv_maes.append(mean_absolute_error(y_test, m.predict(X_test)))
    
    print(f"  Gap MAE: {np.mean(cv_maes):.3f}%")
    reg_model = xgb.XGBRegressor(**reg_params)
    reg_model.fit(X, y_reg)
    joblib.dump(reg_model, os.path.join(MODEL_DIR, "xgb_gap_regressor.pkl"))

    # --- CLASSIFIER (Gap Direction) ---
    print("\n  [GLOBE] Training Gap Direction Classifier...")
    cv_accs = []
    cls_params = {
        'n_estimators': 200,
        'max_depth': 3,
        'learning_rate': 0.05,
        'objective': 'binary:logistic',
        'random_state': 42,
        'eval_metric': 'logloss'
    }
    
    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y_cls.iloc[train_idx], y_cls.iloc[test_idx]
        m = xgb.XGBClassifier(**cls_params)
        m.fit(X_train, y_train)
        cv_accs.append(accuracy_score(y_test, m.predict(X_test)))
        
    print(f"  Dir Accuracy: {np.mean(cv_accs):.1%}")
    cls_model = xgb.XGBClassifier(**cls_params)
    cls_model.fit(X, y_cls)
    joblib.dump(cls_model, os.path.join(MODEL_DIR, "xgb_gap_classifier.pkl"))

    # Importance
    imp = pd.DataFrame({
        'feature': available_features,
        'importance': cls_model.feature_importances_
    }).sort_values('importance', ascending=False)
    imp.to_csv(os.path.join(MODEL_DIR, "importance_contagion.csv"), index=False)

    import json
    summary = {
        "last_trained": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "metrics": {
            "reg_mae": float(np.mean(cv_maes)),
            "cls_accuracy": float(np.mean(cv_accs)),
            "n_samples": len(X)
        }
    }
    with open(os.path.join(MODEL_DIR, "contagion_summary.json"), 'w') as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    df = build_features()
    if df is not None and not df.empty:
        train_contagion_models(df)
