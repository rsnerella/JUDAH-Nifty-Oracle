"""
engine/macro_sentiment_trainer.py — Macro Sentiment Predictor Trainer
========================================================================
Predicts Nifty's "Risk-ON" or "Risk-OFF" state using Gold, Crude, DXY, and US10Y.
Essential for understanding the fundamental global backdrop.

Usage: python -m engine.macro_sentiment_trainer
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

MODEL_DIR = os.path.join(ROOT_DIR, "data", "models", "macro_sentiment")

def train_macro_sentiment_model(df):
    if not os.path.exists(MODEL_DIR): 
        os.makedirs(MODEL_DIR)

    # 1. Macro Features
    macro_feats = [
        'dxy_ret', 'gold_ret', 'crude_ret', 'us10y_ret', 'us_vix_ret', 'sp_ret',
        'copper_ret', 'silver_ret', 'natgas_ret', 'spread'
    ]
    available_features = [f for f in macro_feats if f in df.columns]
    
    df_model = df.copy()
    # Target: 1 if Nifty goes UP in next 5 days
    df_model['target_risk_on'] = (df_model['fwd_5d'] > 0).astype(int)
    
    # Drop rows where target is NaN
    cols_needed = available_features + ['target_risk_on']
    model_df = df_model[cols_needed].dropna()
    
    risk_on_freq = model_df['target_risk_on'].mean() * 100
    print(f"\n  [WORLD] Training Macro Sentiment Predictor")
    print(f"  Predicting Nifty Direction via Global Assets")
    print(f"  Risk-ON Frequency (5d): {risk_on_freq:.1f}%")

    X = model_df[available_features]
    y = model_df['target_risk_on']

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
    print(f"  CV Accuracy: {avg_acc:.1%}")

    # Final Train
    split = int(len(X) * 0.85)
    final_model = xgb.XGBClassifier(**params)
    final_model.fit(X.iloc[:split], y.iloc[:split], eval_set=[(X.iloc[split:], y.iloc[split:])], verbose=False)
    
    # Save
    model_path = os.path.join(MODEL_DIR, "xgb_macro_sentiment.pkl")
    joblib.dump(final_model, model_path)
    
    # Importance
    imp = pd.DataFrame({
        'feature': available_features,
        'importance': final_model.feature_importances_
    }).sort_values('importance', ascending=False)
    imp.to_csv(os.path.join(MODEL_DIR, "importance_macro.csv"), index=False)

    import json
    summary = {
        "last_trained": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "metrics": {
            "cv_accuracy": float(avg_acc),
            "risk_on_freq": float(risk_on_freq),
            "n_samples": len(X)
        }
    }
    with open(os.path.join(MODEL_DIR, "macro_summary.json"), 'w') as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    df = build_features()
    if df is not None and not df.empty:
        train_macro_sentiment_model(df)
