"""
modules/expiry_vol_engine.py — Expiry Week Volatility Module
============================================================
Forecasts if the current expiry week will be high or low volatility.
Helps in Gamma Risk management.
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import joblib
import plotly.graph_objects as go
from datetime import datetime

# Ensure project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from engine.core import build_features, FEATURE_COLS

MODEL_DIR = os.path.join(ROOT_DIR, "data", "models", "expiry_vol")
EVENTS_PATH = os.path.join(ROOT_DIR, "data", "events.csv")

def _load_model():
    path = os.path.join(MODEL_DIR, "xgb_expiry_vol.pkl")
    if os.path.exists(path):
        return joblib.load(path)
    return None

def render():
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.05) 0%, rgba(217, 119, 6, 0.05) 100%); 
                padding: 25px; border-radius: 20px; border: 1px solid rgba(245, 158, 11, 0.2); margin-bottom: 30px;">
        <h2 style="margin:0; color: #f59e0b; font-size: 1.8rem;">⌛ Expiry Week Risk Radar</h2>
        <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 5px;">
            Gamma Forecaster: Predicting if this expiry week will be calm or explosive.
        </p>
    </div>
    """, unsafe_allow_html=True)

    df = build_features()
    if df is None or df.empty:
        st.error("Data error.")
        return

    row = df.iloc[-1]
    
    # Check if expiry week
    events = pd.read_csv(EVENTS_PATH)
    events['date'] = pd.to_datetime(events['Date'])
    expiry_mask = (events['Type'] == 'Monthly_Expiry') | \
                  (events['label'] == 'Weekly Expiry') | \
                  (events['Event'] == 'Weekly Expiry')
    all_expiries = sorted(events[expiry_mask]['date'].tolist())
    
    today = pd.to_datetime(row['date'])
    def get_next_expiry(d):
        for e in all_expiries:
            if e >= d: return e
        return None
    
    next_exp = get_next_expiry(today)
    days_to = (next_exp - today).days if next_exp else 99
    is_exp_wk = 1 if days_to <= 4 else 0
    
    m_vol = _load_model()
    if not m_vol:
        st.warning("Model not found. Please train it first.")
        return

    # Prediction
    available = [f for f in FEATURE_COLS if f in row.index]
    if hasattr(m_vol, 'feature_names_in_'):
        model_feats = list(m_vol.feature_names_in_)
        X = pd.DataFrame(0.0, index=[0], columns=model_feats)
        for f in model_feats:
            if f in row.index: X[f] = float(row.get(f, 0) or 0)
        if 'is_expiry_week' in model_feats:
            X['is_expiry_week'] = is_exp_wk
    else:
        # Simple list for order-sensitive models if needed
        X = pd.DataFrame([[float(row.get(f, 0) or 0) for f in available] + [is_exp_wk]], 
                         columns=available + ['is_expiry_week'])
    
    prob_high = m_vol.predict_proba(X)[0][1]

    # ── CONTEXT ──
    ec1, ec2, ec3 = st.columns(3)
    with ec1:
        st.metric("Expiry Status", "EXPIRY WEEK" if is_exp_wk else "NORMAL WEEK")
    with ec2:
        st.metric("Next Expiry", next_exp.strftime('%Y-%m-%d') if next_exp else "N/A")
    with ec3:
        st.metric("Days to Expiry", f"{days_to}d")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── VOL GAUGE ──
    v_color = "#f87171" if prob_high > 0.6 else "#fbbf24" if prob_high > 0.4 else "#4ade80"
    v_label = "HIGH VOLATILITY EXPIRY" if prob_high > 0.6 else "CALM EXPIRY" if prob_high < 0.4 else "MODERATE VOLATILITY"
    
    st.markdown(f"""
    <div style="text-align: center; padding: 40px; background: rgba(255,255,255,0.03); border-radius: 20px; border: 1px solid rgba(255,255,255,0.05);">
        <div style="font-size: 0.9rem; color: #94a3b8; text-transform: uppercase;">Probability of High Volatility</div>
        <div style="font-size: 4rem; font-weight: 900; color: {v_color};">{prob_high:.1%}</div>
        <div style="font-size: 1.1rem; color: {v_color}; font-weight: 700; margin-top: 5px;">{v_label}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Strategy Sync
    if prob_high > 0.6:
        st.error("💣 **GAMMA RISK HIGH**: High probability of a large move this week. Avoid selling narrow Iron Condors. Buying straddles/strangles or using Debit Spreads is preferred.")
    elif prob_high < 0.35:
        st.success("💎 **THETA BLISS**: Low volatility predicted. Premium decay is likely to be the dominant driver. Ideal for Iron Condors or Butterfly spreads.")
    else:
        st.warning("ℹ️ **NEUTRAL EXPIRY**: Mixed signals. Use wider-than-usual buffers if selling premium.")

if __name__ == "__main__":
    render()
