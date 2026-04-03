"""
modules/pcr_reversal_engine.py — PCR Reversal Predictor Module
==============================================================
Detects mean-reversion signals when the Put-Call Ratio (PCR) hits extremes.
Identifies overbought/oversold crowed states for contrarian entries.
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

MODEL_DIR = os.path.join(ROOT_DIR, "data", "models", "pcr_reversal")
HORIZONS = [3, 5, 7]

def _load_model(horizon):
    path = os.path.join(MODEL_DIR, f"xgb_pcr_rev_{horizon}d.pkl")
    if os.path.exists(path):
        return joblib.load(path)
    return None

def render():
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(236, 72, 153, 0.05) 0%, rgba(244, 63, 94, 0.05) 100%); 
                padding: 25px; border-radius: 20px; border: 1px solid rgba(236, 72, 153, 0.2); margin-bottom: 30px;">
        <h2 style="margin:0; color: #f472b6; font-size: 1.8rem;">🔀 PCR Reversal Predictor</h2>
        <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 5px;">
            Contrarian Signal: Predicting market reversals from PCR extremes.
        </p>
    </div>
    """, unsafe_allow_html=True)

    df = build_features()
    if df is None or df.empty:
        st.error("Data error.")
        return

    row = df.iloc[-1]
    pcr = float(row.get("pcr", 1.0) or 1.0)
    pcr_z = float(row.get("pcr_z", 0) or 0)
    
    # ── PCR STATS ──
    s1, s2, s3 = st.columns(3)
    with s1:
        st.metric("Current PCR", f"{pcr:.2f}")
    with s2:
        st.metric("PCR Z-Score", f"{pcr_z:+.2f}")
    with s3:
        status = "BEARISH OVEREXTENDED" if pcr_z > 1.5 else "BULLISH OVEREXTENDED" if pcr_z < -1.5 else "NEUTRAL"
        st.metric("Market Sentiment", status)

    st.markdown("<br>", unsafe_allow_html=True)

    # Predictions
    probs = {}
    for h in HORIZONS:
        model = _load_model(h)
        if model:
            available = [f for f in FEATURE_COLS if f in row.index]
            if hasattr(model, 'feature_names_in_'):
                model_feats = list(model.feature_names_in_)
                X = pd.DataFrame(0.0, index=[0], columns=model_feats)
                for f in model_feats:
                    if f in row.index: X[f] = float(row.get(f, 0) or 0)
            else:
                X = pd.DataFrame([[float(row.get(f, 0) or 0) for f in available]], columns=available)
            probs[h] = model.predict_proba(X)[0][1]

    # ── REVERSAL GAUGE ──
    max_p = max(probs.values()) if probs else 0
    p_color = "#4ade80" if max_p > 0.6 else "#fbbf24" if max_p > 0.3 else "#94a3b8"
    
    st.markdown(f"""
    <div style="text-align: center; padding: 40px; background: rgba(255,255,255,0.03); border-radius: 20px; border: 1px solid rgba(255,255,255,0.05);">
        <div style="font-size: 0.9rem; color: #94a3b8; text-transform: uppercase;">Reversal Probability</div>
        <div style="font-size: 4rem; font-weight: 900; color: {p_color};">{max_p:.1%}</div>
        <div style="font-size: 1.1rem; color: {p_color}; font-weight: 700; margin-top: 5px;">
            {'⚠️ CRITICAL REVERSAL ZONE' if max_p > 0.6 else 'MODERATE CONTRARIAN EDGE' if max_p > 0.3 else 'NO CLEAR EDGE'}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Logic explanation
    with st.expander("Contrarian Logic"):
        st.write("""
        *   **High PCR (>1.5 Z-score)**: Put buying is disproportionately high. Everyone is already bearish. Market often bounces as "weak hands" get shaken out.
        *   **Low PCR (<-1.5 Z-score)**: Call buying is disproportionately high. Everyone is already bullish. Market often pulls back as the rally runs out of fuel.
        """)

    # Historical PCR Chart
    st.subheader("Historical PCR vs Reversals")
    hist_df = df[['date', 'pcr_z', 'close']].tail(250).copy()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist_df['date'], y=hist_df['pcr_z'], name="PCR Z-Score", line=dict(color="#f472b6", width=2)))
    fig.add_hline(y=1.5, line_dash="dot", line_color="#ef4444", annotation_text="Bearish Extreme")
    fig.add_hline(y=-1.5, line_dash="dot", line_color="#4ade80", annotation_text="Bullish Extreme")
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=300,
        margin=dict(l=0, r=0, t=10, b=0),
        yaxis=dict(title="Z-Score")
    )
    st.plotly_chart(fig, use_container_width=True)

    # Strategy Sync
    st.subheader("Actionable Signal")
    if pcr_z > 1.5 and max_p > 0.4:
        st.success("🎯 **BULLISH PIVOT**: PCR is extremely high and AI confirms reversal potential. Consider selling OTM PUTS or closing existing Call spreads.")
    elif pcr_z < -1.5 and max_p > 0.4:
        st.error("🎯 **BEARISH PIVOT**: PCR is extremely low and AI confirms reversal potential. Consider selling OTM CALLS or closing existing Put spreads.")
    else:
        st.info("ℹ️ **NEUTRAL ZONE**: PCR is within normal bounds. Stick to the primary trend-following modules.")

if __name__ == "__main__":
    render()
