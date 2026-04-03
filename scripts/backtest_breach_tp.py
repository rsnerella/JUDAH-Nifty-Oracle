"""
scripts/backtest_breach_tp.py — Backtest with simple TP/SL approximations
Uses underlying-only path (daily rows) to simulate:
  - TP: assume a winning trade captures TP_PCT of credit (default 0.6 = 60%)
  - SL: on a breach, loss is min(width - credit, credit * SL_X) (default SL_X=2)
NOTE: This is an approximation because we don't track intra-path option pricing.
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from engine.core import build_features, compute_regime_score, classify_regime, FEATURE_COLS

BREACH_DIR = os.path.join(ROOT_DIR, "data", "models", "breach")

def _env_float(name, default):
    try:
        return float(os.getenv(name, default))
    except Exception:
        return default

def _env_int(name, default):
    try:
        return int(os.getenv(name, default))
    except Exception:
        return default

THRESHOLD_PCT = _env_float("BB_THRESHOLD_PCT", 0.025)
SAFETY_THRESHOLD = _env_float("BB_SAFETY", 0.65)
PREMIUM_CREDIT = _env_float("BB_CREDIT", 15)
TRANSACTION_COST_PER_LEG = _env_float("BB_FEE_PER_LEG", 5)
MAX_LOSS_WIDTH = _env_float("BB_WIDTH", 100)
TP_PCT = _env_float("BB_TP_PCT", 0.6)      # fraction of credit kept on wins
SL_X = _env_float("BB_SL_X", 2.0)          # multiple of credit lost on breach
HORIZONS = [3,5,7]
BACKTEST_DAYS = int(os.getenv("BB_LOOKBACK_DAYS", 365))

def load_breach_model(side, horizon):
    path = os.path.join(BREACH_DIR, f"xgb_breach_{side}_{horizon}d.pkl")
    if not os.path.exists(path):
        return None
    return joblib.load(path)

def predict_safety(model, row, features):
    available = [f for f in features if f in row.index]
    vals = [float(row.get(f, 0) or 0) for f in available]
    X = pd.DataFrame([vals], columns=available)
    try:
        if hasattr(model, 'feature_names_in_'):
            model_feats = list(model.feature_names_in_)
            aligned = pd.DataFrame(0.0, index=[0], columns=model_feats)
            for f in model_feats:
                if f in X.columns: aligned[f] = X[f].values[0]
            X = aligned
        probs = model.predict_proba(X)[0]
        return float(probs[1])
    except:
        return 0.5

def run_backtest(df, horizon, side="put"):
    model = load_breach_model(side, horizon)
    if model is None:
        return []
    outcome_col = f"flo_{horizon}d" if side=="put" else f"fhi_{horizon}d"
    if outcome_col not in df.columns:
        return []
    bt_df = df.dropna(subset=[outcome_col]).copy()
    trades=[]
    for _,row in bt_df.iterrows():
        p_safe = predict_safety(model, row, FEATURE_COLS)
        score,_ = compute_regime_score(row)
        regime = classify_regime(score)
        if regime not in ("GREEN","YELLOW"):
            continue
        if p_safe < SAFETY_THRESHOLD:
            continue
        spot = float(row.get("close",0) or 0)
        if spot==0: continue
        # Entry economics
        credit = PREMIUM_CREDIT
        fee = TRANSACTION_COST_PER_LEG*2
        width = MAX_LOSS_WIDTH
        outcome = float(row[outcome_col])
        breached = outcome <= -THRESHOLD_PCT if side=="put" else outcome >= THRESHOLD_PCT
        if breached:
            loss_pts = min(width - credit, credit*SL_X) + fee
            pnl = -loss_pts
            result="LOSS"
        else:
            pnl = credit*TP_PCT - fee
            result="WIN"
        trades.append({
            "date": str(row['date'])[:10],
            "side": side,
            "h": horizon,
            "regime": regime,
            "p_safe": p_safe,
            "result": result,
            "pnl_pts": pnl
        })
    return trades

def main():
    df = build_features()
    df['date']=pd.to_datetime(df['date'])
    latest=df['date'].max()
    df = df[df['date']>= latest-pd.Timedelta(days=BACKTEST_DAYS)]
    all_trades=[]
    for h in HORIZONS:
        for s in ["put","call"]:
            all_trades.extend(run_backtest(df,h,s))
    tdf=pd.DataFrame(all_trades)
    if tdf.empty:
        print("No trades")
        return
    tdf['date']=pd.to_datetime(tdf['date'])
    tdf['month']=tdf['date'].dt.to_period('M')
    summary = tdf.groupby('month')['pnl_pts'].sum().to_frame('pnl_pts')
    summary['pnl_inr']=summary['pnl_pts']*65
    print("Monthly PnL with TP/SL approximation:")
    print(summary)
    print("\nTotal PnL pts:", tdf['pnl_pts'].sum(), "INR:", tdf['pnl_pts'].sum()*65)
    print("Trades:", len(tdf), "Wins:", (tdf['result']=='WIN').sum(), "Losses:", (tdf['result']=='LOSS').sum())

if __name__=="__main__":
    main()
