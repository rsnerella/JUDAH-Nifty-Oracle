"""
engine/expiry_vol_trainer.py — Expiry Week Volatility Trainer
============================================================
Forecasts if the current expiry week will be high-volatility (Wide Range) or low-volatility (Tight Range).
Helps in deciding to sell Iron Condors vs buying Straddles.

Usage: python -m engine.expiry_vol_trainer
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

MODEL_DIR = os.path.join(ROOT_DIR, "data", "models", "expiry_vol")
EVENTS_PATH = os.path.join(ROOT_DIR, "data", "events.csv")

def train_expiry_vol_model(df):
    if not os.path.exists(MODEL_DIR): 
        os.makedirs(MODEL_DIR)

    available_features = [c for c in FEATURE_COLS if c in df.columns]
    
    # 1. Load Events and Tag Expiry Weeks
    events = pd.read_csv(EVENTS_PATH)
    events['date'] = pd.to_datetime(events['Date'])
    
    # Correct tagging based on CSV schema: label or Event can contain 'Weekly Expiry'
    expiry_mask = (events['Type'] == 'Monthly_Expiry') | \
                  (events['label'] == 'Weekly Expiry') | \
                  (events['Event'] == 'Weekly Expiry')
                  
    all_expiries = sorted(events[expiry_mask]['date'].tolist())
    
    df_model = df.copy()
    df_model['date'] = pd.to_datetime(df_model['date'])
    
    # Tagging: A day is in expiry week if its next expiry is within 4 days
    def get_next_expiry(d):
        for e in all_expiries:
            if e >= d: return e
        return None
    
    df_model['next_expiry'] = df_model['date'].apply(get_next_expiry)
    df_model['days_to_expiry'] = (df_model['next_expiry'] - df_model['date']).dt.days
    df_model['is_expiry_week'] = (df_model['days_to_expiry'] <= 4).astype(int)
    
    # 2. Target Construction: High Volatility Week?
    # We look at the range over the next 5 days
    fwd_range = (df_model['high'].rolling(5).max().shift(-5) - df_model['low'].rolling(5).min().shift(-5)) / df_model['close']
    median_range = fwd_range.median()
    
    df_model['target_high_vol'] = (fwd_range > median_range).astype(int)
    
    # Drop rows where target is NaN
    cols_needed = available_features + ['target_high_vol', 'is_expiry_week']
    model_df = df_model[cols_needed].dropna()
    
    vol_freq = model_df['target_high_vol'].mean() * 100
    print(f"\n  [CALENDAR] Training Expiry Volatility Predictor")
    print(f"  High Vol Week Frequency: {vol_freq:.1f}%")

    X = model_df[available_features + ['is_expiry_week']]
    y = model_df['target_high_vol']

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
    model_path = os.path.join(MODEL_DIR, "xgb_expiry_vol.pkl")
    joblib.dump(final_model, model_path)
    
    # Importance
    imp = pd.DataFrame({
        'feature': X.columns,
        'importance': final_model.feature_importances_
    }).sort_values('importance', ascending=False)
    imp.to_csv(os.path.join(MODEL_DIR, "importance_expiry_vol.csv"), index=False)

    import json
    summary = {
        "last_trained": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "metrics": {
            "cv_accuracy": float(avg_acc),
            "vol_freq": float(vol_freq),
            "n_samples": len(X)
        }
    }
    with open(os.path.join(MODEL_DIR, "expiry_vol_summary.json"), 'w') as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    df = build_features()
    if df is not None and not df.empty:
        train_expiry_vol_model(df)
