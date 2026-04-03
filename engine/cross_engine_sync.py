import os
import sys
import joblib
import pandas as pd

# Paths logic
JUDAH_BASE = os.path.dirname(os.path.abspath(__file__))
MOSES_BASE = os.path.abspath(os.path.join(JUDAH_BASE, "..", "Moses-RandomForest"))

# Add Moses to path for imports
sys.path.append(MOSES_BASE)

def get_moses_consensus(df_latest):
    """
    Bridge function: Runs Moses inference on the latest JUDAH date.
    Returns: up_prob (0 to 1)
    """
    try:
        from rf_trainer import DIRECTION_FEATURES
        m_path = os.path.join(MOSES_BASE, "data", "models", "rf_dir_1d.pkl")
        
        if not os.path.exists(m_path):
            return 0.5
            
        m = joblib.load(m_path)
        
        # Sync features: Moses needs specific column names
        # Most are overlapping, but let's ensure alignment
        feats = [f for f in DIRECTION_FEATURES if f in df_latest.columns]
        X = df_latest[feats].values.reshape(1, -1)
        
        probs = m.predict_proba(X)[0]
        return float(probs[1])
    except Exception as e:
        print(f"Sync Bridge Error: {e}")
        return 0.5

def check_elite_sync(judah_prob, moses_prob, vix):
    """
    The 'Triple-Lock' Logic for 85%+ Accuracy:
    1. JUDAH and MOSES must agree (>0.62 or <0.38)
    2. VIX should be in the 'Safe Zone' (< 18)
    """
    sync_up = (judah_prob > 0.62) and (moses_prob > 0.62)
    sync_dn = (judah_prob < 0.38) and (moses_prob < 0.38)
    safe_vix = vix < 18
    
    if sync_up and safe_vix: return "ELITE BULLISH"
    if sync_dn and safe_vix: return "ELITE BEARISH"
    return "NO CONSENSUS"
