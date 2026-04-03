import os
import sys
import pandas as pd
import numpy as np

# Add the project root to sys.path
sys.path.append(os.getcwd())

from JUDAH.engine.core import compute_oracle

def verify_binary_ensemble():
    print("🚀 Starting Binary Ensemble Verification...")
    
    horizons = [3, 5, 7, 14]
    all_passed = True
    
    for h in horizons:
        print(f"\n--- Testing Horizon: {h}d ---")
        try:
            result = compute_oracle(horizon=h)
            if result is None:
                print(f"❌ Failed to get result for {h}d")
                all_passed = False
                continue
                
            direction = result.get("direction")
            p_up = result.get("p_up", 0)
            p_dn = result.get("p_down", 0)
            p_fl = result.get("p_flat", 0)
            
            print(f"Verdict: {direction}")
            print(f"Probabilities: UP={p_up:.2%}, DOWN={p_dn:.2%}, FLAT={p_fl:.2%}")
            
            # Check 1: No FLAT verdict
            if direction == "FLAT":
                print("❌ ERROR: Verdict is FLAT!")
                all_passed = False
            else:
                print("✅ PASS: Verdict is binary (UP/DOWN)")
                
            # Check 2: p_flat is 0.0
            if p_fl != 0.0:
                print(f"❌ ERROR: p_flat is {p_fl}")
                all_passed = False
            else:
                print("✅ PASS: p_flat is 0.0")
                
            # Check 3: Probabilities sum to 1.0
            total_p = p_up + p_dn + p_fl
            if not np.isclose(total_p, 1.0):
                print(f"❌ ERROR: Probabilities sum to {total_p}")
                all_passed = False
            else:
                print("✅ PASS: Probabilities sum to 1.0")
                
            # Check 4: Individual engines are binary
            for engine in ["engine_emp", "engine_mc", "engine_bay", "engine_ml"]:
                e_data = result.get(engine)
                if e_data:
                    e_v = e_data.get("verdict")
                    e_f = e_data.get("p_flat", 0)
                    if e_v == "FLAT" or e_f != 0.0:
                        print(f"❌ ERROR: {engine} is not binary! Verdict={e_v}, p_flat={e_f}")
                        all_passed = False
                    else:
                        print(f"✅ PASS: {engine} is binary")
                        
        except Exception as e:
            print(f"💥 CRASH during test: {str(e)}")
            import traceback
            traceback.print_exc()
            all_passed = False
            
    if all_passed:
        print("\n✨ ALL TESTS PASSED! Ensemble is now strictly binary.")
    else:
        print("\n❗ SOME TESTS FAILED. Check the output above.")

if __name__ == "__main__":
    verify_binary_ensemble()
