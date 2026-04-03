import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from engine.core import compute_regime_score, classify_regime, FEATURE_COLS, load_model_safe

# ── PATHS ──────────────────────────────────────────────────────────────────
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_BASE = os.path.join(ROOT_DIR, "data", "models")

# ── HELPERS ────────────────────────────────────────────────────────────────
import time
# Global model cache to prevent reloading from disk every time
_MODEL_CACHE = {}

def _load_model(rel_path, max_age_days=14):
    if rel_path in _MODEL_CACHE:
        return _MODEL_CACHE[rel_path]
        
    path = os.path.join(MODEL_BASE, rel_path)
    if os.path.exists(path):
        try:
            model = load_model_safe(path, FEATURE_COLS, max_age_days=max_age_days)
            _MODEL_CACHE[rel_path] = model
            return model
        except Exception as e:
            print(f"❌ Failed to load {rel_path}: {e}")
            return None
    return None

def _predict_prob(model, row, features=None):
    if model is None: return 0.5
    if features is None: features = list(row.index)
    
    try:
        # Handle feature alignment
        if hasattr(model, 'feature_names_in_'):
            model_feats = list(model.feature_names_in_)
            X = pd.DataFrame(0.0, index=[0], columns=model_feats)
            for f in model_feats:
                if f in row.index:
                    X[f] = float(row.get(f, 0) or 0)
        else:
            available = [f for f in features if f in row.index]
            X = pd.DataFrame([[float(row.get(f, 0) or 0) for f in available]], columns=available)
            
        probs = model.predict_proba(X)[0]
        return float(probs[1]) # Prob(Class 1)
    except:
        return 0.5

def _predict_val(model, row, features=None):
    if model is None: return 0.0
    if features is None: features = list(row.index)
    
    try:
        if hasattr(model, 'feature_names_in_'):
            model_feats = list(model.feature_names_in_)
            X = pd.DataFrame(0.0, index=[0], columns=model_feats)
            for f in model_feats:
                if f in row.index:
                    X[f] = float(row.get(f, 0) or 0)
        else:
            available = [f for f in features if f in row.index]
            X = pd.DataFrame([[float(row.get(f, 0) or 0) for f in available]], columns=available)
            
        return float(model.predict(X)[0])
    except:
        return 0.0

def _round_strike(val, step=50):
    """Round to nearest strike step (50 for Nifty)."""
    return int(round(val / step) * step)

# ── CORE ENGINE ─────────────────────────────────────────────────────────────

