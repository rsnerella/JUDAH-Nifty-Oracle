"""
engine/breach_trainer.py — Credit Spread Breach Model Trainer
==============================================================
COMPLETELY SEPARATE from the directional trainer.
Does NOT modify any existing JUDAH models or training.

Trains XGBoost to answer the credit spread seller's question:
  "Will my 600-point OTM strike SURVIVE the next N days?"

Two models per horizon:
  1. PUT SAFETY:  P(flo_Nd > -threshold)  → "Will my sold put survive?"
  2. CALL SAFETY: P(fhi_Nd < +threshold)  → "Will my sold call survive?"

Usage: python -m engine.breach_trainer
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, log_loss, classification_report
from sklearn.calibration import CalibratedClassifierCV
from datetime import datetime

# Ensure project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from engine.core import FEATURE_COLS  # Reuse same features, different target

MODEL_DIR = os.path.join(ROOT_DIR, "data", "models", "breach")

# ── CONFIGURATION ────────────────────────────────────────────────────────────
# 600 points on Nifty ~22000-24000 ≈ 2.5-2.7%
# We use percentage-based thresholds so it adapts to Nifty level
BREACH_THRESHOLD_PCT = 0.025  # 2.5% = ~600 points at Nifty 24000

HORIZONS = [3, 5, 7, 14, 28]  # Days to expiry


def train_breach_models(df, horizon=7, threshold=BREACH_THRESHOLD_PCT):
    """
    Train two separate breach models for a given horizon:
      1. PUT SAFETY MODEL:  Will flo_Nd > -threshold? (put strike survives)
      2. CALL SAFETY MODEL: Will fhi_Nd < +threshold? (call strike survives)
    """
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    optimal_params = {}
    params_path = os.path.join(MODEL_DIR, "breach_optimal_params.json")
    if os.path.exists(params_path):
        import json
        try:
            with open(params_path, "r") as f:
                full_params = json.load(f)
            if str(horizon) in full_params:
                optimal_params = full_params[str(horizon)]
        except Exception as e:
            print(f"  ⚠️ Could not load optimal params: {e}")

    # Validate features
    available_features = [c for c in FEATURE_COLS if c in df.columns]
    if len(available_features) < 10:
        print(f"  ⚠️ Skipping {horizon}d: Only {len(available_features)} features.")
        return None

    # Check target columns exist
    flo_col = f"flo_{horizon}d"
    fhi_col = f"fhi_{horizon}d"
    if flo_col not in df.columns or fhi_col not in df.columns:
        print(f"  ⚠️ Skipping {horizon}d: Missing {flo_col} or {fhi_col}.")
        return None

    results = {}

    for side, target_col, safe_condition, model_name in [
        ("PUT",  flo_col, f"> -{threshold}", f"xgb_breach_put_{horizon}d.pkl"),
        ("CALL", fhi_col, f"< +{threshold}", f"xgb_breach_call_{horizon}d.pkl"),
    ]:
        print(f"\n  {'='*60}")
        print(f"  🛡️ Training {side} SAFETY model ({horizon}d, threshold ±{threshold*100:.1f}%)")
        print(f"  {'='*60}")

        # Create binary target
        if side == "PUT":
            # SAFE (1) = low didn't breach below -threshold
            # DANGER (0) = low breached below -threshold
            df_model = df.copy()
            adaptive_threshold = (df_model['atr20'] * 2) / df_model['close']
            df_model['target_breach'] = (df_model[target_col] > -adaptive_threshold).astype(int)
        else:
            # SAFE (1) = high didn't breach above +threshold
            # DANGER (0) = high breached above +threshold
            df_model = df.copy()
            adaptive_threshold = (df_model['atr20'] * 2) / df_model['close']
            df_model['target_breach'] = (df_model[target_col] < adaptive_threshold).astype(int)

        # Drop NaN rows
        cols_needed = available_features + ['target_breach']
        if 'source' in df_model.columns:
            cols_needed.append('source')
        model_df = df_model[cols_needed].dropna()

        # Filter synthetic data
        if 'source' in model_df.columns:
            initial = len(model_df)
            model_df = model_df[model_df['source'] == 'real']
            if initial > len(model_df):
                print(f"  🛡️ Filtered {initial - len(model_df)} synthetic rows.")

        if len(model_df) < 200:
            print(f"  ⚠️ Only {len(model_df)} rows — skipping.")
            continue

        X = model_df[available_features]
        y = model_df['target_breach']

        # Class balance report
        safe_pct = y.mean() * 100
        breach_pct = (1 - y.mean()) * 100
        print(f"  📊 Class balance: SAFE={safe_pct:.1f}% | BREACH={breach_pct:.1f}%")
        print(f"  📊 Total samples: {len(y)}")

        # ── Setup XGBoost Params ──────────────────────────────────────────
        xgb_params = {
            'n_estimators': 400,
            'max_depth': 4,
            'learning_rate': 0.03,
            'subsample': 0.8,
            'colsample_bytree': 0.7,
            'reg_alpha': 0.15,
            'reg_lambda': 2.0,
            'gamma': 0.15,
        }
        
        if side in optimal_params:
            xgb_params.update(optimal_params[side])
            print(f"  🧠 Using Offline Master Chef recipes for {side} {horizon}d")
        
        xgb_params.update({
            'scale_pos_weight': breach_pct / max(safe_pct, 1),
            'objective': 'binary:logistic',
            'random_state': 42,
            'eval_metric': 'logloss',
            'early_stopping_rounds': 25
        })

        # ── Time Series Cross-Validation (5-fold) ────────────────────────
        tscv = TimeSeriesSplit(n_splits=5)
        cv_accs = []
        cv_losses = []

        for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

            model = xgb.XGBClassifier(**xgb_params)
            model.fit(X_train, y_train,
                      eval_set=[(X_test, y_test)],
                      verbose=False)

            preds = model.predict(X_test)
            probs = model.predict_proba(X_test)
            acc = accuracy_score(y_test, preds)
            loss = log_loss(y_test, probs)
            cv_accs.append(acc)
            cv_losses.append(loss)

        avg_acc = np.mean(cv_accs)
        avg_loss = np.mean(cv_losses)
        print(f"  ✅ CV Results: Accuracy={avg_acc:.2%} | LogLoss={avg_loss:.4f}")

        # ── Final model on all data ──────────────────────────────────────
        split_point = int(len(X) * 0.85)
        X_train_f, X_val_f = X.iloc[:split_point], X.iloc[split_point:]
        y_train_f, y_val_f = y.iloc[:split_point], y.iloc[split_point:]

        final_model = xgb.XGBClassifier(**xgb_params)
        final_model.fit(X_train_f, y_train_f,
                        eval_set=[(X_val_f, y_val_f)],
                        verbose=False)
        
        # Calibrate probabilities (handles scikit-learn >= 1.6.0 deprecation of cv='prefit')
        try:
            from sklearn.calibration import FrozenEstimator
            calibrated_final = CalibratedClassifierCV(estimator=FrozenEstimator(final_model), method='isotonic')
        except ImportError:
            calibrated_final = CalibratedClassifierCV(final_model, cv='prefit', method='isotonic')
            
        calibrated_final.fit(X_val_f, y_val_f)
        # Propagate feature names so dashboard modules can align features
        if hasattr(final_model, 'feature_names_in_'):
            calibrated_final.feature_names_in_ = final_model.feature_names_in_

        # Save model
        save_path = os.path.join(MODEL_DIR, model_name)
        joblib.dump(calibrated_final, save_path)
        print(f"  💾 Saved: {save_path}")

        # Save feature importance
        importance = pd.DataFrame({
            'feature': available_features,
            'importance': final_model.feature_importances_
        }).sort_values('importance', ascending=False)
        imp_path = os.path.join(MODEL_DIR, f"importance_breach_{side.lower()}_{horizon}d.csv")
        importance.to_csv(imp_path, index=False)

        # Final validation metrics
        val_preds = calibrated_final.predict(X_val_f)
        val_probs = calibrated_final.predict_proba(X_val_f)
        val_acc = accuracy_score(y_val_f, val_preds)
        val_loss = log_loss(y_val_f, val_probs)

        print(f"  🎯 Final Validation: Accuracy={val_acc:.2%} | LogLoss={val_loss:.4f}")
        print(f"  📋 Classification Report:")
        print(classification_report(y_val_f, val_preds, 
              target_names=["BREACH ⚠️", "SAFE ✅"], zero_division=0))

        results[side] = {
            "cv_accuracy": float(avg_acc),
            "cv_logloss": float(avg_loss),
            "val_accuracy": float(val_acc),
            "val_logloss": float(val_loss),
            "safe_pct": float(safe_pct),
            "breach_pct": float(breach_pct),
            "n_samples": len(y),
            "n_features": len(available_features),
            "model_path": save_path,
        }

    return results


def train_all_breach_models(df):
    """Train breach models for all horizons."""
    import json
    all_results = {}

    for h in HORIZONS:
        print(f"\n{'#'*70}")
        print(f"  HORIZON: {h} DAYS")
        print(f"{'#'*70}")
        res = train_breach_models(df, horizon=h)
        if res:
            all_results[h] = res

    # Save summary JSON
    summary = {
        "last_trained": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "threshold_pct": BREACH_THRESHOLD_PCT * 100,
        "threshold_desc": f"±{BREACH_THRESHOLD_PCT*100:.1f}% (~600 pts at Nifty 24000)",
        "horizons": {}
    }
    for h, data in all_results.items():
        summary["horizons"][str(h)] = data

    summary_path = os.path.join(MODEL_DIR, "breach_summary.json")
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\n💎 Breach summary saved: {summary_path}")

    return all_results


if __name__ == "__main__":
    from engine.core import build_features
    print("🛡️ BREACH RADAR — Credit Spread Safety Trainer")
    print("=" * 60)
    print(f"Threshold: ±{BREACH_THRESHOLD_PCT*100:.1f}% (~600 pts)")
    print(f"Horizons: {HORIZONS}")
    print("=" * 60)

    print("\n📦 Building features...")
    df = build_features()
    if df is None or df.empty:
        print("❌ Failed to build features.")
        sys.exit(1)

    print(f"✅ {len(df)} rows, {len(df.columns)} columns loaded.")
    train_all_breach_models(df)
    print("\n🎉 BREACH RADAR training complete!")
