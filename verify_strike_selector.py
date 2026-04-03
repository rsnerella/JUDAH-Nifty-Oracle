import sys
import os
import pandas as pd

# Add project root to path
sys.path.insert(0, os.getcwd())

try:
    from engine.core import build_features
    from engine.strike_selector import select_strikes

    print("Loading features...")
    df = build_features()
    if df is not None and not df.empty:
        row = df.iloc[-1]
        print(f"Testing strike selection for 7d horizon on {row.get('date', 'Unknown Date')}...")
        result = select_strikes(row, df, horizon=7)
        
        print("\n--- STRIKE SELECTOR RESULTS (7d) ---")
        print(f"Strategy: {result.get('strategy', 'N/A')}")
        print(f"Action: {result.get('action', 'N/A')}")
        print(f"Put Strike: {result.get('put_strike', 0)}")
        print(f"Call Strike: {result.get('call_strike', 0)}")
        print(f"Confidence: {result.get('confidence', 0)}%")
        print(f"Regime: {result.get('regime', 'N/A')}")
        print("\nJustifications:")
        for j in result.get('justifications', []):
            print(f"- {j}")
            
        print("\nTesting 14d, 21d, 30d...")
        for h in [14, 21, 30]:
            try:
                res = select_strikes(row, df, horizon=h)
                print(f"{h}d: {res.get('strategy', 'N/A')} | {res.get('put_strike', 0)} - {res.get('call_strike', 0)}")
            except Exception as e:
                print(f"{h}d error: {e}")
    else:
        print("Error: Could not load features.")
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()
