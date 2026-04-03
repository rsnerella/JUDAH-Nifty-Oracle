"""
scripts/integrity_check.py — Quick model/file integrity assertions.
Run this to verify expected PKLs/CSVs exist before launching the dashboard.
Usage: python scripts/integrity_check.py
"""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "data" / "models"

def expect(paths):
    missing = []
    for rel in paths:
        if not (MODELS / rel).exists():
            missing.append(rel)
    return missing

def main():
    checks = {
        "direction": [f"xgb_direction_{h}d.pkl" for h in [3,5,7,14,21,30]],
        "breach": [f"breach/xgb_breach_{side}_{h}d.pkl" for side in ["put","call"] for h in [3,5,7,14,21,30]],
        "monthly_breach": [f"monthly_breach/xgb_monthly_breach_{side}_{h}d.pkl" for side in ["put","call"] for h in [21,30]],
        "range_width": [f"range_width/xgb_range_{t}_{h}d.pkl" for t in ["cls","reg"] for h in [3,5,7,14]],
        "vol_crush": [f"vol_crush/xgb_vol_crush_{h}d.pkl" for h in [3,5,7,14]],
        "tail_risk": [f"tail_risk/xgb_tail_risk_{h}d.pkl" for h in [3,5,7]],
        "vix_direction": [f"vix_direction/xgb_vix_dir_{h}d.pkl" for h in [1,3,5,7]],
        "pcr_reversal": [f"pcr_reversal/xgb_pcr_rev_{h}d.pkl" for h in [3,5,7]],
        "regime_transition": [f"regime_transition/xgb_regime_shift_{h}d.pkl" for h in [3,5,7]],
        "max_drawdown": [f"max_drawdown/xgb_dd_{d}_{h}d.pkl" for d in ["down","up"] for h in [3,5,7,14]],
        "theta_decay": ["theta_decay/xgb_theta_decay.pkl"],
        "macro_sentiment": ["macro_sentiment/xgb_macro_sentiment.pkl"],
        "intraday_reversal": ["intraday_reversal/xgb_intraday_rev.pkl"],
        "expiry_vol": ["expiry_vol/xgb_expiry_vol.pkl"],
        "gap_risk": ["gap_risk/xgb_gap_risk.pkl", "gap_risk/xgb_gap_size_reg.pkl"],
        "global_contagion": ["global_contagion/xgb_gap_classifier.pkl", "global_contagion/xgb_gap_regressor.pkl"],
    }

    any_missing = False
    for name, paths in checks.items():
        missing = expect(paths)
        if missing:
            any_missing = True
            print(f"[WARN] {name}: {len(missing)} missing")
            for m in missing:
                print(f"   - {m}")
        else:
            print(f"[OK]   {name}: all present")

    if any_missing:
        exit(1)
    print("\nAll expected artifacts found.")

if __name__ == "__main__":
    main()
