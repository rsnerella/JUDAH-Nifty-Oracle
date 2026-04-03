"""
scripts/walkforward_backtest.py — Full Ensemble Walk-Forward Backtester
========================================================================
Runs the 16-model ensemble (via strike_selector) over historical data to 
validate aggregate performance.

IMPORTANT: Uses a fixed train/test cutoff to prevent look-ahead bias.
Models are loaded from disk (trained on data up to their training date).
The backtest only evaluates on dates AFTER the training cutoff.

For a truly clean test:
  1. Train all models using data up to CUTOFF_DATE
  2. Run this script — it only evaluates dates after CUTOFF_DATE
  3. The models never saw the test period during training

Usage: python scripts/walkforward_backtest.py
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from engine.core import build_features
from engine.strike_selector import select_strikes

# ── CONFIGURATION ──────────────────────────────────────────────────────────
# Only backtest on dates AFTER this cutoff.
# You must ensure models were trained on data BEFORE this date.
CUTOFF_DATE = '2024-06-01'   # Models trained on data up to ~mid-2024
HORIZON = 7                   # Days to expiry

def run_backtest(cutoff=CUTOFF_DATE, horizon=HORIZON):
    print("🚀 JUDAH Options ML: Walk-Forward Backtest (No Look-Ahead)")
    print(f"Horizon:       {horizon} days")
    print(f"Test Cutoff:   {cutoff} (only evaluating dates AFTER this)")
    print("="*60)
    
    print("[1] Building Feature Dataset...")
    df = build_features()
    if df is None or df.empty:
        print("❌ FAILED to build features.")
        return
    
    if 'date' not in df.columns:
        print("❌ No 'date' column found in features.")
        return
        
    df['date'] = pd.to_datetime(df['date'])
    
    # Split: only evaluate on out-of-sample period
    test_df = df[df['date'] >= cutoff].copy()
    
    if len(test_df) == 0:
        print(f"❌ No data found after {cutoff}.")
        return
    
    # We need future data to check outcomes, so exclude last `horizon` rows
    max_eval_date = df['date'].max() - pd.Timedelta(days=horizon + 5)
    test_df = test_df[test_df['date'] <= max_eval_date]
    
    print(f"[2] Evaluating {len(test_df)} trading days ({cutoff} → {max_eval_date.strftime('%Y-%m-%d')})...")
    print(f"    ⚠️  Models must have been trained on data BEFORE {cutoff} for valid results.")
    
    results = []
    skipped = 0
    
    for idx, (_, row) in enumerate(test_df.iterrows()):
        try:
            # Get ensemble decision
            verdict = select_strikes(row, df, horizon=horizon)
            
            trade_date = row['date']
            target_date = trade_date + pd.Timedelta(days=horizon)
            
            # Find the actual market data in the horizon window
            period_data = df[(df['date'] > trade_date) & (df['date'] <= target_date + pd.Timedelta(days=3))]
            
            if len(period_data) < 2:
                skipped += 1
                continue
            
            # Check maximum adverse excursion during the holding period
            min_low = period_data['low'].min()
            max_high = period_data['high'].max()
            
            put_strike = verdict['put_strike']
            call_strike = verdict['call_strike']
            strategy = verdict['strategy']
            
            # Determine outcome
            put_breached = min_low < put_strike if put_strike > 0 else False
            call_breached = max_high > call_strike if call_strike > 0 else False
            
            if strategy in ["NO TRADE", "WAITING"]:
                outcome = "NO TRADE"
            elif strategy == "BULL PUT SPREAD":
                outcome = "LOSS (PUT)" if put_breached else "WIN"
            elif strategy == "BEAR CALL SPREAD":
                outcome = "LOSS (CALL)" if call_breached else "WIN"
            elif strategy == "IRON CONDOR":
                if put_breached and call_breached:
                    outcome = "LOSS (BOTH)"
                elif put_breached:
                    outcome = "LOSS (PUT)"
                elif call_breached:
                    outcome = "LOSS (CALL)"
                else:
                    outcome = "WIN"
            else:
                outcome = "NO TRADE"
                
            results.append({
                'date': trade_date.strftime('%Y-%m-%d'),
                'spot': float(row['close']),
                'regime': verdict['regime'],
                'strategy': strategy,
                'confidence': verdict['confidence'],
                'size': verdict['size'],
                'put_strike': put_strike,
                'call_strike': call_strike,
                'put_buffer_pct': round((float(row['close']) - put_strike) / float(row['close']) * 100, 2) if put_strike > 0 else 0,
                'call_buffer_pct': round((call_strike - float(row['close'])) / float(row['close']) * 100, 2) if call_strike > 0 else 0,
                'min_low': min_low,
                'max_high': max_high,
                'outcome': outcome
            })
            
        except Exception as e:
            skipped += 1
            
    # ── RESULTS ────────────────────────────────────────────────────────────
    res_df = pd.DataFrame(results)
    if res_df.empty:
        print("\n❌ Backtest produced no results (possibly missing models).")
        return
    
    traded = res_df[res_df['outcome'] != "NO TRADE"]
    wins = traded[traded['outcome'] == 'WIN']
    losses = traded[traded['outcome'].str.startswith('LOSS')]
    win_rate = len(wins) / len(traded) * 100 if len(traded) > 0 else 0
    
    print("\n" + "="*60)
    print(f"📊 BACKTEST RESULTS (Out-of-Sample: {cutoff} onward)")
    print("="*60)
    print(f"Total Days Evaluated:    {len(res_df)}")
    print(f"Days Skipped:            {skipped}")
    print(f"Trade Signals Given:     {len(traded)} ({len(traded)/len(res_df)*100:.0f}% of days)")
    print(f"No-Trade Days:           {len(res_df) - len(traded)}")
    print(f"")
    print(f"  ✅ Wins:               {len(wins)}")
    print(f"  ❌ Losses:             {len(losses)}")
    print(f"  📈 WIN RATE:           {win_rate:.1f}%")
    
    # By strategy
    print(f"\n{'─'*60}")
    print("BY STRATEGY:")
    print(f"{'─'*60}")
    for strat in ['BULL PUT SPREAD', 'BEAR CALL SPREAD', 'IRON CONDOR']:
        strat_trades = traded[traded['strategy'] == strat]
        if len(strat_trades) > 0:
            strat_wins = (strat_trades['outcome'] == 'WIN').sum()
            strat_wr = strat_wins / len(strat_trades) * 100
            print(f"  {strat.ljust(20)}: {strat_wr:.1f}% win rate ({strat_wins}/{len(strat_trades)} trades)")
    
    # By regime
    print(f"\n{'─'*60}")
    print("BY REGIME:")
    print(f"{'─'*60}")
    for reg in ['GREEN', 'YELLOW', 'RED']:
        reg_trades = traded[traded['regime'] == reg]
        if len(reg_trades) > 0:
            reg_wins = (reg_trades['outcome'] == 'WIN').sum()
            reg_wr = reg_wins / len(reg_trades) * 100
            print(f"  {reg.ljust(20)}: {reg_wr:.1f}% win rate ({reg_wins}/{len(reg_trades)} trades)")
    
    # Monthly signal frequency
    print(f"\n{'─'*60}")
    print("MONTHLY SIGNAL FREQUENCY:")
    print(f"{'─'*60}")
    res_df['month'] = pd.to_datetime(res_df['date']).dt.to_period('M')
    for month in res_df['month'].unique():
        month_data = res_df[res_df['month'] == month]
        month_traded = month_data[month_data['outcome'] != 'NO TRADE']
        month_wins = (month_traded['outcome'] == 'WIN').sum() if len(month_traded) > 0 else 0
        print(f"  {str(month).ljust(10)}: {len(month_traded)} signals, {month_wins} wins")
    
    # Save
    out_path = os.path.join(ROOT_DIR, "data", f"walkforward_backtest_{horizon}d.csv")
    res_df.to_csv(out_path, index=False)
    print(f"\n💾 Detailed log saved to: {out_path}")
    
    # Summary stats
    print(f"\n{'='*60}")
    avg_put_buffer = traded['put_buffer_pct'].mean() if len(traded) > 0 else 0
    avg_call_buffer = traded['call_buffer_pct'].mean() if len(traded) > 0 else 0
    print(f"Avg Put Buffer:  {avg_put_buffer:.2f}% OTM")
    print(f"Avg Call Buffer: {avg_call_buffer:.2f}% OTM")
    print(f"Avg Signals/Month: {len(traded) / max(res_df['month'].nunique(), 1):.1f}")
    print(f"{'='*60}")

if __name__ == "__main__":
    run_backtest()
