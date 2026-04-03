"""
run_breach_sl_proxy.py
Approximate how often SL would be hit vs final outcome, using flo/fhi (max adverse move)
Assumptions:
  - Credit spread, 2.5% OTM
  - Width, Credit, Safety, Fees read from env (BB_WIDTH, BB_CREDIT, BB_SAFETY, etc.)
  - SL proxy: if max adverse move reaches short strike (flo <= -threshold for puts; fhi >= threshold for calls)
Limitations: uses only flo/fhi, not full price path. Coarse proxy.
"""

import os, sys, pandas as pd
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path: sys.path.insert(0, ROOT)

from engine.core import build_features, compute_regime_score, classify_regime, FEATURE_COLS
from scripts.backtest_breach import load_breach_model, predict_safety

def env_float(name, default): 
    try: return float(os.getenv(name, default))
    except: return default
def env_int(name, default):
    try: return int(os.getenv(name, default))
    except: return default

THRESHOLD_PCT = env_float("BB_THRESHOLD_PCT", 0.025)
SAFETY = env_float("BB_SAFETY", 0.65)
WIDTH = env_float("BB_WIDTH", 200)
CREDIT = env_float("BB_CREDIT", 24)
LOOKBACK = env_int("BB_LOOKBACK_DAYS", 365)

HORIZONS = [3,5,7]

def main():
    df = build_features()
    df['date']=pd.to_datetime(df['date'])
    latest=df['date'].max()
    df=df[df['date']>=latest-pd.Timedelta(days=LOOKBACK)]
    
    rows=[]
    for h in HORIZONS:
        m_put=load_breach_model('put',h)
        m_call=load_breach_model('call',h)
        if m_put is None or m_call is None: 
            continue
        for _,row in df.iterrows():
            score,_=compute_regime_score(row)
            regime=classify_regime(score)
            if regime not in ("GREEN","YELLOW"):
                continue
            spot=float(row.get('close',0) or 0)
            # put side
            o_put=f"flo_{h}d"
            if o_put in row and not pd.isna(row[o_put]):
                p_safe=predict_safety(m_put,row,FEATURE_COLS)
                if p_safe>=SAFETY:
                    flo=float(row[o_put])
                    breached = flo <= -THRESHOLD_PCT
                    sl_hit = breached  # proxy: hitting short strike
                    rows.append({"h":h,"side":"put","breached":breached,"sl_hit":sl_hit})
            # call side
            o_call=f"fhi_{h}d"
            if o_call in row and not pd.isna(row[o_call]):
                p_safe=predict_safety(m_call,row,FEATURE_COLS)
                if p_safe>=SAFETY:
                    fhi=float(row[o_call])
                    breached = fhi >= THRESHOLD_PCT
                    sl_hit = breached
                    rows.append({"h":h,"side":"call","breached":breached,"sl_hit":sl_hit})
    if not rows:
        print("No trades")
        return
    rdf=pd.DataFrame(rows)
    rdf['win']=~rdf['breached']
    summary = rdf.groupby(['h','side']).agg(trades=('win','count'),
                                            breaches=('breached','sum'),
                                            wins=('win','sum'))
    print("Breach (SL proxy) counts by horizon/side:")
    print(summary)
    print("\nTotal breaches:", int(rdf['breached'].sum()), "Trades:", len(rdf))

if __name__=="__main__":
    main()