def get_all_verdicts(row, df, horizon):
    """
    Collects predictions from all 14+ models for a specific row and horizon.
    """
    h = horizon
    verdicts = {}
    
    # 1. Signal Engine (Direction)
    m_dir = _load_model(f"xgb_direction_{h}d.pkl")
    p_up = _predict_prob(m_dir, row)
    verdicts['direction'] = {
        'name': 'Directional Alpha',
        'val': 'UP' if p_up > 0.55 else 'DOWN' if p_up < 0.45 else 'FLAT',
        'prob': p_up if p_up > 0.5 else 1-p_up,
        'impact': 'BULLISH' if p_up > 0.55 else 'BEARISH' if p_up < 0.45 else 'NEUTRAL',
        'raw_prob': p_up
    }
    
    # 2. Breach Radar
    m_br_put = _load_model(f"breach/xgb_breach_put_{h}d.pkl")
    m_br_call = _load_model(f"breach/xgb_breach_call_{h}d.pkl")
    p_safe_put = _predict_prob(m_br_put, row)
    p_safe_call = _predict_prob(m_br_call, row)
    
    # 3. Tail Risk (Nuclear Alarm)
    # Use closest available horizon if exact not found
    h_tail = 7 if h >= 7 else 5 if h >= 5 else 3
    m_tail = _load_model(f"tail_risk/xgb_tail_risk_{h_tail}d.pkl")
    p_tail = _predict_prob(m_tail, row)
    verdicts['tail_risk'] = {'name': 'Tail Risk', 'val': 'NUCLEAR' if p_tail > 0.40 else 'ELEVATED' if p_tail > 0.15 else 'NORMAL', 'prob': p_tail}
    
    # 4. VIX Direction
    h_vix = 7 if h >= 7 else 5 if h >= 5 else 3 if h >= 3 else 1
    m_vix = _load_model(f"vix_direction/xgb_vix_dir_{h_vix}d.pkl")
    p_vix_up = _predict_prob(m_vix, row)
    verdicts['vix_dir'] = {'name': 'VIX Trend', 'val': 'RISING' if p_vix_up > 0.55 else 'FALLING' if p_vix_up < 0.45 else 'FLAT', 'prob': p_vix_up}
    
    # 5. Range Width
    m_range_cls = _load_model(f"range_width/xgb_range_cls_{h}d.pkl")
    m_range_reg = _load_model(f"range_width/xgb_range_reg_{h}d.pkl")
    p_tight = _predict_prob(m_range_cls, row)
    pred_range = _predict_val(m_range_reg, row)
    verdicts['range_width'] = {
        'name': 'Range Forecast', 
        'val': 'TIGHT' if p_tight > 0.6 else 'WIDE', 
        'prob': p_tight,
        'pred_pct': pred_range
    }
    
    # 6. Volatility Crush
    m_crush = _load_model(f"vol_crush/xgb_vol_crush_{h}d.pkl")
    p_crush = _predict_prob(m_crush, row)
    verdicts['vol_crush'] = {'name': 'Vol Crush', 'val': 'CRUSH' if p_crush > 0.65 else 'EXPAND', 'prob': p_crush}
    
    # 7. Max Drawdown (Regressors — predict point-based excursion, not probability)
    h_dd = 7 if h >= 7 else 5 if h >= 5 else 3
    m_dd_down = _load_model(f"max_drawdown/xgb_dd_down_{h_dd}d.pkl")
    m_dd_up = _load_model(f"max_drawdown/xgb_dd_up_{h_dd}d.pkl")
    pred_dd_down = _predict_val(m_dd_down, row)  # Predicted worst drop in points
    pred_dd_up = _predict_val(m_dd_up, row)      # Predicted worst rally in points
    spot = float(row.get('close', 0))
    verdicts['drawdown_put'] = {'name': 'Max Put DD', 'pred_pts': pred_dd_down, 'prob': min(abs(pred_dd_down) / max(spot * 0.03, 1), 1.0)}
    verdicts['drawdown_call'] = {'name': 'Max Call DD', 'pred_pts': pred_dd_up, 'prob': min(abs(pred_dd_up) / max(spot * 0.03, 1), 1.0)}
    
    # 8. Theta Decay
    m_theta = _load_model("theta_decay/xgb_theta_decay.pkl")
    p_theta = _predict_prob(m_theta, row)
    verdicts['theta_decay'] = {'name': 'Theta Edge', 'val': 'EDGY' if p_theta > 0.6 else 'NORMAL', 'prob': p_theta}
    
    # 9. PCR Reversal
    h_pcr = 7 if h >= 7 else 5 if h >= 5 else 3
    m_pcr = _load_model(f"pcr_reversal/xgb_pcr_rev_{h_pcr}d.pkl")
    p_pcr_rev = _predict_prob(m_pcr, row)
    verdicts['pcr_reversal'] = {'name': 'PCR Reversal', 'val': 'REVERSING' if p_pcr_rev > 0.6 else 'STABLE', 'prob': p_pcr_rev}
    
    # 10. Gap Risk & 12. Global Contagion (Sharing models from gap_risk/global_contagion)
    m_gap_cls = _load_model("global_contagion/xgb_gap_classifier.pkl")
    m_gap_reg = _load_model("global_contagion/xgb_gap_regressor.pkl")
    p_gap = _predict_prob(m_gap_cls, row)
    pred_gap = _predict_val(m_gap_reg, row)
    verdicts['gap_risk'] = {'name': 'Gap Risk', 'val': 'SKEWED' if p_gap > 0.6 else 'NORMAL', 'prob': p_gap, 'pred': pred_gap}
    
    # 11. Monthly Breach (21d/30d) with fallback when dedicated breach model missing
    if h >= 21:
        m_m_put = _load_model(f"monthly_breach/xgb_monthly_breach_put_{h}d.pkl")
        m_m_call = _load_model(f"monthly_breach/xgb_monthly_breach_call_{h}d.pkl")
        p_m_put = _predict_prob(m_m_put, row)
        p_m_call = _predict_prob(m_m_call, row)
        verdicts['monthly_breach'] = {'put': p_m_put, 'call': p_m_call}

        # If dedicated breach model is absent (prob ~0.5), fall back to monthly model probabilities
        if (m_br_put is None or abs(p_safe_put - 0.5) < 1e-6) and m_m_put is not None:
            p_safe_put = p_m_put
        if (m_br_call is None or abs(p_safe_call - 0.5) < 1e-6) and m_m_call is not None:
            p_safe_call = p_m_call

    verdicts['breach_put'] = {'name': 'Put Safety', 'val': 'SAFE' if p_safe_put > 0.65 else 'RISKY', 'prob': p_safe_put}
    verdicts['breach_call'] = {'name': 'Call Safety', 'val': 'SAFE' if p_safe_call > 0.65 else 'RISKY', 'prob': p_safe_call}
    
    # 13. Macro Sentiment
    m_macro = _load_model("macro_sentiment/xgb_macro_sentiment.pkl")
    p_macro = _predict_prob(m_macro, row)
    verdicts['macro_sentiment'] = {'name': 'Macro Pulse', 'val': 'RISK-ON' if p_macro > 0.6 else 'RISK-OFF' if p_macro < 0.4 else 'NEUTRAL', 'prob': p_macro}
    
    # 14. Intraday Reversal
    m_rev = _load_model("intraday_reversal/xgb_intraday_rev.pkl")
    p_rev = _predict_prob(m_rev, row)
    verdicts['intraday_reversal'] = {'name': 'Reversal Edge', 'val': 'REVERSAL' if p_rev > 0.6 else 'TRENDING', 'prob': p_rev}
    
    # 15. Expiry Vol
    m_exp_vol = _load_model("expiry_vol/xgb_expiry_vol.pkl")
    p_exp_vol = _predict_prob(m_exp_vol, row)
    verdicts['expiry_vol'] = {'name': 'Expiry Vol', 'val': 'SPIKE' if p_exp_vol > 0.6 else 'CRUSH', 'prob': p_exp_vol}

    # 16. Regime Transition
    h_shift = 7 if h >= 7 else 5 if h >= 5 else 3
    m_shift = _load_model(f"regime_transition/xgb_regime_shift_{h_shift}d.pkl")
    p_shift = _predict_prob(m_shift, row)
    verdicts['regime_transition'] = {'name': 'Shift Risk', 'val': 'SHIFT' if p_shift > 0.55 else 'STABLE', 'prob': p_shift}

    return verdicts

