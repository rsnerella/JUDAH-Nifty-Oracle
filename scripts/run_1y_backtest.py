import sys, os, pandas as pd
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path: sys.path.insert(0, ROOT_DIR)
from scripts.backtest_breach import run_backtest, analyze_trades
from engine.core import build_features

def main():
    print("=== 1-YEAR NO-LOOKAHEAD BACKTEST ===")
    df = build_features()
    if df is None or df.empty: return
    df['date'] = pd.to_datetime(df['date'])
    latest_date = df['date'].max()
    start_date = latest_date - pd.Timedelta(days=365)
    import scripts.backtest_breach as bbt
    bbt.BACKTEST_START = start_date.strftime('%Y-%m-%d')
    horizons = [3, 5, 7, 21, 30]
    results = []
    for h in horizons:
        for s in ["put", "call"]:
            trades = run_backtest(df, h, s)
            if not trades: continue
            valid_trades = [t for t in trades if pd.to_datetime(t['date']) <= (latest_date - pd.Timedelta(days=h)) and pd.to_datetime(t['date']) >= start_date]
            if not valid_trades: continue
            st = analyze_trades(valid_trades, f"{s.upper()} {h}d")
            if st:
                tdf = pd.DataFrame(valid_trades)
                tdf['mo'] = pd.to_datetime(tdf['date']).dt.to_period('M')
                mc = tdf.groupby('mo').size()
                results.append({
                    "Horizon": f"{h}d", "Side": s.upper(), "Trades": st['total_trades'], "WinRate%": st['win_rate'],
                    "PNL": st['total_pnl_pts'], "Avg/Mo": round(mc.mean(), 1)
                })
    print("\n=== SUMMARY ===")
    res_df = pd.DataFrame(results)
    print(res_df.to_string(index=False) if not res_df.empty else "No results")
    if not res_df.empty:
        for h in horizons:
            hd = res_df[res_df["Horizon"]==f"{h}d"]
            print(f"Total Combined Trades/Month for {h}d: {hd['Avg/Mo'].sum():.1f}")
if __name__ == "__main__": main()
