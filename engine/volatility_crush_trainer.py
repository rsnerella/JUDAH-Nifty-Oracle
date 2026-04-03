"""
engine/volatility_crush_trainer.py — Volatility Crush ML Trainer
================================================================
Predicts if Realized Volatility will be LOWER than Implied Volatility (VIX).

Target: 1 if actual_Nd_range < VIX_implied_range_Nd else 0
WHY: If realized vol < implied vol -> options are OVERPRICED -> SELL them.

Usage: python -m engine.volatility_crush_trainer
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, log_loss, classification_report
from datetime import datetime

# Ensure project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from engine.core import FEATURE_COLS
from engine.core import build_features

MODEL_DIR = os.path.join(ROOT_DIR, "data", "models", "vol_crush")
HORIZONS = [3, 5, 7, 14]

def train_vol_crush_models(df, horizon=7):
    """
    Train a volatility crush model for a given horizon.
    Target: 1 if actual_Nd_range < VIX_implied_range_Nd else 0
    """
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    # Validate features
    available_features = [c for c in FEATURE_COLS if c in df.columns]
    
    # Target Construction
    # VIX-implied range (points): spot * (VIX/100) * sqrt(horizon/252)
    # Actual range (points): max(high_Nd) - min(low_Nd)
    
    # We need max/min over horizon
    # These are already in df if we use build_features() which adds fhi and flo
    # fhi_Nd = high_rolling_max(h) / close - 1
    # flo_Nd = low_rolling_min(h) / close - 1
    # actual_range_pct = fhi_Nd - flo_Nd
    # vix_implied_range_pct = (vix / 100) * sqrt(h / 252)
    
    vix_col = 'vix'
    fhi_col = f"fhi_{horizon}d"
    flo_col = f"flo_{horizon}d"
    
    if vix_col not in df.columns or fhi_col not in df.columns or flo_col not in df.columns:
        print(f"  SKIPPING {horizon}d: Missing required columns.")
        return None

    # Calculate actual range as percentage of current close
    df_model = df.copy()
    df_model['actual_range_pct'] = df_model[fhi_col] - df_model[flo_col]
    df_model['vix_implied_range_pct'] = (df_model[vix_col] / 100) * np.sqrt(horizon / 252)
    
    # Target: 1 if actual < implied (CRUSH), 0 otherwise (EXPANSION)
    df_model['target_crush'] = (df_model['actual_range_pct'] < df_model['vix_implied_range_pct']).astype(int)
    
    # Drop NaN rows
    cols_needed = available_features + ['target_crush']
    if 'source' in df_model.columns:
        cols_needed.append('source')
    model_df = df_model[cols_needed].dropna()

    # Filter synthetic data
    if 'source' in model_df.columns:
        model_df = model_df[model_df['source'] == 'real']

    if len(model_df) < 200:
        print(f"  ONLY {len(model_df)} rows — skipping.")
        return None

    X = model_df[available_features]
    y = model_df['target_crush']

    # Class balance
    crush_pct = y.mean() * 100
    print(f"  {horizon}d Class balance: CRUSH={crush_pct:.1f}% | EXPANSION={100-crush_pct:.1f}%")

    # Time Series CV
    tscv = TimeSeriesSplit(n_splits=5)
    cv_accs = []
    
    model_params = {
        'n_estimators': 400,
        'max_depth': 4,
        'learning_rate': 0.03,
        'subsample': 0.8,
        'colsample_bytree': 0.7,
        'reg_alpha': 0.15,
        'reg_lambda': 2.0,
        'gamma': 0.15,
        'objective': 'binary:logistic',
        'random_state': 42,
        'eval_metric': 'logloss'
    }

    for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        model = xgb.XGBClassifier(**model_params, early_stopping_rounds=25)
        model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
        
        preds = model.predict(X_test)
        cv_accs.append(accuracy_score(y_test, preds))

    avg_acc = np.mean(cv_accs)
    print(f"  OK {horizon}d CV Accuracy: {avg_acc:.2%}")

    # Final Train
    split = int(len(X) * 0.85)
    X_f, X_v = X.iloc[:split], X.iloc[split:]
    y_f, y_v = y.iloc[:split], y.iloc[split:]
    
    final_model = xgb.XGBClassifier(**model_params, early_stopping_rounds=25)
    final_model.fit(X_f, y_f, eval_set=[(X_v, y_v)], verbose=False)
    
    # Save
    model_name = f"xgb_vol_crush_{horizon}d.pkl"
    save_path = os.path.join(MODEL_DIR, model_name)
    joblib.dump(final_model, save_path)
    
    # Feature Importance
    importance = pd.DataFrame({
        'feature': available_features,
        'importance': final_model.feature_importances_
    }).sort_values('importance', ascending=False)
    importance.to_csv(os.path.join(MODEL_DIR, f"importance_vol_crush_{horizon}d.csv"), index=False)

    val_preds = final_model.predict(X_v)
    val_acc = accuracy_score(y_v, val_preds)
    
    return {
        "cv_accuracy": float(avg_acc),
        "val_accuracy": float(val_acc),
        "crush_pct": float(crush_pct),
        "n_samples": len(y),
        "model_path": save_path
    }

def train_all_vol_crush_models():
    print("\n" + "="*50)
    print("TRAINING VOLATILITY CRUSH MODELS")
    print("="*50)
    
    df = build_features()
    if df is None or df.empty:
        print("FAILED to load features.")
        return

    results = {}
    for h in HORIZONS:
        res = train_vol_crush_models(df, horizon=h)
        if res:
            results[h] = res
            
    # Save Summary
    import json
    summary = {
        "last_trained": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "horizons": results
    }
    with open(os.path.join(MODEL_DIR, "vol_crush_summary.json"), 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\nVol Crush Summary saved to {MODEL_DIR}")

if __name__ == "__main__":
    train_all_vol_crush_models()
