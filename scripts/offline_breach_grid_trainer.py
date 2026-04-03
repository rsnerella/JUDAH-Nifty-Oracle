"""
scripts/offline_breach_grid_trainer.py — "Super Grid" Parameter Discovery for Breach Radar
========================================================================================
Performs exhaustive grid search across hyperparameter combinations
and distinct market regime splits for the Breach Radar models (PUT & CALL Safety).
Saves the optimized parameters to `data/models/breach/breach_optimal_params.json`
for the fast weekly automated trainer to consume.

Usage: python scripts/offline_breach_grid_trainer.py
"""

import os
import sys
import time
import json
import warnings
import numpy as np
import pandas as pd
import xgboost as xgb
from datetime import datetime
from sklearn.metrics import log_loss

# Ensure the project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from engine.core import build_features, FEATURE_COLS

warnings.filterwarnings("ignore")

# Single advanced grid (~648 combos) for Breach
GRID = {
    'n_estimators': [100, 200, 300],
    'max_depth': [3, 4, 5],
    'learning_rate': [0.01, 0.03, 0.05],
    'subsample': [0.6, 0.8, 1.0],
    'colsample_bytree': [0.7, 1.0],
    'reg_alpha': [0, 0.5],
    'reg_lambda': [1.0, 3.0],
}

# Define Multi-regime Splits (Robustness Test)
SPLITS = [
    ('2016-01-01', '2018-01-01'), # Pre-COVID Bull
    ('2019-01-01', '2021-01-01'), # COVID Stress test
    ('2022-01-01', '2023-01-01'), # Recovery
    ('2024-01-01', '2025-06-01'), # Recent Regime
]

BREACH_THRESHOLD_PCT = 0.025
HORIZONS = [3, 5, 7, 14, 28]
MODEL_DIR = os.path.join(ROOT_DIR, "data", "models", "breach")

def run_breach_grid_search(df, horizon, side):
    """Find best parameters that perform well across all regimes for a specific side."""
    print(f"\n🚀 [{horizon}d - {side}] Starting Breach Grid Search...")
    
    target_col_raw = f"flo_{horizon}d" if side == "PUT" else f"fhi_{horizon}d"
    
    if target_col_raw not in df.columns:
        print(f"⚠️ Missing {target_col_raw}.")
        return None

    df_model = df.copy()
    adaptive_threshold = (df_model['atr20'] * 2) / df_model['close']
    
    if side == "PUT":
        df_model['target_breach'] = (df_model[target_col_raw] > -adaptive_threshold).astype(int)
    else:
        df_model['target_breach'] = (df_model[target_col_raw] < adaptive_threshold).astype(int)
        
    available_features = [c for c in FEATURE_COLS if c in df_model.columns]
    cols_needed = available_features + ['target_breach', 'date']
    if 'source' in df_model.columns:
        cols_needed.append('source')
        
    df_h = df_model[cols_needed].dropna()
    if 'source' in df_h.columns:
        df_h = df_h[df_h['source'] == 'real']
        
    if len(df_h) < 200:
        return None

    # Class balance for scale_pos_weight
    safe_rate = df_h['target_breach'].mean()
    breach_rate = 1 - safe_rate
    scale_pos_weight = breach_rate / max(safe_rate, 1e-4)

    split_data = []
    for t_end, v_end in SPLITS:
        train = df_h[df_h['date'] < t_end]
        val   = df_h[(df_h['date'] >= t_end) & (df_h['date'] < v_end)]
        if len(train) > 100 and len(val) > 30:
            split_data.append((
                train[available_features], train['target_breach'],
                val[available_features], val['target_breach']
            ))
            
    if not split_data:
        print("⚠️ No valid splits.")
        return None

    total_combos = 1
    for v in GRID.values(): total_combos *= len(v)
    
    best_avg_score = float('inf')
    best_params = None
    
    run_idx = 0
    t0 = time.time()
    max_combos = int(os.getenv("MAX_GRID_COMBOS", "0")) or None

    for n_est in GRID['n_estimators']:
      for depth in GRID['max_depth']:
        for lr in GRID['learning_rate']:
          for sub in GRID['subsample']:
            for col_sample in GRID['colsample_bytree']:
              for r_alpha in GRID['reg_alpha']:
                for r_lambda in GRID['reg_lambda']:
                    run_idx += 1
                    if max_combos and run_idx > max_combos:
                        break
                    
                    split_scores = []
                    for Xt, yt, Xv, yv in split_data:
                        model = xgb.XGBClassifier(
                            n_estimators=n_est, max_depth=depth, learning_rate=lr,
                            subsample=sub, colsample_bytree=col_sample,
                            reg_alpha=r_alpha, reg_lambda=r_lambda,
                            scale_pos_weight=scale_pos_weight,
                            objective='binary:logistic', eval_metric='logloss',
                            random_state=42, n_jobs=4, verbosity=0,
                            early_stopping_rounds=25
                        )
                        model.fit(Xt, yt, eval_set=[(Xv, yv)], verbose=False)
                        probs = model.predict_proba(Xv)
                        split_scores.append(log_loss(yv, probs))
                    
                    avg_logloss = np.mean(split_scores)
                    
                    if avg_logloss < best_avg_score:
                        best_avg_score = avg_logloss
                        best_params = {
                            'n_estimators': n_est, 'max_depth': depth,
                            'learning_rate': lr, 'subsample': sub,
                            'colsample_bytree': col_sample,
                            'reg_alpha': r_alpha, 'reg_lambda': r_lambda
                        }
                    
                    if run_idx % 100 == 0:
                        print(f"   Progress: {run_idx}/{total_combos} | Elapsed: {time.time()-t0:.1f}s | Best LogLoss: {best_avg_score:.4f}")

    print(f"✅ Found ROBUST params for {horizon}d {side}: {best_params} (Avg LogLoss: {best_avg_score:.4f})")
    
    return {
        "params": best_params,
        "avg_robust_logloss": float(best_avg_score)
    }

def main():
    print("🔥 BOOTING JUDAH BREACH MASTER CHEF (Offline Parameter Discovery)")
    print("===================================================================")
    
    df = build_features()
    if df is None or df.empty:
        return

    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    all_optimal_params = {}

    for h in HORIZONS:
        all_optimal_params[str(h)] = {}
        for side in ["PUT", "CALL"]:
            res = run_breach_grid_search(df, h, side)
            if res:
                all_optimal_params[str(h)][side] = res["params"]
            
    summary_path = os.path.join(MODEL_DIR, "breach_optimal_params.json")
    with open(summary_path, 'w') as f:
        json.dump(all_optimal_params, f, indent=4)
        
    print(f"\n🎉 MASTER CHEF COMPLETE! Wrote best parameter recipes to: {summary_path}")

if __name__ == "__main__":
    main()
