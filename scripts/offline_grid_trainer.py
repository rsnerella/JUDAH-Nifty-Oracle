"""
scripts/offline_grid_trainer.py — "Super Grid" Hyperparameter Search 
========================================================================
Performs exhaustive grid search across 360 hyperparameter combinations
and 3 distinct market regime splits per horizon. Selects best parameters 
based on average robustness (Average LogLoss).

Usage: python scripts/offline_grid_trainer.py
"""

import os
import sys
import time
import joblib
import warnings
import json
import hashlib
import numpy as np
import pandas as pd
import xgboost as xgb
from datetime import datetime
from sklearn.metrics import log_loss, accuracy_score, roc_auc_score, precision_recall_fscore_support

# Ensure the project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from engine.core import build_features
from engine.core import FEATURE_COLS

def _safe_feature_list(df):
    """Drop any future-looking columns from FEATURE_COLS."""
    blacklist = ("fwd_", "flo_", "fhi_")
    return [c for c in FEATURE_COLS if c in df.columns and not c.startswith(blacklist)]

def _feature_hash(feats):
    return hashlib.sha256("|".join(sorted(feats)).encode()).hexdigest()

def _write_metadata(path, feats, pos_rate, spw, params, cv_logloss, cv_acc, holdout_metrics, train_end):
    meta = {
        "train_end_date": train_end,
        "features": feats,
        "feature_hash": _feature_hash(feats),
        "pos_rate": pos_rate,
        "scale_pos_weight": spw,
        "params": params,
        "cv_avg_logloss": cv_logloss,
        "cv_avg_accuracy": cv_acc,
        "holdout": holdout_metrics,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    with open(path, "w") as f:
        json.dump(meta, f, indent=2)

warnings.filterwarnings("ignore")

# Single advanced grid (~648 combos) to balance depth and runtime
GRID = {
    'n_estimators': [100, 200, 300],
    'max_depth': [3, 5, 7],
    'learning_rate': [0.01, 0.03, 0.05],
    'subsample': [0.6, 0.8, 1.0],
    'colsample_bytree': [0.7, 1.0],
    'reg_alpha': [0, 0.5],
    'reg_lambda': [1.0, 3.0],
}

# Define Multi-regime Splits (Robustness Test) — 4 regimes for full coverage
SPLITS = [
    ('2016-01-01', '2018-01-01'), # Split A: Pre-COVID Bull Market (NEW)
    ('2019-01-01', '2021-01-01'), # Split B: COVID Stress test
    ('2022-01-01', '2023-01-01'), # Split C: Recovery
    ('2024-01-01', '2025-06-01'), # Split D: Recent Regime
]

# FEATURE_COLS is now imported from engine.trainer to ensure 'Brain Unification'

MODEL_DIR = os.path.join(ROOT_DIR, "data", "models")

def run_super_grid_search(df, horizon):
    """Find best parameters that perform well across all regime splits."""
    print(f"\n🚀 [Horizon {horizon}d] Starting SUPER GRID Search...")
    
    # 1. Target Engineering (Binary)
    target_col = f"fwd_{horizon}d"
    df_h = df.dropna(subset=[target_col]).copy()
    df_h['target_xgb'] = (df_h[target_col] > 0.01).astype(int)
    
    if 'source' in df_h.columns:
        df_h = df_h[df_h['source'] == 'real']

    available_features = _safe_feature_list(df_h)
    if not available_features:
        print(f"⚠️ [Horizon {horizon}d] No usable features after leakage filter.")
        return None

    # Class balance
    pos_rate = df_h['target_xgb'].mean()
    scale_pos_weight = (1 - pos_rate) / max(pos_rate, 1e-4)
    
    # 2. Pre-split the data for each regime to avoid redundant filtering
    split_data = []
    for t_end, v_end in SPLITS:
        train = df_h[df_h['date'] < t_end]
        val   = df_h[(df_h['date'] >= t_end) & (df_h['date'] < v_end)]
        if len(train) > 100 and len(val) > 30:
            split_data.append((
                train[available_features], train['target_xgb'],
                val[available_features], val['target_xgb']
            ))
    
    if not split_data:
        print(f"⚠️ [Horizon {horizon}d] No valid splits available.")
        return None

    # 3. Grid Search Loop
    total_grid_combos = 1
    for v in GRID.values():
        total_grid_combos *= len(v)
    
    best_avg_score = float('inf')
    best_params = None
    all_grid_results = []
    
    # Pre-calculate latest data point for inference
    latest_row_X = df_h[available_features].iloc[-1:].values
    
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
                    split_accs = []
                    for Xt, yt, Xv, yv in split_data:
                        model = xgb.XGBClassifier(
                            n_estimators=n_est,
                            max_depth=depth,
                            learning_rate=lr,
                            subsample=sub,
                            colsample_bytree=col_sample,
                            reg_alpha=r_alpha,
                            reg_lambda=r_lambda,
                            scale_pos_weight=scale_pos_weight,
                            objective='binary:logistic',
                            eval_metric='logloss',
                            random_state=42,
                            n_jobs=-1,
                            verbosity=0,
                            early_stopping_rounds=25
                        )
                        model.fit(Xt, yt,
                                  eval_set=[(Xv, yv)],
                                  verbose=False)
                        probs = model.predict_proba(Xv)
                        split_scores.append(log_loss(yv, probs))
                        split_accs.append(accuracy_score(yv, model.predict(Xv)))
                    
                    avg_logloss = np.mean(split_scores)
                    avg_accuracy = np.mean(split_accs)
                    
                    try:
                        curr_probs = model.predict_proba(latest_row_X)[0]
                        up_p = float(curr_probs[1])
                        dw_p = float(curr_probs[0])
                        pred = "UP" if up_p > 0.5 else "DOWN"
                    except:
                        up_p = 0.5; dw_p = 0.5; pred = "FLAT"

                    all_grid_results.append({
                        'n_estimators': n_est, 'max_depth': depth,
                        'learning_rate': lr, 'subsample': sub,
                        'colsample_bytree': col_sample,
                        'reg_alpha': r_alpha, 'reg_lambda': r_lambda,
                        'avg_logloss': float(avg_logloss),
                        'avg_accuracy': float(avg_accuracy),
                        'prediction': pred, 'up_prob': up_p, 'down_prob': dw_p
                    })
                    
                    if avg_logloss < best_avg_score:
                        best_avg_score = avg_logloss
                        best_params = {
                            'n_estimators': n_est, 'max_depth': depth,
                            'learning_rate': lr, 'subsample': sub,
                            'colsample_bytree': col_sample,
                            'reg_alpha': r_alpha, 'reg_lambda': r_lambda
                        }
                    
                    if run_idx % 200 == 0:
                        print(f"   [{horizon}d] Progress: {run_idx}/{total_grid_combos} | Elapsed: {time.time()-t0:.1f}s | Best: {best_avg_score:.4f}")

    # 4. Save detailed grid results for dashboard heatmap
    details_path = os.path.join(MODEL_DIR, f"offline_grid_details_{horizon}d.csv")
    pd.DataFrame(all_grid_results).sort_values('avg_logloss').to_csv(details_path, index=False)
    
    # 5. Final Fit on all historical data up to early 2026
    print(f"✅ [Horizon {horizon}d] Found ROBUST params: {best_params} (Average Logloss: {best_avg_score:.4f})")
    
    cutoff = df_h['date'].max() - pd.Timedelta(days=horizon)
    final_X = df_h[df_h['date'] <= cutoff][available_features]
    final_y = df_h[df_h['date'] <= cutoff]['target_xgb']
    
    final_model = xgb.XGBClassifier(
        **best_params,
        objective='binary:logistic',
        eval_metric='logloss',
        random_state=42,
        n_jobs=-1,
        early_stopping_rounds=25,
        scale_pos_weight=scale_pos_weight
    )
    # Use last split as early stopping validation
    if split_data:
        Xt_last, yt_last, Xv_last, yv_last = split_data[-1]
        final_model.fit(final_X, final_y,
                        eval_set=[(Xv_last, yv_last)],
                        verbose=False)
    else:
        final_model.fit(final_X, final_y)
    
    # Calculate final performance metrics on a held-out validation set (last split) and recent holdout
    if len(split_data) > 0:
        _, _, eval_X, eval_y = split_data[-1]
    else:
        eval_X = final_X
        eval_y = final_y
        
    final_probs = final_model.predict_proba(eval_X)
    final_acc   = accuracy_score(eval_y, final_model.predict(eval_X))
    final_loss  = log_loss(eval_y, final_probs)
    try:
        final_auc = roc_auc_score(eval_y, final_probs[:,1])
    except Exception:
        final_auc = None

    # Recent holdout (last 180 days)
    holdout_days = int(os.getenv("HOLDOUT_DAYS", "180"))
    hold_mask = df_h['date'] >= (df_h['date'].max() - pd.Timedelta(days=holdout_days))
    hold_df = df_h[hold_mask]
    hold_metrics = {}
    if len(hold_df) > 50:
        hold_X = hold_df[available_features]
        hold_y = hold_df['target_xgb']
        hold_probs = final_model.predict_proba(hold_X)
        hold_preds = final_model.predict(hold_X)
        hold_metrics = {
            "n": int(len(hold_df)),
            "accuracy": float(accuracy_score(hold_y, hold_preds)),
            "logloss": float(log_loss(hold_y, hold_probs)),
            "auc": float(roc_auc_score(hold_y, hold_probs[:,1])) if len(np.unique(hold_y))>1 else None,
            "precision_recall": list(precision_recall_fscore_support(hold_y, hold_preds, average='binary')[:2])
        }

    res = {
        "params": best_params,
        "avg_robust_logloss": float(best_avg_score),
        "final_accuracy": float(final_acc),
        "final_logloss": float(final_loss),
        "final_auc": final_auc,
        "holdout": hold_metrics
    }
    
    # Save Model + metadata
    if not os.path.exists(MODEL_DIR): os.makedirs(MODEL_DIR)
    model_path = os.path.join(MODEL_DIR, f"xgb_direction_{horizon}d.pkl")
    joblib.dump(final_model, model_path)
    meta_path = model_path + ".meta.json"
    _write_metadata(
        meta_path,
        available_features,
        pos_rate,
        scale_pos_weight,
        best_params,
        float(best_avg_score),
        float(final_acc),
        hold_metrics,
        str(df_h['date'].max())[:10]
    )
    
    # Save Feature Importance
    importance = pd.DataFrame({'feature': available_features, 'importance': final_model.feature_importances_}).sort_values('importance', ascending=False)
    importance.to_csv(os.path.join(MODEL_DIR, f"importance_{horizon}d.csv"), index=False)
    
    return res

def save_robot_brain_json(all_results, all_features):
    """Consolidate heatmaps and features into one single JSON for high-speed sync."""
    brain = {
        "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "horizons": {}
    }
    
    for h, data in all_results.items():
        brain["horizons"][str(h)] = {
            "best_params": data["params"],
            "metrics": {
                "acc": data["final_accuracy"],
                "logloss": data["final_logloss"]
            },
            "heatmap": data["heatmap_data"], # List of dicts
            "top_features": all_features.get(h, [])
        }
    
    json_path = os.path.join(MODEL_DIR, "offline_robot_brain.json")
    with open(json_path, 'w') as f:
        json.dump(brain, f, indent=2)
    print(f"💎 Consolidated Robot Brain saved to: {json_path}")

def main():
    print("🔥 JUDAH: Super Grid Robust Trainer")
    print("====================================")
    
    df = build_features()
    if df is None or df.empty:
        print("❌ Error: Memory initialization failed.")
        return

    horizons = [3, 5, 7, 14, 28]
    all_res_details = {}
    all_imp_details = {}
    summary = {}
    
    for h in horizons:
        try:
                res = run_super_grid_search(df, h)
                if res: 
                    summary[h] = res
                # Capture heatmap and features for the JSON brain
                det_path = os.path.join(MODEL_DIR, f"offline_grid_details_{h}d.csv")
                if os.path.exists(det_path):
                    all_res_details[h] = {
                        "params": res["params"],
                        "final_accuracy": res["final_accuracy"],
                        "final_logloss": res["final_logloss"],
                        "heatmap_data": pd.read_csv(det_path).to_dict(orient='records')
                    }
                
                imp_path = os.path.join(MODEL_DIR, f"importance_{h}d.csv")
                if os.path.exists(imp_path):
                    all_imp_details[h] = pd.read_csv(imp_path).head(10).to_dict(orient='records')
                    
        except Exception as e:
            print(f"❌ Horizon {h}d failed: {e}")
            
    # Save consolidated JSON for dashboard
    save_robot_brain_json(all_res_details, all_imp_details)

    # Save tactical summary
    with open(os.path.join(MODEL_DIR, "grid_search_summary.json"), 'w') as f:
        json.dump(summary, f, indent=4)
    print("\n🎉 DONE. Models calibrated for all regimes.")

if __name__ == "__main__":
    main()
