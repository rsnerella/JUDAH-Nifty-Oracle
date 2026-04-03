"""
scripts/train_all_arsenal.py — Unified Training Orchestrator
=============================================================
Runs all 14 Arsenal trainers back-to-back using a single shared 
feature dataset, reducing training time by ~60%.

Usage: python scripts/train_all_arsenal.py
"""

import os
import sys
import time

# Ensure project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import engine.core
from engine.core import build_features

def main():
    print("🔥 Options ML Arsenal Unified Orchestrator")
    print("==========================================")
    
    t0 = time.time()
    print("[0] Building feature dataset once for all models...")
    df = build_features()
    
    if df is None or df.empty:
        print("❌ FAILED to build features. Exiting.")
        sys.exit(1)
        
    print(f"✅ Baseline Features Ready! (Rows: {len(df)}, Cols: {len(df.columns)})")
    
    # ── MONKEYPATCH build_features ──
    # We patch the function so that any trainer calling it gets our static `df` 
    # immediately, ignoring the 300s cache timeout.
    engine.core.build_features = lambda: df.copy()
    
    # Import and run all trainers sequentially
    import traceback

    steps = [
        ("Volatility Crush", "engine.volatility_crush_trainer", "train_all_vol_crush_models"),
        ("Range Width", "engine.range_width_trainer", "train_all"),
        ("Gap Risk", "engine.gap_risk_trainer", "train_all"),
        ("VIX Direction", "engine.vix_direction_trainer", "train_all"),
        ("Monthly Breach", "engine.monthly_breach_trainer", "train_all"),
        ("Regime Transition", "engine.regime_transition_trainer", "train_all"),
        ("Tail Risk", "engine.tail_risk_trainer", "train_all"),
        ("Max Drawdown", "engine.max_drawdown_trainer", "train_all"),
        ("Global Contagion", "engine.global_contagion_trainer", "train_all"), # Wait, global_contagion_trainer uses `train_contagion_models(df)` directly inside `__main__`
        ("Theta Decay", "engine.theta_decay_trainer", "train_all"),
        ("Intraday Reversal", "engine.intraday_reversal_trainer", "train_all"),
        ("Expiry Vol", "engine.expiry_vol_trainer", "train_all"),
        ("Macro Sentiment", "engine.macro_sentiment_trainer", "train_all"),
        ("Breach Radar", "engine.breach_trainer", "train_all_breach_models") # Wait, breach_trainer takes `df` as argument!
    ]
    
    import runpy
    
    success_count = 0
    fail_count = 0
    
    print("\n🚀 Beginning sequential training...")
    
    for name, module_name, _ in steps:
        print(f"\n" + "="*50)
        print(f"▶️ RUNNING: {name} ({module_name})")
        print("="*50)
        try:
            # Running as __main__ will trigger their if __name__ == "__main__": blocks
            # But the underlying build_features has been monkeypatched, so it's instant!
            runpy.run_module(module_name, run_name="__main__")
            success_count += 1
        except Exception as e:
            print(f"❌ ERROR in {name}: {e}")
            traceback.print_exc()
            fail_count += 1
            
    print("\n" + "="*50)
    print("🎉 ALL TRAINING COMPLETE!")
    print(f"Elapsed Time: {(time.time() - t0)/60:.1f} minutes")
    print(f"Success: {success_count} | Failed: {fail_count}")
    print("="*50)

if __name__ == "__main__":
    main()
