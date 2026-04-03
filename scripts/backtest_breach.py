"""
scripts/backtest_breach.py — Walk-Forward Backtest for Breach Radar
====================================================================
Simulates trading credit spreads using the breach model's signals
over historical data WITHOUT look-ahead bias.

Strategy:
  - Each day, check if breach model says SAFE (P(safe) >= threshold)
  - If SAFE + regime not RED → enter 600-pt OTM credit spread
  - Check if the actual flo/fhi in the next N days breached the strike
  - Track win/loss, premium collected, max loss hit

No look-ahead bias because:
  1. Features are all shift(1) lagged in build_features()
  2. We only use information available AT the time of the trade
  3. We check outcomes using actual future data (flo/fhi) which
     is the "answer key" — but we never feed it to the model

Usage: python scripts/backtest_breach.py
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

from engine.core import build_features, compute_regime_score, classify_regime
from engine.core import FEATURE_COLS

BREACH_DIR = os.path.join(ROOT_DIR, "data", "models", "breach")
RESULTS_DIR = os.path.join(ROOT_DIR, "data", "models", "breach")

# ── CONFIGURATION ────────────────────────────────────────────────────────────
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

THRESHOLD_PCT = _env_float("BB_THRESHOLD_PCT", 0.025)       # 2.5% ≈ 600 pts
SAFETY_THRESHOLD = _env_float("BB_SAFETY", 0.65)            # P(safe) ≥ 65% to enter
PREMIUM_CREDIT = _env_float("BB_CREDIT", 15)                # Gross credit per spread
TRANSACTION_COST_PER_LEG = _env_float("BB_FEE_PER_LEG", 5)  # Fee per leg
MAX_LOSS_WIDTH = _env_float("BB_WIDTH", 100)                # Width of spread
HORIZONS_TO_TEST = [3, 5, 7, 21, 30]
MAX_TRADES_PER_DAY = _env_int("BB_MAX_TRADES_PER_DAY", 5)   # cap concurrent new entries/day
BACKTEST_START = "2023-01-01"  # Only test on recent data (out of sample)


def load_breach_model(side, horizon):
    """Load a trained breach model."""
    path = os.path.join(BREACH_DIR, f"xgb_breach_{side}_{horizon}d.pkl")
    if not os.path.exists(path):
        return None
    return joblib.load(path)


def predict_safety(model, row, features):
    """Get P(safe) from model for a single row."""
    available = [f for f in features if f in row.index]
    vals = [float(row.get(f, 0) or 0) for f in available]
    X = pd.DataFrame([vals], columns=available)

    try:
        if hasattr(model, 'feature_names_in_'):
            model_feats = list(model.feature_names_in_)
            aligned = pd.DataFrame(0.0, index=[0], columns=model_feats)
            for f in model_feats:
                if f in X.columns:
                    aligned[f] = X[f].values[0]
            X = aligned
        probs = model.predict_proba(X)[0]
        return float(probs[1])  # P(safe)
    except:
        return 0.5


def run_backtest(df, horizon, side="put"):
    """
    Walk-forward backtest for one side/horizon.

    For each day in the backtest period:
      1. Get the breach model prediction using THAT day's features
      2. Check regime using THAT day's features
      3. If signal says ENTER → check actual outcome (did strike survive?)
      4. Record P/L
    """
    model = load_breach_model(side, horizon)
    if model is None:
        print(f"  No model for {side} {horizon}d")
        return None

    # Determine target column
    if side == "put":
        outcome_col = f"flo_{horizon}d"  # max drawdown in next N days
    else:
        outcome_col = f"fhi_{horizon}d"  # max rally in next N days

    if outcome_col not in df.columns:
        print(f"  Missing {outcome_col}")
        return None

    # Filter to backtest period
    bt_df = df[df['date'] >= BACKTEST_START].copy()
    # Need outcome data, so remove last N rows where we don't have outcomes
    bt_df = bt_df.dropna(subset=[outcome_col])

    if len(bt_df) < 30:
        print(f"  Too few rows for backtest: {len(bt_df)}")
        return None

    trades = []
    trades_per_day = {}
    features = FEATURE_COLS

    for idx in range(len(bt_df)):
        row = bt_df.iloc[idx]
        date = row['date']
        spot = float(row.get('close', 0) or 0)
        if spot == 0:
            continue

        # 1. Get breach prediction
        p_safe = predict_safety(model, row, features)

        # 2. Check regime
        reg_score, _ = compute_regime_score(row)
        regime = classify_regime(reg_score)

        # 3. Entry decision
        regime_ok = regime in ["GREEN", "YELLOW"]
        signal_ok = p_safe >= SAFETY_THRESHOLD

        day_str = str(date)[:10]
        trades_per_day.setdefault(day_str, 0)

        # Enforce daily cap
        if trades_per_day[day_str] >= MAX_TRADES_PER_DAY:
            continue

        if not signal_ok or not regime_ok:
            continue  # Skip — no trade

        # 4. Check actual outcome
        actual_excursion = float(row[outcome_col])

        if side == "put":
            # Bull Put Spread: strike = spot - 600 pts (~2.5%)
            # SAFE if flo > -threshold (low didn't breach)
            strike = spot * (1 - THRESHOLD_PCT)
            breached = actual_excursion <= -THRESHOLD_PCT
        else:
            # Bear Call Spread: strike = spot + 600 pts (~2.5%)
            # SAFE if fhi < +threshold (high didn't breach)
            strike = spot * (1 + THRESHOLD_PCT)
            breached = actual_excursion >= THRESHOLD_PCT

        # 5. Calculate P/L
        total_cost = TRANSACTION_COST_PER_LEG * 2  # two legs
        net_credit = PREMIUM_CREDIT - total_cost

        if not breached:
            pnl = net_credit  # Win — credit minus costs
            result = "WIN"
        else:
            pnl = -MAX_LOSS_WIDTH + PREMIUM_CREDIT - total_cost  # Loss — width minus net credit
            result = "LOSS"

        trades.append({
            "date": str(date)[:10],
            "spot": round(spot),
            "strike": round(strike),
            "p_safe": round(p_safe, 3),
            "regime": regime,
            "regime_score": reg_score,
            "actual_excursion": round(actual_excursion * 100, 2),
            "breached": breached,
            "result": result,
            "pnl_pts": pnl,
        })
        trades_per_day[day_str] += 1

    return trades


def analyze_trades(trades, label=""):
    """Analyze trade results."""
    if not trades:
        print(f"  {label}: No trades generated.")
        return None

    df = pd.DataFrame(trades)
    total = len(df)
    wins = len(df[df['result'] == 'WIN'])
    losses = len(df[df['result'] == 'LOSS'])
    win_rate = wins / total * 100
    total_pnl = df['pnl_pts'].sum()
    avg_pnl = df['pnl_pts'].mean()
    max_drawdown = df['pnl_pts'].cumsum().min()
    avg_p_safe = df['p_safe'].mean()

    # Monthly signal count
    df['month'] = pd.to_datetime(df['date']).dt.to_period('M')
    signals_per_month = df.groupby('month').size().mean()

    # Win streaks and loss streaks
    results = df['result'].values
    max_win_streak = 0
    max_loss_streak = 0
    current_streak = 0
    for i, r in enumerate(results):
        if i == 0:
            current_streak = 1
        elif r == results[i-1]:
            current_streak += 1
        else:
            current_streak = 1
        if r == 'WIN':
            max_win_streak = max(max_win_streak, current_streak)
        else:
            max_loss_streak = max(max_loss_streak, current_streak)

    stats = {
        "total_trades": total,
        "wins": wins,
        "losses": losses,
        "win_rate": round(win_rate, 1),
        "total_pnl_pts": round(total_pnl),
        "avg_pnl_per_trade": round(avg_pnl, 1),
        "max_drawdown_pts": round(max_drawdown),
        "avg_p_safe": round(avg_p_safe, 3),
        "signals_per_month": round(signals_per_month, 1),
        "max_win_streak": max_win_streak,
        "max_loss_streak": max_loss_streak,
    }

    return stats


def print_results(label, stats, trades):
    """Pretty print results."""
    if not stats:
        return

    win_color = "\033[92m" if stats['win_rate'] >= 65 else "\033[93m" if stats['win_rate'] >= 55 else "\033[91m"
    pnl_color = "\033[92m" if stats['total_pnl_pts'] > 0 else "\033[91m"
    reset = "\033[0m"

    print(f"\n  {'='*60}")
    print(f"  {label}")
    print(f"  {'='*60}")
    print(f"  Total Trades:      {stats['total_trades']}")
    print(f"  Wins/Losses:       {stats['wins']}/{stats['losses']}")
    print(f"  Win Rate:          {win_color}{stats['win_rate']}%{reset}")
    print(f"  Total P/L:         {pnl_color}{stats['total_pnl_pts']:+} pts{reset}")
    print(f"  Avg P/L per trade: {stats['avg_pnl_per_trade']:+.1f} pts")
    print(f"  Max Drawdown:      {stats['max_drawdown_pts']} pts")
    print(f"  Avg P(safe) at entry: {stats['avg_p_safe']:.1%}")
    print(f"  Signals/Month:     {stats['signals_per_month']:.1f}")
    print(f"  Max Win Streak:    {stats['max_win_streak']}")
    print(f"  Max Loss Streak:   {stats['max_loss_streak']}")

    # Show worst losses
    df = pd.DataFrame(trades)
    worst = df[df['result'] == 'LOSS'].sort_values('actual_excursion')
    if not worst.empty:
        print(f"\n  Worst 5 Losses:")
        for _, row in worst.head(5).iterrows():
            print(f"    {row['date']} | Spot {row['spot']:,} | Excursion {row['actual_excursion']:+.2f}% | P(safe) was {row['p_safe']:.1%}")

    # Show monthly breakdown
    df['month'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m')
    monthly = df.groupby('month').agg(
        trades=('result', 'count'),
        wins=('result', lambda x: (x == 'WIN').sum()),
        pnl=('pnl_pts', 'sum')
    ).reset_index()
    print(f"\n  Monthly Breakdown:")
    print(f"  {'Month':<10} {'Trades':>7} {'Wins':>6} {'P/L':>8}")
    print(f"  {'-'*35}")
    for _, row in monthly.iterrows():
        pnl_str = f"{row['pnl']:+.0f}"
        print(f"  {row['month']:<10} {row['trades']:>7} {row['wins']:>6} {pnl_str:>8}")


def main():
    print("=" * 70)
    print("  BREACH RADAR BACKTEST — Walk-Forward (No Look-Ahead)")
    print(f"  Period: {BACKTEST_START} to present")
    print(f"  Safety threshold: P(safe) >= {SAFETY_THRESHOLD:.0%}")
    print(f"  Breach threshold: +/-{THRESHOLD_PCT*100:.1f}% (~600 pts)")
    print(f"  Credit: {PREMIUM_CREDIT} pts | Max Loss: {MAX_LOSS_WIDTH} pts")
    print("=" * 70)

    print("\nBuilding features...")
    df = build_features()
    if df is None or df.empty:
        print("Failed to build features.")
        return

    print(f"Loaded {len(df)} rows.")

    all_results = {}

    for horizon in HORIZONS_TO_TEST:
        print(f"\n{'#'*70}")
        print(f"  HORIZON: {horizon} DAYS")
        print(f"{'#'*70}")

        for side in ["put", "call"]:
            label = f"{'Bull Put' if side == 'put' else 'Bear Call'} Spread ({horizon}d)"
            trades = run_backtest(df, horizon, side)
            if trades:
                stats = analyze_trades(trades, label)
                print_results(label, stats, trades)
                all_results[f"{side}_{horizon}d"] = {
                    "stats": stats,
                    "trades": trades
                }

    # Save results
    save_path = os.path.join(RESULTS_DIR, "backtest_results.json")

    # Convert for JSON serialization
    save_data = {}
    for key, val in all_results.items():
        save_data[key] = {
            "stats": val["stats"],
            "trade_count": len(val["trades"]),
            "sample_trades": val["trades"][:10] + val["trades"][-5:] if len(val["trades"]) > 15 else val["trades"]
        }

    with open(save_path, 'w') as f:
        json.dump(save_data, f, indent=2)
    print(f"\nResults saved to: {save_path}")

    # ── OVERALL SUMMARY ──────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  OVERALL SUMMARY")
    print("=" * 70)

    for key, val in all_results.items():
        s = val["stats"]
        win_emoji = "+" if s["win_rate"] >= 65 else "~" if s["win_rate"] >= 55 else "!"
        pnl_emoji = "+" if s["total_pnl_pts"] > 0 else "-"
        print(f"  [{win_emoji}] {key:<15} | WR: {s['win_rate']:>5.1f}% | P/L: {s['total_pnl_pts']:>+6} pts | {s['signals_per_month']:.1f} sig/mo | {s['total_trades']} trades")

    # Best strategy recommendation
    best = max(all_results.items(), key=lambda x: x[1]["stats"]["total_pnl_pts"])
    print(f"\n  >>> BEST: {best[0]} — Win Rate {best[1]['stats']['win_rate']}%, P/L {best[1]['stats']['total_pnl_pts']:+} pts")


if __name__ == "__main__":
    main()
