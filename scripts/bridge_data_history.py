import pandas as pd
import numpy as np
import os
import sys

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

def bridge_history():
    print("🚀 Starting JUDAH Historical Data Bridge...")
    
    nifty_path = os.path.join(DATA_DIR, "nifty_daily.csv")
    if not os.path.exists(nifty_path):
        print(f"❌ Error: {nifty_path} not found.")
        return

    nifty = pd.read_csv(nifty_path)
    nifty['date'] = pd.to_datetime(nifty['date'])
    nifty = nifty.sort_values('date')
    
    # 1. GENERATE PCR PROXY (Volatility Inverse Logic)
    # --------------------------------------------------------------------------
    print("📈 Generating PCR Proxies (VIX Correlation)...")
    pcr_path = os.path.join(DATA_DIR, "pcr_daily.csv")
    
    # Existing PCR data (if any)
    existing_pcr = pd.DataFrame(columns=['date', 'pcr'])
    if os.path.exists(pcr_path) and os.path.getsize(pcr_path) > 10:
        existing_pcr = pd.read_csv(pcr_path)
        existing_pcr['date'] = pd.to_datetime(existing_pcr['date'])

    # Logic: PCR usually drifts between 0.7 and 1.4. 
    # High VIX = Low PCR. Low VIX = High PCR.
    vix = nifty['vix'].fillna(nifty['vix'].mean())
    vix_z = (vix - vix.rolling(20).mean()) / vix.rolling(20).std()
    vix_z = vix_z.fillna(0)
    
    # Base PCR 1.0, minus 0.1 for every 1 std VIX spike
    pcr_proxy = 1.05 - (vix_z * 0.12)
    # Clip to realistic bounds
    pcr_proxy = pcr_proxy.clip(0.65, 1.45)
    
    pcr_bridge = pd.DataFrame({
        'date': nifty['date'],
        'pcr': pcr_proxy
    })
    
    # Merge: Prefer real data, fill history with proxy
    final_pcr = pcr_bridge.merge(existing_pcr, on='date', how='left', suffixes=('_prox', '_real'))
    final_pcr['pcr'] = final_pcr['pcr_real'].fillna(final_pcr['pcr_prox'])
    final_pcr['source'] = np.where(final_pcr['pcr_real'].isna(), 'synthetic', 'real')
    final_pcr = final_pcr[['date', 'pcr', 'source']].sort_values('date')
    final_pcr.to_csv(pcr_path, index=False)
    print(f"✅ PCR Bridged: {len(final_pcr)} rows saved.")

    # 2. GENERATE FII PROXY (Market Return Logic)
    # --------------------------------------------------------------------------
    print("💰 Generating FII Net Proxies (Return Correlation)...")
    fii_path = os.path.join(DATA_DIR, "fii_dii_daily.csv")
    
    existing_fii = pd.DataFrame(columns=['date', 'fii_net', 'dii_net'])
    if os.path.exists(fii_path) and os.path.getsize(fii_path) > 10:
        existing_fii = pd.read_csv(fii_path)
        existing_fii['date'] = pd.to_datetime(existing_fii['date'])

    # Logic: FIIs usually buy when Nifty is trending and global risk is on.
    nifty_ret = nifty['close'].pct_change()
    # Estimate FII Net: Volatility scaled returns
    fii_proxy = nifty_ret * 150000 
    fii_proxy = fii_proxy - (vix_z * 500)
    
    fii_bridge = pd.DataFrame({
        'date': nifty['date'],
        'fii_net': fii_proxy.fillna(0),
        'dii_net': (-fii_proxy * 0.8).fillna(0)
    })
    
    final_fii = fii_bridge.merge(existing_fii, on='date', how='left', suffixes=('_prox', '_real'))
    if 'fii_net_real' in final_fii.columns:
        final_fii['fii_net'] = final_fii['fii_net_real'].fillna(final_fii['fii_net_prox'])
        final_fii['dii_net'] = final_fii['dii_net_real'].fillna(final_fii['dii_net_prox'])
        final_fii['source'] = np.where(final_fii['fii_net_real'].isna(), 'synthetic', 'real')
    else:
        final_fii['fii_net'] = final_fii['fii_net_prox']
        final_fii['dii_net'] = final_fii['dii_net_prox']
        final_fii['source'] = 'synthetic'

    final_fii = final_fii[['date', 'fii_net', 'dii_net', 'source']].sort_values('date')
    final_fii.to_csv(fii_path, index=False)
    print(f"✅ FII/DII Bridged: {len(final_fii)} rows saved.")
    
    print("\n✨ Data Gap Closed! You can now retrain your models with 2015-2026 data.")

if __name__ == "__main__":
    bridge_history()