def select_strikes(row, df, horizon=7):
    """
    Synthesizes all model verdicts into an actionable strike selection.
    """
    spot = float(row.get('close', 0))
    atr10 = float(row.get('atr10', 0))
    vix = float(row.get('vix', 15))
    
    # 1. Get all verdicts
    verdicts = get_all_verdicts(row, df, horizon)
    
    # 2. Regime Scoring
    score, comps = compute_regime_score(row)
    regime = classify_regime(score)
    
    # 3. Base Calculation
    # Time factor: proportional to sqrt of days
    time_factor = np.sqrt(horizon / 7)
    
    # Regime multiplier: Widen in risky regimes
    regime_mult = 1.0 if regime == 'GREEN' else 1.25 if regime == 'YELLOW' else 1.5
    
    # Initial base distance (2 ATRs normalized for 7 days)
    base_dist = atr10 * 2.0 * time_factor * regime_mult
    
    # Ensure minimum distance based on VIX
    vix_min_dist = spot * (vix/100) * np.sqrt(horizon/252) * 0.7 # 70% of 1SD move
    base_dist = max(base_dist, vix_min_dist)
    
    # 4. Adjustments & Justifications
    justifications = []
    
    # Direction Skew
    dir_v = verdicts['direction']
    p_up = dir_v['raw_prob']
    put_skew = 1.0
    call_skew = 1.0
    
    if p_up > 0.6:
        put_skew = 0.8  # Tighten Puts (BULLISH)
        call_skew = 1.2 # Widen Calls
        justifications.append(f"Directional Alpha is BULLISH ({p_up:.0%}); tightened Puts for premium and widened Calls for safety.")
    elif p_up < 0.4:
        put_skew = 1.2  # Widen Puts (BEARISH)
        call_skew = 0.8 # Tighten Calls
        justifications.append(f"Directional Alpha is BEARISH ({1-p_up:.0%}); widened Puts for safety and tightened Calls for premium.")
        
    # Tail Risk Guard
    p_tail = verdicts['tail_risk']['prob']
    if p_tail > 0.15:
        tail_mult = 1.0 + (p_tail * 0.5)
        put_skew *= tail_mult
        call_skew *= tail_mult
        justifications.append(f"Tail Risk Elevated ({p_tail:.0%}); widened both sides by {tail_mult:.0%} as insurance.")
        
    # Vol Crush Opportunity
    p_crush = verdicts['vol_crush']['prob']
    if p_crush > 0.7 and regime == 'GREEN':
        put_skew *= 0.9
        call_skew *= 0.9
        justifications.append(f"Vol Crush Likely ({p_crush:.0%}) & GREEN Regime; tightened both sides to capture fast decay.")
        
    # Range Width ML Override
    # If ML range regressor is high confidence, use it to bound
    ml_range_pct = verdicts['range_width']['pred_pct']
    ml_range_pts = spot * (ml_range_pct / 100)
    # If ML predicted range + 0.5% buffer is wider than base_dist, widen.
    ml_dist = ml_range_pts * 1.1 # 10% safety buffer over predicted high/low
    
    if ml_dist > base_dist:
        base_dist = (base_dist + ml_dist) / 2 # Blend it
        justifications.append(f"ML Range Forecast (±{ml_range_pct:.1f}%) suggests wider movement than ATR; adjusted base distance up.")

    # 5. Final Strike Calculation
    raw_put = spot - (base_dist * put_skew)
    raw_call = spot + (base_dist * call_skew)
    
    put_strike = _round_strike(raw_put)
    call_strike = _round_strike(raw_call)
    
    # 6. Hedge Selection (100 pts wider)
    put_hedge = _round_strike(put_strike - 100)
    call_hedge = _round_strike(call_strike + 100)
    
    # 7. Strategy Selection
    p_safe_put = verdicts['breach_put']['prob']
    p_safe_call = verdicts['breach_call']['prob']
    
    strategy = "NO TRADE"
    action = "STAY ON SIDELINES"
    color = "red"
    
    if regime == 'RED' or p_tail > 0.4:
        strategy = "NO TRADE"
        action = "NUCLEAR RISK"
        justifications.append("CRITICAL: Portfolio blocked due to RED regime or NUCLEAR tail risk.")
    elif p_safe_put > 0.65 and p_safe_call > 0.65:
        if p_up > 0.60:
            strategy = "BULL PUT SPREAD"
            action = "SELL PE"
            color = "green"
        elif p_up < 0.40:
            strategy = "BEAR CALL SPREAD"
            action = "SELL CE"
            color = "red"
        else:
            strategy = "IRON CONDOR"
            action = "SELL BOTH"
            color = "blue"
    elif p_safe_put > 0.65:
        strategy = "BULL PUT SPREAD"
        action = "SELL PE"
        color = "green"
    elif p_safe_call > 0.65:
        strategy = "BEAR CALL SPREAD"
        action = "SELL CE"
        color = "red"
    else:
        strategy = "WAITING"
        action = "UNSAFE LEVELS"
        justifications.append("Breach Radar suggests both strikes are currently unsafe.")

    # Position Sizing
    size = "ZERO"
    if strategy != "NO TRADE" and strategy != "WAITING":
        if regime == "GREEN" and max(p_safe_put, p_safe_call) > 0.8:
            size = "FULL"
        elif regime == "GREEN" or max(p_safe_put, p_safe_call) > 0.7:
            size = "HALF"
        else:
            size = "QUARTER"

    return {
        'put_strike': put_strike,
        'call_strike': call_strike,
        'put_hedge': put_hedge,
        'call_hedge': call_hedge,
        'strategy': strategy,
        'action': action,
        'color': color,
        'size': size,
        'horizon': horizon,
        'verdicts': verdicts,
        'justifications': justifications,
        'regime': regime,
        'score': score,
        'confidence': int(max(p_safe_put, p_safe_call)*100) if strategy != "NO TRADE" else 0
    }
