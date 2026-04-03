"""
train_models.py — Convenience script to retrain the Nifty Oracle XGBoost models.
=============================================================================
Run this script to update models with the latest OHLCV and 15m data.
"""

import os
import sys
import pandas as pd
from engine.core import build_features
from engine.trainer_legacy import train_all_horizons

def main():
    print("🚀 Nifty Oracle Model Trainer")
    print("==============================")
    
    # 1. Build Features
    print("\nPhase 1: Feature Engineering...")
    try:
        df = build_features()
        if df is None or df.empty:
            print("❌ Error: build_features() returned empty DataFrame.")
            return
        print(f"✅ Features built: {len(df)} rows, {len(df.columns)} columns.")
    except Exception as e:
        print(f"❌ Error during feature engineering: {e}")
        return

    # 2. Train Models
    print("\nPhase 2: Training XGBoost Models (3d, 5d, 7d, 14d)...")
    try:
        results = train_all_horizons(df)
        if not results:
            print("⚠️ No models were trained. Check logs for details.")
        else:
            print(f"\n✅ Training Complete! Trained {len(results)} models.")
            for h in results:
                print(f"   - {h}d Horizon: COMPLETED")
    except Exception as e:
        print(f"❌ Error during training: {e}")
        return

    print("\n🎉 All set! Restart the dashboard to use the new models.")

if __name__ == "__main__":
    main()
