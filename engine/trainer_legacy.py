"""
engine/trainer.py — XGBoost Model Trainer for Nifty Oracle (v2 Optimized)
=========================================================================
Trains directional classification models for different horizons.
Key upgrades in v2:
  - Optimized FEATURE_COLS (removed dead/redundant, added lag chains + regime momentum)
  - Early stopping to prevent overfitting
  - L1/L2 regularization (reg_alpha, reg_lambda, gamma)
  - 5-fold TimeSeriesSplit for more robust CV
"""

import os
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
import hashlib
import json
from datetime import datetime
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "models")

from engine.core import FEATURE_COLS

def _safe_feature_list(df):
    """Drop any future-looking columns from FEATURE_COLS."""
    blacklist_prefix = ("fwd_", "flo_", "fhi_")
    feats = []
    for c in FEATURE_COLS:
        if c in df.columns and not c.startswith(blacklist_prefix):
            feats.append(c)
    return feats

def _feature_hash(feats):
    return hashlib.sha256("|".join(sorted(feats)).encode()).hexdigest()

def _write_metadata(path, feats, pos_rate, spw, params, cv_accs, train_end):
    meta = {
        "train_end_date": train_end,
        "features": feats,
        "feature_hash": _feature_hash(feats),
        "pos_rate": pos_rate,
        "scale_pos_weight": spw,
        "params": params,
        "cv_accuracy_mean": float(np.mean(cv_accs)) if cv_accs else None,
        "cv_accuracy_per_fold": [float(a) for a in cv_accs],
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    with open(path, "w") as f:
        json.dump(meta, f, indent=2)

def train_direction_model(df, horizon=7):
    """
    Train XGBoost on engineered features with early stopping + regularization.
    Target: 1 if fwd_return > 0.01 (1%), else 0.
    """
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    # Validate features exist
    available_features = _safe_feature_list(df)
    if len(available_features) < 10:
        print(f"Skipping horizon {horizon}: Only {len(available_features)} features found.")
        return None

    # Create target
    target_col = f"fwd_{horizon}d"
    if target_col not in df.columns:
        print(f"Skipping horizon {horizon}: Target column {target_col} missing.")
        return None

    # Binary target: 1 if fwd > 0.01 (Up), else 0
    df['target_xgb'] = (df[target_col] > 0.01).astype(int)
    
    # Drop NaN rows
    potential_cols = available_features + ['target_xgb']
    if 'source' in df.columns: potential_cols.append('source')
    
    model_df = df[potential_cols].dropna()
    
    # Filter out synthetic data
    if 'source' in model_df.columns:
        initial_len = len(model_df)
        model_df = model_df[model_df['source'] == 'real']
        filtered_len = len(model_df)
        if initial_len > filtered_len:
            print(f"🛡️ AI Hardening: Ignored {initial_len - filtered_len} synthetic rows.")

    if len(model_df) < 200:
        print(f"Skipping horizon {horizon}: Only {len(model_df)} real data points remain.")
        return None

    X = model_df[available_features]
    y = model_df['target_xgb']

    # Dynamic class weight based on balance
    pos_rate = y.mean()
    scale_pos_weight = (1 - pos_rate) / max(pos_rate, 1e-4)
    
    # Time-series split (5-fold for robustness)
    tscv = TimeSeriesSplit(n_splits=5)
    accuracies = []
    
    print(f"Training horizon {horizon} days ({len(available_features)} features)...")
    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        
        model = xgb.XGBClassifier(
            n_estimators=500,
            max_depth=5,
            learning_rate=0.03,
            subsample=0.8,
            colsample_bytree=0.7,
            reg_alpha=0.1,
            reg_lambda=1.5,
            gamma=0.1,
            scale_pos_weight=scale_pos_weight,
            objective='binary:logistic',
            random_state=42,
            eval_metric='logloss',
            early_stopping_rounds=30
        )
        model.fit(X_train, y_train,
                  eval_set=[(X_test, y_test)],
                  verbose=False)
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        accuracies.append(acc)
    
    # Final model on all available data (with early stopping via last fold)
    print(f"Final fit for {horizon}d...")
    split_point = int(len(X) * 0.85)
    X_train_final, X_val_final = X.iloc[:split_point], X.iloc[split_point:]
    y_train_final, y_val_final = y.iloc[:split_point], y.iloc[split_point:]
    
    final_model = xgb.XGBClassifier(
        n_estimators=500,
        max_depth=5,
        learning_rate=0.03,
        subsample=0.8,
        colsample_bytree=0.7,
        reg_alpha=0.1,
        reg_lambda=1.5,
        gamma=0.1,
        scale_pos_weight=scale_pos_weight,
        objective='binary:logistic',
        random_state=42,
        eval_metric='logloss',
        early_stopping_rounds=30
    )
    final_model.fit(X_train_final, y_train_final,
                    eval_set=[(X_val_final, y_val_final)],
                    verbose=False)
    
    # Save the model + metadata
    model_name = f"xgb_direction_{horizon}d.pkl"
    save_path = os.path.join(MODEL_DIR, model_name)
    joblib.dump(final_model, save_path)
    meta_path = save_path + ".meta.json"
    params_used = final_model.get_xgb_params()
    train_end = str(df['date'].max())[:10] if 'date' in df.columns else None
    _write_metadata(meta_path, available_features, pos_rate, scale_pos_weight, params_used, accuracies, train_end)
    
    # Save feature importance
    importance = pd.DataFrame({
        'feature': available_features,
        'importance': final_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    importance_path = os.path.join(MODEL_DIR, f"importance_{horizon}d.csv")
    importance.to_csv(importance_path, index=False)
    
    print(f"Horizon {horizon}d: CV Accuracy {np.mean(accuracies):.2%} | Saved to {model_name} (meta saved)")
    return final_model

def train_all_horizons(df):
    """Loop through suggested horizons"""
    results = {}
    for h in [3, 5, 7, 14]:
        model = train_direction_model(df, horizon=h)
        if model:
            results[h] = model
    return results

if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from engine.core import build_features
    print("Pre-processing features...")
    df = build_features()
    if df is not None:
         train_all_horizons(df)
